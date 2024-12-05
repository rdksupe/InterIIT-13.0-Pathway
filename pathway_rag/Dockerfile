FROM python:3.12-slim

WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose necessary port
EXPOSE 4005

# Run the four scripts concurrently as per the README instructions
CMD ["bash", "-c", "fuser -k 4005/tcp && python3 rag_server.py & python3 pw_new.py & python3 http_serve.py & python3 pw_userkb.py & wait"]
