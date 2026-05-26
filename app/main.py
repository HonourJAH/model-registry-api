from fastapi import FastAPI, status
from fastapi.params import Depends
from sqlmodel import Session
from app.schemas import (
    GetAllModelsResponse,
    ModelCreate,
    ModelCreateResponse,
    ModelRead,
    ModelUpdate,
)
from app.database import get_db
from typing import Annotated
from fastapi import HTTPException
from app import crud

session = Annotated[Session, Depends(get_db)]

app = FastAPI()


@app.post("/models", status_code=status.HTTP_201_CREATED)
async def create_model(model: ModelCreate, db: session) -> ModelCreateResponse:
    return crud.create_model(model, db)


@app.get("/models")
async def get_all_models(db: session) -> GetAllModelsResponse:
    models = crud.get_all_models(db)
    return models


@app.get("/models/{model_id}")
async def get_model(model_id: str, db: session) -> ModelRead:
    model = crud.get_model(model_id, db)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Model not found"
        )
    return model


@app.patch("/models/{model_id}")
async def update_model(
    model_id: str, model_update: ModelUpdate, db: session
) -> ModelRead:
    model = crud.update_model(model_id, model_update, db)
    if not model:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Model not found"
        )
    return model


@app.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(model_id: str, db: session) -> None:
    result = crud.delete_model(model_id, db)
    if result is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Model not found"
        )
    return None


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
