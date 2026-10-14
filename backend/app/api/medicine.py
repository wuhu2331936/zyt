"""药品识别 / 详情路由"""
from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.medicine import RecognizeResponse
from app.services import qwen_vl

router = APIRouter()

# 限制上传 5MB
MAX_UPLOAD_BYTES = 5 * 1024 * 1024


@router.post("/recognize", response_model=RecognizeResponse, summary="拍照识药")
async def recognize_medicine(
    file: UploadFile = File(..., description="药盒照片，jpg/png/webp"),
):
    """接收药盒图片 → 调用通义千问 VL → 返回结构化药品信息

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

    return RecognizeResponse(success=True, medicine=medicine)