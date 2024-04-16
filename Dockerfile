# Use a smaller base image
FROM python:3.12-alpine

# Set the working directory to /app/src
WORKDIR /app/src

# Copy only the requirements file first to leverage Docker caching
COPY src/requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the working directory contents into the container at /app/src
COPY src/ .

# Run app.py when the container launches
CMD ["python", "main.py"]
