FROM python:3-slim

# Working directory inside the container
WORKDIR /app

# Copy only the pyproject first (layer caching)
COPY pyproject.toml .

# Install project dependencies using PEP 517/518
RUN pip install --no-cache-dir .

# Copy the rest of your source code
COPY . .

# Expose the port the Flask/Gunicorn server will run on
EXPOSE 8000

# Run using gunicorn in production
# (main.py contains: app = Flask(__name__))
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app"]
