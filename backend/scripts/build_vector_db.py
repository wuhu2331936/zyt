"""构建 ChromaDB 向量库

读取 medicines.json → 用 BAAI/bge-small-zh Embedding → 持久化到 ChromaDB

运行：
    cd backend
    python scripts/build_vector_db.py

数据源建议（生产环境可替换为）：
- 国家药品监督管理局公开说明书：https://www.nmpa.gov.cn/
- 药智数据药品说明书：https://www.yaozh.com/
- 临床用药信息：https://www.drugs.com/
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# 把项目根目录加入 sys.path，让脚本可直接执行
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings  # noqa: E402

import chromadb  # noqa: E402
from chromadb.config import Settings as ChromaSettings  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402


def load_medicines() -> list[dict]:
    """读取示例药品数据"""
    data_path = Path(__file__).parent / "data" / "medicines.json"
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build():
    """主流程：加载 → Embedding → 写入 ChromaDB"""
    print("=" * 60)
    print("📚 智药通 ChromaDB 向量库构建脚本")
    print("=" * 60)

    # 1. 准备客户端
    print(f"\n[1/4] 初始化 ChromaDB (persist: {settings.chroma_persist_dir})")
    client = chromadb.PersistentClient(
        path=settings.chroma_persist_dir,
        settings=ChromaSettings(anonymized_telemetry=False, allow_reset=True),
    )

    # 2. 加载 Embedding 模型（首次会下载 ~180MB）
    print(f"\n[2/4] 加载 Embedding 模型: {settings.embedding_model}")
    print("（首次运行需联网下载，耗时约 1-3 分钟）")
    model = SentenceTransformer(settings.embedding_model)

    # 3. 读取药品数据
    print(f"\n[3/4] 读取药品说明书数据")
    medicines = load_medicines()
    print(f"  共 {len(medicines)} 条药品")

    # 4. 创建/重建 collection
    collection_name = "medicines"
    # 如果已存在则删除重建
    if collection_name in [c.name for c in client.list_collections()]:
        print(f"  已存在 collection '{collection_name}'，删除重建")
        client.delete_collection(collection_name)
    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "老年常用药说明书 + 相互作用"},
    )

    # 5. Embedding + 写入
    print(f"\n[4/4] Embedding 并写入 ChromaDB...")
    for i, med in enumerate(medicines, 1):
        # 拼成可被语义检索的文本
        doc_text = med["text"]
        emb = model.encode(doc_text).tolist()
        collection.add(
            ids=[med["id"]],
            embeddings=[emb],
            documents=[doc_text],
            metadatas=[{
                "name": med["name"],
                "category": med.get("category", ""),
                "spec": med.get("spec", ""),
            }],
        )
        print(f"  [{i}/{len(medicines)}] {med['name']}")

    # 6. 验证检索
    print("\n" + "=" * 60)
    print("✅ 构建完成！测试检索效果：")
    test_queries = [
        "阿司匹林和华法林能一起吃吗",
        "高血压的人可以吃什么药",
        "糖尿病的用药",
        "老年人退烧用什么药",
    ]
    for q in test_queries:
        q_emb = model.encode(q).tolist()
        results = collection.query(query_embeddings=[q_emb], n_results=2)
        print(f"\n  ❓ Query: {q}")
        for i, (doc, meta, dist) in enumerate(
            zip(results["documents"][0], results["metadatas"][0], results["distances"][0]), 1
        ):
            print(f"    Top{i} {meta['name']} (dist={dist:.3f})")
            print(f"      {doc[:80]}...")

    print("\n" + "=" * 60)
    print(f"📁 向量库已持久化到: {settings.chroma_persist_dir}")
    print("=" * 60)


if __name__ == "__main__":
    build()