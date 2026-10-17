"""药品识别 / 详情路由"""
from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.medicine import EnrichRequest, MedicineInfo, RecognizeResponse
from app.services import medicine_knowledge, qwen_vl

router = APIRouter()

# 限制上传 5MB
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


@router.post("/recognize", response_model=RecognizeResponse, summary="拍照识药")
async def recognize_medicine(
    file: UploadFile = File(..., description="药盒照片，jpg/png/webp"),
):
    """接收药盒图片 → 通义千问 VL 读药盒 → DeepSeek 补全说明书级解读

    两阶段：
    1. qwen_vl：看图识字，拿到真实药名/规格/厂家（药盒上有什么读什么，不臆测）
    2. medicine_knowledge：按药名补适应症、不良反应、禁忌、老年人注意、相互作用、
       漏服处理、储存与大白话总结，让结果接近一份用药说明书

    前端调用：在「拍照识药页」上传/拍摄后调用此接口。
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail=f"不支持的文件类型: {file.content_type}")

    image_bytes = await file.read()
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="图片过大（>5MB），请压缩后再试")

    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="图片为空")

    try:
        medicine = await qwen_vl.recognize_medicine(
            image_bytes=image_bytes,
            content_type=file.content_type,
        )
    except ValueError as e:
        # 配置错误
        raise HTTPException(status_code=500, detail=str(e))
    except RuntimeError as e:
        # VL 调用失败
        raise HTTPException(status_code=502, detail=f"VL 调用失败: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {e}")

    if medicine is None:
        return RecognizeResponse(
            success=False,
            error="未能识别出药品信息，请上传更清晰的药盒正面照",
        )

    # 第二阶段：按药名补全说明书级解读（失败也不影响识药结果）
    try:
        medicine = await medicine_knowledge.enrich_medicine(medicine)
    except Exception as e:
        print(f"[api/medicine] 知识补全异常({e})，返回药盒识别结果")

    return RecognizeResponse(success=True, medicine=medicine)


@router.post("/enrich", response_model=MedicineInfo, summary="按药名补全详细用药说明")
async def enrich_medicine_info(req: EnrichRequest):
    """给已有药品（尤其是手动添加的）补一份说明书级解读

    前端：药品详情页在缺少详细说明时点「生成详细用药说明」调用。
    """
    med = MedicineInfo(
        name=req.name,
        spec=req.spec,
        manufacturer=req.manufacturer,
        source=req.source,
    )
    try:
        med = await medicine_knowledge.enrich_medicine(med)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成用药说明失败: {e}")

    if not med.summary and not med.indications:
        raise HTTPException(status_code=502, detail="未能生成该药品的说明，请检查药品名是否准确")

    return med