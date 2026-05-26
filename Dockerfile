FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


FROM base AS dependencies

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


FROM base AS production

RUN useradd -m appuser

COPY --from=dependencies /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=dependencies /usr/local/bin /usr/local/bin

COPY . .

RUN chmod +x /app/start.sh

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["./start.sh"]
