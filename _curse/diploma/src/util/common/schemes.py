from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    message: str | dict | list

    class Config:
        from_attributes = True