# Use Python 3.12.3 as the base image
FROM python:3.12.3-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for Python packages
# RUN apt-get update && apt-get install -y \
#    gcc \
#    && rm -rf /var/lib/apt/lists/*

# Install uv for faster Python package installation
RUN pip install uv

# Copy the entire project directory
COPY . .

# Create virtual environment and install dependencies
RUN uv venv
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN uv pip install .

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the Scrapy settings module
ENV SCRAPY_SETTINGS_MODULE=planning_applications.settings

# Command to run scrapy
WORKDIR /app/planning_applications
ENTRYPOINT ["uv", "run", "scrapy", "crawl"]
CMD ["--help"]