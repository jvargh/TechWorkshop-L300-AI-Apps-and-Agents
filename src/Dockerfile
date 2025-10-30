
FROM python:3.12-slim

# Upgrade pip and system packages to reduce vulnerabilities
RUN apt-get update && apt-get upgrade -y && pip install --upgrade pip && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install system dependencies (including ODBC for pyodbc, OpenCV, and all common video/image libraries)
RUN apt-get update && apt-get install -y \
    build-essential unixodbc-dev gcc g++ \
    libgl1 libglib2.0-0 libsm6 libxext6 libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


# Copy the rest of the code
COPY . .

# Copy .env file into the image (for python-dotenv)
COPY .env .env

# Expose the port for A2A application
EXPOSE 8001

# Set environment variables (override in production)
ENV PORT=8001

# Start the A2A FastAPI app
CMD ["python", "-m", "a2a.main"]
