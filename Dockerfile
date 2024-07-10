# Use the official Python base image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file and install dependencies
COPY src/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY src/ .

# Command to run both consumer scripts concurrently
CMD ["sh", "-c", "python consumer-1.py & python consumer-2.py"]
