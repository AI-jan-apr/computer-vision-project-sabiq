# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Install required system libraries
RUN apt-get update && apt-get install -y \
    libgl1 \          # Needed for some image/ML libraries
    libglib2.0-0 \    # Required by certain Python packages
    && rm -rf /var/lib/apt/lists/*  # Clean up to reduce image size

# Copy dependency file
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy all project files into the container
COPY . .

# Expose port 7860
EXPOSE 7860

# Run the app using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
