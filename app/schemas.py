from sqlmodel import SQLModel, Field
import uuid
from datetime import datetime
from app.model import ModelStage


class ModelCreate(SQLModel):
    model_name: str
    model_description: str
    model_version: str
    model_file_path: str
    model_metadata: dict = Field(default={})
    created_by: str
    training_accuracy: float
    test_accuracy: float
    hyperparameters: dict = Field(default={})
    git_commit_hash: str
    is_active: bool = False
    stage: ModelStage


class ModelRead(ModelCreate):
    model_id: uuid.UUID
    created_at: datetime
    is_active: bool
    model_config = {"from_attributes": True}


class ModelUpdate(SQLModel):
    stage: ModelStage | None = None
    is_active: bool | None = None
    model_description: str | None = None
    model_config = {"extra": "forbid"}


class ModelCreateResponse(SQLModel):
    model_id: uuid.UUID
    model_name: str
    model_version: str
    stage: ModelStage
    is_active: bool
    created_at: datetime
    created_by: str


class GetAllModelsResponse(SQLModel):
    result: int
    models: list[ModelRead]
