FROM python:3.11

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "worker.py", "--host", "rabbitmq", "--queue", "image_tasks", "--output", "/app/results"]