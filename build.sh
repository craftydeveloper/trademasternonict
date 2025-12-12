#!/bin/bash
# Build script for Render deployment

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -e .

echo "Setting up database..."
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Database tables created successfully')
"

echo "Build completed successfully!"