# IMAGO Media API

## Clone Repository
```
git clone https://github.com/quincykwende/imago-media-api
```
```
cd imago-media-api/
```

## Run via Docker
```bash
docker-compose up --build
```

## Run with Uvicorn:

### 1. Create virtual env

```bash
cd imago-media-api/
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your credentials
# ES_HOST="https://XXXXX"
# ES_USER="USERNAME"
# ES_PASS="PASSWORD"
# ES_INDEX="INDEX"
# IMAGE_BASE_URL=https://www.imago-images.de
```

### 4. Quick run
```bash
fastapi dev app/main.py --port=8000
```

-- OR --

```bash
uvicorn app.main:app --reload --port=8000
```


The API will be available at http://localhost:8000

