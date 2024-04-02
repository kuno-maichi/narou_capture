#!/bin/bash

if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
  echo "Virtual environment created."
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo "Running build_exe.py..."
python build_exe.py 2> /dev/null

read -p "Press any key to continue..."
