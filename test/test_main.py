import pytest
import uuid
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_db

# ─── Test Database Setup ─────────────────────────────────────────────────────
# Use an in-memory SQLite database for tests
# StaticPool ensures the same connection is reused across threads
# so the data persists for the duration of each test
TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def override_get_db():
    with Session(engine) as session:
        yield session


# Override the real database with the test database
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Create all tables before each test and drop them after."""
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


client = TestClient(app)


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def newsgroups_payload():
    return {
        "model_name": "newsgroups-classifier",
        "model_description": "Classifies text into 5 newsgroup categories using TF-IDF and Logistic Regression",
        "model_version": "v1",
        "model_file_path": "models/newsgroups-classifier/v1/model.joblib",
        "model_metadata": {
            "framework": "scikit-learn",
            "model_type": "LogisticRegression",
            "vectorizer": "TfidfVectorizer",
            "categories": [
                "sci.space",
                "alt.atheism",
                "talk.religion.misc",
                "soc.religion.christian",
                "sci.med",
            ],
            "dataset": "20newsgroups",
            "preprocessing": ["remove_headers", "remove_footers", "remove_quotes"],
        },
        "created_by": "john@company.com",
        "training_accuracy": 0.941,
        "test_accuracy": 0.732,
        "hyperparameters": {
            "C": 10.0,
            "max_features": 50000,
            "ngram_range": [1, 1],
            "stop_words": "english",
            "max_iter": 1000,
        },
        "git_commit_hash": "a3f9c12",
        "stage": "staging",
        "is_active": False,
    }


@pytest.fixture
def image_classifier_payload():
    return {
        "model_name": "image-classifier",
        "model_description": "Classifies images into 1000 ImageNet categories using pretrained ResNet50",
        "model_version": "v1",
        "model_file_path": "models/image-classifier/v1/resnet50.pt",
        "model_metadata": {
            "framework": "pytorch",
            "model_type": "ResNet50",
            "weights": "ResNet50_Weights.DEFAULT",
            "dataset": "ImageNet",
            "num_classes": 1000,
            "input_size": [3, 224, 224],
            "preprocessing": {
                "resize": 256,
                "center_crop": 224,
                "normalize_mean": [0.485, 0.456, 0.406],
                "normalize_std": [0.229, 0.224, 0.225],
            },
            "supported_formats": ["image/jpeg", "image/png", "image/webp"],
        },
        "created_by": "john@company.com",
        "training_accuracy": 0.998,
        "test_accuracy": 0.804,
        "hyperparameters": {
            "pretrained": True,
            "frozen_layers": True,
            "optimizer": "none",
            "fine_tuned": False,
        },
        "git_commit_hash": "b7d2e45",
        "stage": "staging",
        "is_active": False,
    }


@pytest.fixture
def created_newsgroups_model(newsgroups_payload):
    """Creates a newsgroups model and returns the response data."""
    response = client.post("/models", json=newsgroups_payload)
    return response.json()


@pytest.fixture
def created_image_model(image_classifier_payload):
    """Creates an image classifier model and returns the response data."""
    response = client.post("/models", json=image_classifier_payload)
    return response.json()


# ─── POST /models ─────────────────────────────────────────────────────────────


class TestCreateModel:
    def test_returns_201(self, newsgroups_payload):
        response = client.post("/models", json=newsgroups_payload)
        assert response.status_code == 201

    def test_returns_model_id(self, newsgroups_payload):
        response = client.post("/models", json=newsgroups_payload)
        assert "model_id" in response.json()

    def test_model_id_is_valid_uuid(self, newsgroups_payload):
        response = client.post("/models", json=newsgroups_payload)
        model_id = response.json()["model_id"]
        assert uuid.UUID(model_id)

    def test_returns_model_name(self, newsgroups_payload):
        response = client.post("/models", json=newsgroups_payload)
        assert response.json()["model_name"] == "newsgroups-classifier"

    def test_returns_model_version(self, newsgroups_payload):
        response = client.post("/models", json=newsgroups_payload)
        assert response.json()["model_version"] == "v1"

    def test_returns_stage(self, newsgroups_payload):
        response = client.post("/models", json=newsgroups_payload)
        assert response.json()["stage"] == "staging"

    def test_returns_is_active(self, newsgroups_payload):
        response = client.post("/models", json=newsgroups_payload)
        assert not response.json()["is_active"]

    def test_returns_created_at(self, newsgroups_payload):
        response = client.post("/models", json=newsgroups_payload)
        assert "created_at" in response.json()

    def test_returns_created_by(self, newsgroups_payload):
        response = client.post("/models", json=newsgroups_payload)
        assert response.json()["created_by"] == "john@company.com"

    def test_created_at_is_valid_datetime(self, newsgroups_payload):
        from datetime import datetime

        response = client.post("/models", json=newsgroups_payload)
        created_at = response.json()["created_at"]
        assert datetime.fromisoformat(created_at)

    def test_image_classifier_returns_201(self, image_classifier_payload):
        response = client.post("/models", json=image_classifier_payload)
        assert response.status_code == 201

    def test_two_models_get_different_ids(
        self, newsgroups_payload, image_classifier_payload
    ):
        response1 = client.post("/models", json=newsgroups_payload)
        response2 = client.post("/models", json=image_classifier_payload)
        assert response1.json()["model_id"] != response2.json()["model_id"]

    def test_missing_model_name_returns_422(self, newsgroups_payload):
        newsgroups_payload.pop("model_name")
        response = client.post("/models", json=newsgroups_payload)
        assert response.status_code == 422

    def test_missing_created_by_returns_422(self, newsgroups_payload):
        newsgroups_payload.pop("created_by")
        response = client.post("/models", json=newsgroups_payload)
        assert response.status_code == 422

    def test_missing_git_commit_hash_returns_422(self, newsgroups_payload):
        newsgroups_payload.pop("git_commit_hash")
        response = client.post("/models", json=newsgroups_payload)
        assert response.status_code == 422

    def test_invalid_training_accuracy_returns_422(self, newsgroups_payload):
        newsgroups_payload["training_accuracy"] = "not_a_float"
        response = client.post("/models", json=newsgroups_payload)
        assert response.status_code == 422

    def test_empty_payload_returns_422(self):
        response = client.post("/models", json={})
        assert response.status_code == 422


# ─── GET /models ──────────────────────────────────────────────────────────────


class TestGetAllModels:
    def test_returns_200(self):
        response = client.get("/models")
        assert response.status_code == 200

    def test_response_has_result_field(self):
        response = client.get("/models")
        assert "result" in response.json()

    def test_response_has_models_field(self):
        response = client.get("/models")
        assert "models" in response.json()

    def test_returns_zero_result_when_no_models(self):
        response = client.get("/models")
        assert response.json()["result"] == 0

    def test_returns_empty_models_list_when_no_models(self):
        response = client.get("/models")
        assert response.json()["models"] == []

    def test_result_is_one_after_one_created(self, created_newsgroups_model):
        response = client.get("/models")
        assert response.json()["result"] == 1

    def test_models_list_has_one_item_after_one_created(self, created_newsgroups_model):
        response = client.get("/models")
        assert len(response.json()["models"]) == 1

    def test_result_is_two_after_two_created(
        self, created_newsgroups_model, created_image_model
    ):
        response = client.get("/models")
        assert response.json()["result"] == 2

    def test_models_list_has_two_items_after_two_created(
        self, created_newsgroups_model, created_image_model
    ):
        response = client.get("/models")
        assert len(response.json()["models"]) == 2

    def test_result_matches_models_list_length(
        self, created_newsgroups_model, created_image_model
    ):
        response = client.get("/models")
        data = response.json()
        assert data["result"] == len(data["models"])

    def test_returned_model_has_correct_name(self, created_newsgroups_model):
        response = client.get("/models")
        assert response.json()["models"][0]["model_name"] == "newsgroups-classifier"

    def test_models_list_is_a_list(self, created_newsgroups_model):
        response = client.get("/models")
        assert isinstance(response.json()["models"], list)

    def test_result_is_an_integer(self, created_newsgroups_model):
        response = client.get("/models")
        assert isinstance(response.json()["result"], int)


# ─── GET /models/{model_id} ───────────────────────────────────────────────────


class TestGetModelById:
    def test_returns_200_for_existing_model(self, created_newsgroups_model):
        model_id = created_newsgroups_model["model_id"]
        response = client.get(f"/models/{model_id}")
        assert response.status_code == 200

    def test_returns_correct_model_id(self, created_newsgroups_model):
        model_id = created_newsgroups_model["model_id"]
        response = client.get(f"/models/{model_id}")
        assert response.json()["model_id"] == model_id

    def test_returns_correct_model_name(self, created_newsgroups_model):
        model_id = created_newsgroups_model["model_id"]
        response = client.get(f"/models/{model_id}")
        assert response.json()["model_name"] == "newsgroups-classifier"

    def test_returns_404_for_nonexistent_model(self):
        fake_id = str(uuid.uuid4())
        response = client.get(f"/models/{fake_id}")
        assert response.status_code == 404

    def test_returns_correct_error_message_for_missing_model(self):
        fake_id = str(uuid.uuid4())
        response = client.get(f"/models/{fake_id}")
        assert "not found" in response.json()["detail"].lower()

    def test_returns_hyperparameters(self, created_newsgroups_model):
        model_id = created_newsgroups_model["model_id"]
        response = client.get(f"/models/{model_id}")
        assert "hyperparameters" in response.json()

    def test_returns_model_metadata(self, created_newsgroups_model):
        model_id = created_newsgroups_model["model_id"]
        response = client.get(f"/models/{model_id}")
        assert "model_metadata" in response.json()

    def test_returns_accuracies(self, created_newsgroups_model):
        model_id = created_newsgroups_model["model_id"]
        response = client.get(f"/models/{model_id}")
        data = response.json()
        assert "training_accuracy" in data
        assert "test_accuracy" in data


# ─── PATCH /models/{model_id}/stage ──────────────────────────────────────────


class TestUpdateModel:
    def test_returns_200_on_valid_update(self, created_newsgroups_model):
        model_id = created_newsgroups_model["model_id"]
        response = client.patch(f"/models/{model_id}", json={"stage": "production"})
        assert response.status_code == 200

    def test_stage_is_updated_correctly(self, created_newsgroups_model):
        model_id = created_newsgroups_model["model_id"]
        client.patch(f"/models/{model_id}", json={"stage": "production"})
        response = client.get(f"/models/{model_id}")
        assert response.json()["stage"] == "production"

    def test_can_update_is_active(self, created_newsgroups_model):
        model_id = created_newsgroups_model["model_id"]
        client.patch(f"/models/{model_id}", json={"is_active": True})
        response = client.get(f"/models/{model_id}")
        assert response.json()["is_active"]

    def test_can_update_model_description(self, created_newsgroups_model):
        model_id = created_newsgroups_model["model_id"]
        client.patch(
            f"/models/{model_id}", json={"model_description": "Updated description"}
        )
        response = client.get(f"/models/{model_id}")
        assert response.json()["model_description"] == "Updated description"

    def test_can_update_multiple_fields_at_once(self, created_newsgroups_model):
        model_id = created_newsgroups_model["model_id"]
        client.patch(
            f"/models/{model_id}", json={"stage": "production", "is_active": True}
        )
        response = client.get(f"/models/{model_id}")
        data = response.json()
        assert data["stage"] == "production"
        assert data["is_active"]

    def test_unrelated_fields_are_not_affected(self, created_newsgroups_model):
        model_id = created_newsgroups_model["model_id"]
        client.patch(f"/models/{model_id}", json={"stage": "production"})
        response = client.get(f"/models/{model_id}")
        assert response.json()["model_name"] == "newsgroups-classifier"

    def test_returns_404_for_nonexistent_model(self):
        fake_id = str(uuid.uuid4())
        response = client.patch(f"/models/{fake_id}", json={"stage": "production"})
        assert response.status_code == 404

    def test_model_id_cannot_be_changed(self, created_newsgroups_model):
        model_id = created_newsgroups_model["model_id"]
        new_id = str(uuid.uuid4())
        client.patch(f"/models/{model_id}", json={"model_id": new_id})
        get_response = client.get(f"/models/{model_id}")
        assert get_response.status_code == 200

    def test_created_at_cannot_be_changed(self, created_newsgroups_model):
        model_id = created_newsgroups_model["model_id"]
        original = created_newsgroups_model["created_at"]
        client.patch(f"/models/{model_id}", json={"created_at": "2000-01-01T00:00:00"})
        response = client.get(f"/models/{model_id}")
        assert response.json()["created_at"] == original

    def test_empty_patch_body_does_not_crash(self, created_newsgroups_model):
        model_id = created_newsgroups_model["model_id"]
        response = client.patch(f"/models/{model_id}", json={})
        assert response.status_code == 200

    def test_invalid_stage_value_returns_422(self, created_newsgroups_model):
        model_id = created_newsgroups_model["model_id"]
        response = client.patch(f"/models/{model_id}", json={"stage": "InvalidStage"})
        assert response.status_code == 422

    def test_invalid_field_type_returns_422(self, created_newsgroups_model):
        model_id = created_newsgroups_model["model_id"]
        response = client.patch(
            f"/models/{model_id}", json={"training_accuracy": "not_a_float"}
        )
        assert response.status_code == 422


# ─── Health Check ─────────────────────────────────────────────────────────────


class TestHealthCheck:
    def test_returns_200(self):
        response = client.get("/health")
        assert response.status_code == 200

    def test_returns_healthy_status(self):
        response = client.get("/health")
        assert response.json() == {"status": "healthy"}
