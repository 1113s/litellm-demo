from fastapi import APIRouter, status

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
def list_keys() -> dict[str, list]:
    return {"items": []}
