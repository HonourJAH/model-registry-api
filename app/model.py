import uuid
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON, Enum as SQLEnum
from enum import Enum


class ModelStage(str, Enum):
    staging = "staging"
    production = "production"
    archived = "archived"


class Model(SQLModel, table=True):
    model_id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    model_name: str
    model_description: str
    model_version: str
    model_file_path: str
    model_metadata: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str
    training_accuracy: float
    test_accuracy: float
    hyperparameters: dict = Field(default_factory=dict, sa_column=Column(JSON))
    git_commit_hash: str
    stage: ModelStage = Field(
        default=ModelStage.staging, sa_column=Column(SQLEnum(ModelStage))
    )
    is_active: bool = False
