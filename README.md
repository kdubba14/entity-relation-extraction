# 👀 Scouta

## 📌 Project Overview

This is a **FastAPI** project designed to handle the AI tasks for **Scouta**. The project uses **Poetry** for dependency management and is deployable on **Railway**.

## 🚀 Setup & Run Locally

### 1️⃣ Install Dependencies

- Install Python using `pyenv`
- Install dependencies using `poetry`

```sh
pyenv install 3.9.21
pyenv local 3.9.21
poetry install
```

### 2️⃣ Run Locally

```sh
poetry run uvicorn app.main:app --reload
```

Visit: `http://127.0.0.1:8000`

### 3️⃣ Run with Docker

```sh
docker build -t fastapi-boilerplate .
docker run -p 8000:8000 fastapi-boilerplate
```

## 🚀 Deploy on Railway

### 1️⃣ Install Railway CLI

```sh
npm i -g @railway/cli
railway login
```

### 2️⃣ Deploy

```sh
railway init
railway up
```

## 📘 API Routes

- `GET /` - Check if API is running
- `GET /health` - Health check
