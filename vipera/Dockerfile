# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Create virtualenv and install dependencies
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install -r requirements.txt

# Set virtualenv path
ENV PATH="/opt/venv/bin:$PATH"

# Expose port (optional)
EXPOSE 8000

# Start gunicorn with evaluated $PORT
CMD ["sh", "-c", "gunicorn vipera.wsgi:application --bind 0.0.0.0:$PORT"]
