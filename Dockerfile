FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variables for the server
ENV PORT=7860
EXPOSE 7860

# Start from the server subdirectory
CMD ["python", "server/main.py"]
