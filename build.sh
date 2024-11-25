#!/bin/bash

# Install required packages
pip3 install -r requirements.txt

# Set up Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Check if db.sqlite3 exists and delete it
if [ -f "db.sqlite3" ]; then
    echo "Deleting existing db.sqlite3..."
    rm db.sqlite3
else
    echo "No db.sqlite3 file found. Proceeding..."
fi

# Run Django migrations
python3 manage.py makemigrations
python3 manage.py migrate

# Load initial mock data
python3 manage.py loaddata mock_data2.json

# Navigate to frontend directory
echo "Navigating to frontend directory..."
cd frontend || { echo "Frontend directory not found. Exiting..."; exit 1; }

# Install frontend dependencies and build
echo "Installing frontend dependencies..."
npm install

echo "Building frontend assets..."
npm run build

# Return to the project root and start the Django server
echo "Returning to project root..."
cd .. || { echo "Failed to return to project root. Exiting..."; exit 1; }

# Run Django development server
echo "Starting Django development server on localhost:8001..."
python3 manage.py runserver localhost:8001