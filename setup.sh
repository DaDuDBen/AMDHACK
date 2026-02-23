#!/bin/bash
# Prayog-Shala local dev setup

echo "Setting up backend..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
echo "Backend ready."

echo "Setting up frontend..."
cd ../frontend
npm install
echo "Frontend ready."

echo "Done. Run: source backend/venv/bin/activate && uvicorn main:app --reload"
