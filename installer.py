# PyHx/installer.py

import os
import getpass
import json
import hashlib
import shutil
import textwrap

# --- Helper Functions (self-contained for the installer) ---
CONFIG_DIR = "config"
USERS_FILE = os.path.join(CONFIG_DIR, "users.json")
HOSTNAME_FILE = os.path.join(CONFIG_DIR, "hostname.txt")

def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def save_users(users_data):
    """Saves user data to the JSON file."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, indent=4)

def save_hostname(hostname):
    """Saves the hostname to its file."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(HOSTNAME_FILE, 'w', encoding='utf-8') as f:
        f.write(hostname)

def clear_screen():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

# --- Dockerfile Generation ---
def create_docker_files():
    """Generates the Dockerfile and other necessary files for a portable environment."""
    
    dockerfile_content = """
# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /pyhx-os

# Copy the entire project directory into the container
COPY . .

# (Optional) Install any system-level dependencies your apps might need
# RUN apt-get update && apt-get install -y ...

# (Optional) Install any Python dependencies listed in requirements.txt
# RUN pip install --no-cache-dir -r requirements.txt

# Command to run on container start
CMD ["python", "main.py"]
"""
    
    readme_content = """
# PyHx OS - Portable Docker Environment

This package contains everything needed to run PyHx OS in an isolated Docker container.

## Prerequisites
- Docker must be installed on your system.

## How to Run

1. Open a terminal in this directory.
2. Build the Docker image by running:
   ```bash
   docker build -t pyhx-os .
