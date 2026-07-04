FROM python:3.11-slim
WORKDIR /app
RUN pip install requests
COPY watcher.py .
CMD ["python", "watcher.py"]
