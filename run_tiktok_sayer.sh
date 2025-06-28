#!/bin/bash

echo "Starting TikTok-Sayer..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.6 or higher."
    echo "Visit https://www.python.org/downloads/ to download Python."
    exit 1
fi

# Check if requirements are installed
echo "Checking requirements..."
pip3 install -r requirements.txt

# Run the application
echo "Launching TikTok-Sayer..."
python3 tiktok_sayer.py