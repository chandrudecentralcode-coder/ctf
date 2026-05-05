FROM python:3.11-slim
WORKDIR /app
RUN mkdir -p /data
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app.py .
COPY templates/ templates/
EXPOSE 8000
# 4 worker processes × 4 threads = 16 concurrent requests
CMD ["gunicorn", "app:app", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "4", \
     "--threads", "4", \
     "--timeout", "60", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
