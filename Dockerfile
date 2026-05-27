FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m appuser && \
    chown -R appuser:appuser /app

RUN chmod +x /app/start.sh

USER appuser

EXPOSE 8000

CMD ["./start.sh"]
