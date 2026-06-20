# Model Registry API

A production-ready REST API for registering, tracking, and managing machine learning models throughout their lifecycle. Built with FastAPI, SQLModel, and SQLite.

---

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Getting Started](#getting-started)
- [Environment Variables](#environment-variables)
- [Database Migrations](#database-migrations)
- [API Endpoints](#api-endpoints)
- [Request & Response Schemas](#request--response-schemas)
- [Running Tests](#running-tests)
- [Docker](#docker)
- [Example Payloads](#example-payloads)

---

## Overview

The Model Registry API provides a centralized store for tracking machine learning models across teams and projects. It records model metadata, performance metrics, hyperparameters, lifecycle stage, and deployment status — giving you a full audit trail of every model from training to production.

**Key features:**

- Register new models with full metadata and performance metrics
- Track model lifecycle stages — Staging, Production, Archived
- Update model fields individually without affecting unrelated data
- Retrieve all models or query a specific model by ID
- Delete models that are no longer needed
- Health check endpoint for container orchestration and load balancers

---

## Project Structure

```
model-registry-api/
├── app/
│   ├── __init__.py
│   ├── main.py          — FastAPI app and route handlers
│   ├── crud.py          — Database operations (create, read, update, delete)
│   ├── database.py      — SQLite engine, session factory, and get_db dependency
│   ├── model.py         — SQLModel table definition
│   └── schemas.py       — Request and response schemas
├── migrations/          — Alembic migration scripts
├── test/
│   ├── __init__.py
│   └── test_main.py     — Full test suite
├── .gitignore
├── alembic.ini
├── registry.db          — SQLite database file (auto-created on first run)
├── requirements.txt
└── README.md
```

---

## Requirements

- Python 3.12+
- pip

---

## Getting Started

**1. Clone the repository**

```bash
git clone git@github.com:HonourJAH/model-registry-api.git
cd model-registry-api
```

**2. Create and activate a virtual environment**

```bash
python3 -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run database migrations**

```bash
alembic upgrade head
```

**5. Start the server**

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.
Interactive docs at `http://localhost:8000/docs`.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./registry.db` | Database connection string |

Create a `.env` file in the project root to override defaults:

```
DATABASE_URL=sqlite:///./registry.db
```

---

## Database Migrations

This project uses Alembic for database migrations.

**Apply all pending migrations:**

```bash
alembic upgrade head
```

**Create a new migration after changing a model:**

```bash
alembic revision --autogenerate -m "describe your change"
```

**Roll back the last migration:**

```bash
alembic downgrade -1
```

---

## API Endpoints

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `POST` | `/models` | Register a new model | `201 Created` |
| `GET` | `/models` | Retrieve all registered models | `200 OK` |
| `GET` | `/models/{model_id}` | Retrieve a specific model by ID | `200 OK` |
| `PATCH` | `/models/{model_id}` | Update one or more fields of a model | `200 OK` |
| `DELETE` | `/models/{model_id}` | Delete a model | `204 No Content` |
| `GET` | `/health` | Health check | `200 OK` |

---

## Request & Response Schemas

### `POST /models` — Register a Model

**Request body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `model_name` | `string` | ✅ | Human-readable name of the model |
| `model_description` | `string` | ✅ | What the model does |
| `model_version` | `string` | ✅ | Version identifier e.g. `v1` |
| `model_file_path` | `string` | ✅ | Path or URL to the saved model file |
| `model_metadata` | `object` | ✅ | Framework, dataset, and architecture details |
| `created_by` | `string` | ✅ | Email or name of who trained the model |
| `training_accuracy` | `float` | ✅ | Accuracy score on training data |
| `test_accuracy` | `float` | ✅ | Accuracy score on test data |
| `hyperparameters` | `object` | ✅ | Key-value pairs of training hyperparameters |
| `git_commit_hash` | `string` | ✅ | Git commit that produced this model |
| `stage` | `string` | ✅ | Initial lifecycle stage |
| `is_active` | `bool` | ❌ | Whether model is serving traffic. Defaults to `false` |

**Response body:**

| Field | Type | Description |
|---|---|---|
| `model_id` | `uuid` | Auto-generated unique identifier |
| `model_name` | `string` | Confirmed model name |
| `model_version` | `string` | Confirmed version |
| `stage` | `string` | Confirmed stage |
| `is_active` | `bool` | Confirmed active status |
| `created_at` | `datetime` | Auto-generated UTC timestamp |
| `created_by` | `string` | Confirmed creator |

---

### `GET /models` — Get All Models

**Response body:**

```json
{
  "result": 2,
  "models": [ ... ]
}
```

| Field | Type | Description |
|---|---|---|
| `result` | `int` | Total number of models returned |
| `models` | `array` | List of full model objects |

---

### `PATCH /models/{model_id}` — Update a Model

All fields are optional. Only the fields you include will be updated.

```json
{
  "stage": "production",
  "is_active": true
}
```

Returns the full updated model object.

---

### `GET /health` — Health Check

```json
{
  "status": "healthy"
}
```

---

## Running Tests

```bash
pytest test/ -v
```

The test suite uses an in-memory SQLite database — no setup required. The production database is never touched during testing.

**Run with coverage:**

```bash
pytest test/ -v --cov=app --cov-report=term-missing
```

---

## Docker

**Build the image:**

```bash
docker build -t model-registry-api .
```

**Run the container:**

```bash
docker run -d -p 8000:8000 --name model-registry-api model-registry-api
```

---

## Example Payloads

### Register a scikit-learn text classifier

```json
{
  "model_name": "newsgroups-classifier",
  "model_description": "Classifies text into 5 newsgroup categories using TF-IDF and Logistic Regression",
  "model_version": "v1",
  "model_file_path": "models/newsgroups-classifier/v1/model.joblib",
  "model_metadata": {
    "framework": "scikit-learn",
    "model_type": "LogisticRegression",
    "vectorizer": "TfidfVectorizer",
    "categories": ["sci.space", "alt.atheism", "talk.religion.misc", "soc.religion.christian", "sci.med"],
    "dataset": "20newsgroups",
    "preprocessing": ["remove_headers", "remove_footers", "remove_quotes"]
  },
  "created_by": "john@company.com",
  "training_accuracy": 0.941,
  "test_accuracy": 0.732,
  "hyperparameters": {
    "C": 10.0,
    "max_features": 50000,
    "ngram_range": [1, 1],
    "stop_words": "english",
    "max_iter": 1000
  },
  "git_commit_hash": "a3f9c12",
  "stage": "staging",
  "is_active": false
}
```

### Register a PyTorch image classifier

```json
{
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
      "normalize_std": [0.229, 0.224, 0.225]
    },
    "supported_formats": ["image/jpeg", "image/png", "image/webp"]
  },
  "created_by": "john@company.com",
  "training_accuracy": 0.998,
  "test_accuracy": 0.804,
  "hyperparameters": {
    "pretrained": true,
    "frozen_layers": true,
    "optimizer": "none",
    "fine_tuned": false
  },
  "git_commit_hash": "b7d2e45",
  "stage": "staging",
  "is_active": false
}
```
