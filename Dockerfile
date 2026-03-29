# ── Stage 1: builder ──────────────────────────────────────────────────────────
FROM python:3.11.9-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Install system dependencies required for building psycopg2 and other C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install production dependencies into a virtual environment
RUN uv sync --frozen --no-dev --no-install-project

# Pre-download the sentence-transformer model
RUN .venv/bin/python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2', cache_folder='/app/.cache')"

# ── Stage 2: runtime ──────────────────────────────────────────────────────────
FROM python:3.11.9-slim AS runtime

# Install system dependencies required by psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 1. สร้าง Group และ User ใหม่ (ชื่อ appuser)
RUN addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --gid 1001 appuser

WORKDIR /app

# Copy the virtual environment from the builder stage
COPY --from=builder /app/.venv /app/.venv
# Copy the pre-downloaded model cache
COPY --from=builder --chown=appuser:appgroup /app/.cache /app/.cache

# 2. ก๊อปปี้ไฟล์ที่มีขนาดใหญ่ (โมเดล) แยกมาก่อน เพื่อให้โดน Cache ไว้ถ้าโมเดลไม่เปลี่ยน
COPY --chown=appuser:appgroup src/modules/model/pkl_files/ ./src/modules/model/pkl_files/
COPY --chown=appuser:appgroup src/modules/model/tabm_model.pth ./src/modules/model/tabm_model.pth

# 3. ก๊อปปี้ไฟล์โค้ดของโปรเจกต์ ส่วนนี้จะถูก Build ใหม่เฉพาะตอนแก้โค้ด โดยไม่กระทบ Cache ของโมเดลข้างบน
COPY --chown=appuser:appgroup alembic/ ./alembic/
COPY --chown=appuser:appgroup alembic.ini ./
COPY --chown=appuser:appgroup src/ ./src/

USER appuser

# Use the venv's Python/scripts
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    HF_HOME="/app/.cache"

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
