from pydantic import BaseModel
from typing_extensions import Dict
from typing import Any

class CreateRecordArgs(BaseModel):
    tableId: str
    fields: Dict[str, Any]

class GetTableArgs(BaseModel):
    tableId: str

class UrlBuilderArgs(BaseModel):
    application_id: str
    id: str

class EmptyArgs(BaseModel):
    pass