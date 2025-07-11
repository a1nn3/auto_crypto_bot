# Use official Python 3.11 slim image for compatibility with latest packages
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy requirements file into the container
COPY requirements.txt .

# Install Python dependencies without cache to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Default command to run your bot
CMD ["python3", "main.py"]
