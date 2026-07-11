# =====================================================
# Stage 1 - Build Tailwind CSS
# =====================================================
FROM node:22-alpine AS tailwind-builder

WORKDIR /build

COPY package*.json ./

RUN npm ci

COPY templates ./templates
COPY static ./static

RUN npx @tailwindcss/cli \
    -i ./static/css/input.css \
    -o ./static/css/output.css \
    --minify


# =====================================================
# Stage 2 - Build FastAPI Application
# =====================================================
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY --from=tailwind-builder \
    /build/static/css/output.css \
    /app/static/css/output.css

EXPOSE 8000


CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]