from src.models.enums import ResponseStatus, ResponseDataType
from pydantic import BaseModel
from typing import Any

class CommonResponseModel(BaseModel):
    status: ResponseStatus
    data_type: ResponseDataType
    data: Any
