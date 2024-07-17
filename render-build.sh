#!/bin/bash

# Update and install build tools
apt-get update && apt-get install -y build-essential gcc

# Install Python dependencies
pip install -r requirements.txt
