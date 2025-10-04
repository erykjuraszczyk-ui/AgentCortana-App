from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/v1", tags=["demo"])


class EchoIn(BaseModel):
    message: str


@router.post("/echo")
def echo(body: EchoIn):
    return {"echo": body.message}
