# Use the official Python image from the Docker Hub
FROM python:3.9.18-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install system dependencies and Rust (Cargo)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Set Cargo's bin directory in the PATH environment variable
ENV PATH="/root/.cargo/bin:${PATH}"

# Install any needed dependencies specified in requirements.txt
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container at /app
COPY . .

# Run the application
CMD ["python", "Main_App_Starter.py"]
