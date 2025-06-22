# Use official Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Create virtual environment & install dependencies + run migrations
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --upgrade pip \
 && /opt/venv/bin/pip install -r requirements.txt \
 && /opt/venv/bin/python manage.py makemigrations \
 && /opt/venv/bin/python manage.py migrate \
 && /opt/venv/bin/python manage.py collectstatic --noinput

# Set virtualenv in PATH
ENV PATH="/opt/venv/bin:$PATH"

# Expose port (optional)
EXPOSE 8000

# Start gunicorn
CMD ["gunicorn", "vipera.wsgi:application", "--bind", "0.0.0.0:8000"]
