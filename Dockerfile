FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY sigenergy_poller.py .
CMD ["python3", "-u", "sigenergy_poller.py"]
