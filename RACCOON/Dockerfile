FROM python:3.12-slim

WORKDIR /app
COPY . /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 4005

# Run both main.py and change.py concurrently
CMD ["bash", "-c", "python3 main.py & python3 change.py & wait"]
