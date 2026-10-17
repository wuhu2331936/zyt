"""RAG 服务（阶段 4 升级：ChromaDB 检索 + LLM 总结）

阶段 2：直接调 DeepSeek 分析（基于其内置医学知识）
阶段 4：用 ChromaDB 检索药品说明书 → 把相关段落塞进 Prompt → DeepSeek 总结

启动时延迟加载向量库（避免每次请求都加载）。
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

# RAG 依赖是可选的：未安装时应用仍可启动（仅向量检索功能降级）。
# 这也保证 CI 环境（只装 core+ai 依赖）能通过导入冒烟测试。
try:  # pragma: no cover - import guard
    import chromadb
    from chromadb.config import Settings as ChromaSettings
    from sentence_transformers import SentenceTransformer

    RAG_DEPENDENCIES_AVAILABLE = True
except ImportError:  # chromadb / sentence-transformers 未安装
    chromadb = None
    ChromaSettings = None
    SentenceTransformer = None
    RAG_DEPENDENCIES_AVAILABLE = False

from app.core.config import settings
from app.services import deepseek

# ChromaDB 集合名称（与 build_vector_db.py 保持一致）
COLLECTION_NAME = "medicines"


@lru_cache(maxsize=1)
def _get_vectorstore():
    """单例加载向量库和 embedding 模型"""
    if not RAG_DEPENDENCIES_AVAILABLE:
        raise RuntimeError(
            "RAG 依赖未安装 (chromadb / sentence-transformers)。\n"
            "完整安装: cd backend && pip install -r requirements-rag.txt\n"
            "未安装时应用可启动，但药品说明书向量检索不可用。"
        )
    if not os.path.exists(settings.chroma_persist_dir):
        raise FileNotFoundError(
            f"向量库不存在: {settings.chroma_persist_dir}\n"
            f"请先运行: cd backend && python scripts/build_vector_db.py"
        )
    client = chromadb.PersistentClient(
        path=settings.chroma_persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False),
    )
    if COLLECTION_NAME not in [c.name for c in client.list_collections()]:
        raise FileNotFoundError(
            f"ChromaDB 中找不到 collection '{COLLECTION_NAME}'\n"
            f"请先运行: cd backend && python scripts/build_vector_db.py"
        )
    collection = client.get_collection(COLLECTION_NAME)
    embedder = SentenceTransformer(settings.embedding_model)
    return collection, embedder


def _search_relevant_docs(query: str, n_results: int = 4) -> list[dict]:
    """向量检索：返回药品名 + 说明书段落"""
    collection, embedder = _get_vectorstore()
    q_emb = embedder.encode(query).tolist()
    results = collection.query(
        query_embeddings=[q_emb],
        n_results=n_results,
    )
    docs = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        docs.append({"name": meta["name"], "text": doc})
    return docs


async def check_interactions(medicines: list[str]) -> dict:
    """检查药物相互作用（阶段 4 升级版）

    1. 拼接"药名 + 相互影响"作为 query
    2. ChromaDB 检索 Top-4 相关药品段落
    3. 把段落 + 药品清单塞进 Prompt
    4. DeepSeek 总结风险
    """
    if len(medicines) < 2:
        return {
            "has_risk": False,
            "risks": [],
            "summary": "只用了一种药，暂时无法评估相互作用。",
        }

    # 1. 检索相关药品段落
    # 注意：向量库不可用的原因有很多（依赖未安装 RuntimeError / 库未构建
    # FileNotFoundError / 模型下载失败 等），任何一种都必须回落到 LLM 内置知识，
    # 绝不能把异常抛给上层导致接口 500 —— 云端通常不安装 RAG 依赖。
    if not getattr(settings, "rag_enabled", True):
        return await deepseek.analyze_interactions(medicines)

    try:
        query = f"{'、'.join(medicines)} 之间是否存在药物相互作用"
        relevant_docs = _search_relevant_docs(query, n_results=4)
    except Exception as e:
        print(f"[rag] 向量检索不可用({type(e).__name__}: {e})，改用 LLM 内置知识分析")
        return await deepseek.analyze_interactions(medicines)

    # 2. 构造增强 Prompt
    context = "\n\n".join(
        f"### {d['name']}\n{d['text']}" for d in relevant_docs
    )

    prompt = f"""以下是数据库中与「{'、'.join(medicines)}」相关的药品说明书摘要：

{context}

---

请基于以上摘要分析用户当前用药清单（{', '.join(medicines)}）是否存在相互作用风险。
若数据库中无直接证据，请诚实告知并基于药理学常识给出推测。

**严格 JSON 格式** 返回（不要任何多余文字、不要 markdown 代码块）：

{{
  "has_risk": true/false,
  "risks": [
    {{
      "pair": ["药品A", "药品B"],
      "level": "critical|major|moderate|minor",
      "level_cn": "严禁/较严重/中等/轻微",
      "description": "作用机制简述",
      "suggestion": "建议措施"
    }}
  ],
  "summary": "整体概述，1-2 句话"
}}"""

    # 3. DeepSeek 总结
    return await deepseek._complete_json(
        system=(
            "你是资深临床药师，擅长分析药物相互作用。"
            "请严格根据提供的药品说明书摘要回答，不支持用其他数据。"
            "回答时先引用说明书中的具体证据再下结论。"
        ),
        user=prompt,
    )


async def search_medicine_info(query: str) -> list[dict]:
    """通用药品信息检索（供语音问答等场景使用）"""
    try:
        return _search_relevant_docs(query, n_results=3)
    except FileNotFoundError:
        return []