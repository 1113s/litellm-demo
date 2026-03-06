from fastapi import APIRouter, status

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def list_models() -> dict[str, list]:
    return {"items": []}
