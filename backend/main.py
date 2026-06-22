"""
TextDiff 后端服务 - FastAPI 应用入口

提供 RESTful API 接口：
- GET  /api/health    - 健康检查
- POST /api/compare   - 文本差异比较
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional

from diff_engine import compare_texts

app = FastAPI(
    title="TextDiff API",
    description="文本比较工具后端服务 - 支持 JSON/YAML 格式差异比较",
    version="1.0.0",
)

# CORS 配置 - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class CompareRequest(BaseModel):
    """比较请求模型"""
    left_text: str = Field(..., description="左文本内容")
    right_text: str = Field(..., description="右文本内容")
    format: str = Field(..., description="格式类型: json 或 yaml")

    class Config:
        json_schema_extra = {
            "example": {
                "left_text": '{"name": "Alice", "age": 30}',
                "right_text": '{"Name": "Bob", "Age": 25}',
                "format": "json"
            }
        }


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "ok"
    service: str = "textdiff"
    version: str = "1.0.0"


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """健康检查接口"""
    return HealthResponse()


@app.post("/api/compare")
async def compare(request: CompareRequest):
    """文本差异比较接口

    接收左右两段文本和格式类型，返回差异比较结果。
    支持 JSON 和 YAML 两种格式。
    比较时忽略字段大小写和同层字段顺序。
    """
    # 验证格式
    valid_formats = ["json", "yaml"]
    if request.format not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的格式: {request.format}，支持的格式: {', '.join(valid_formats)}"
        )

    # 验证输入不为空
    if not request.left_text.strip():
        raise HTTPException(
            status_code=400,
            detail="左文本不能为空"
        )
    if not request.right_text.strip():
        raise HTTPException(
            status_code=400,
            detail="右文本不能为空"
        )

    # 执行比较
    result = compare_texts(request.left_text, request.right_text, request.format)

    if not result.get("success"):
        error = result.get("error", "未知错误")
        side = result.get("error_side", "")
        raise HTTPException(
            status_code=400,
            detail=f"{'左侧' if side == 'left' else '右侧'}文本{error}"
        )

    # 移除内部字段，返回干净结果
    return {
        "success": True,
        "has_diff": result["has_diff"],
        "format": result["format"],
        "left_normalized": result["left_normalized"],
        "right_normalized": result["right_normalized"],
        "left_original_lines": result["left_original_lines"],
        "right_original_lines": result["right_original_lines"],
        "left_annotations": result["left_annotations"],
        "right_annotations": result["right_annotations"],
        "diff_entries": result["diff_entries"],
        "summary": result["summary"],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
