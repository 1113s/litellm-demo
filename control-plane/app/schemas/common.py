from pydantic import BaseModel


class ApiEnvelope(BaseModel):
    data: dict | list
