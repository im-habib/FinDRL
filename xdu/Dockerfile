# Use an official Ubuntu-based Python image
FROM ubuntu:22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    VENV_PATH=/opt/venv \
    PROJECT_ROOT=/thesis \
    DATA_DIR=/thesis/data

# Update and install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-venv \
    python3-pip \
    python3-dev \
    build-essential \
    pkg-config \
    gfortran \
    libopenblas-dev \
    liblapack-dev \
    libffi-dev \
    bash \
    && rm -rf /var/lib/apt/lists/*

# Ensure python3 is the default
RUN ln -s /usr/bin/python3 /usr/bin/python

# Create a virtual environment
RUN python -m venv $VENV_PATH
ENV PATH="$VENV_PATH/bin:$PATH"

# Copy all project files to the image
WORKDIR $PROJECT_ROOT
COPY . $PROJECT_ROOT

# Upgrade pip, setuptools, and wheel before installing dependencies
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install TensorFlow separately to avoid dependency issues
RUN pip install --no-cache-dir tensorflow

# Install all dependencies from requirements.txt
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Expose port for Jupyter Notebook
EXPOSE 8888

# Use the virtual environment for all commands
ENTRYPOINT ["jupyter"]

# Command to run Jupyter Notebook
CMD ["notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]