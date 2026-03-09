from fastapi import APIRouter, status

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def list_models() -> dict[str, list[dict[str, str]]]:
    return {
        "items": [
            {"id": "glm-4.5", "name": "GLM-4.5", "provider": "glm"},
            {"id": "deepseek-chat", "name": "DeepSeek Chat", "provider": "deepseek"},
            {"id": "qwen-plus", "name": "Qwen Plus", "provider": "qwen"},
        ]
    }
