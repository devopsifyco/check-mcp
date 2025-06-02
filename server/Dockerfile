FROM python:3.12-slim

ARG PORT=8050

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Copy the MCP server files
COPY . .

# Install packages system-wide
RUN uv pip install --system -e .

# Create directory for environment file
RUN mkdir -p /app/config

EXPOSE ${PORT}

# Command to run the MCP server
CMD ["uv", "run", "src/main.py"]