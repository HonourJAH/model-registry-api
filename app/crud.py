from .schemas import (
    ModelCreate,
    ModelRead,
    ModelUpdate,
    ModelCreateResponse,
    GetAllModelsResponse,
)
from sqlmodel import Session, select
from .model import Model
import uuid


def create_model(model: ModelCreate, db: Session) -> ModelCreateResponse:
    new_model = Model(**model.model_dump())
    db.add(new_model)
    db.commit()
    db.refresh(new_model)
    return ModelCreateResponse(**new_model.model_dump())


def get_model(model_id: str, db: Session) -> ModelRead:
    model_uuid = uuid.UUID(model_id)
    model = db.get(Model, model_uuid)
    if not model:
        return None
    return ModelRead(**model.model_dump())


def get_all_models(db: Session) -> GetAllModelsResponse:
    models = db.exec(select(Model)).all()
    if not models:
        return GetAllModelsResponse(result=0, models=[])
    return GetAllModelsResponse(result=len(models), models=models)


def update_model(model_id: str, model_update: ModelUpdate, db: Session) -> ModelRead:
    model_uuid = uuid.UUID(model_id)
    model = db.get(Model, model_uuid)
    if not model:
        return None

    update_data = model_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(model, key, value)

    db.add(model)
    db.commit()
    db.refresh(model)
    return ModelRead(**model.model_dump())


def delete_model(model_id: str, db: Session) -> None:
    model_uuid = uuid.UUID(model_id)
    model = db.get(Model, model_uuid)
    if not model:
        return False

    db.delete(model)
    db.commit()
    return True
