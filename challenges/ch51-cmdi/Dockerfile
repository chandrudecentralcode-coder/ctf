FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y iputils-ping --no-install-recommends && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]
