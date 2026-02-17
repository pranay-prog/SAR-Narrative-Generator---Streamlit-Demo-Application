#!/bin/bash

echo "🚀 Starting SAR Narrative Generator..."
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

echo ""
echo "✅ Dependencies installed!"
echo ""
echo "🌐 Launching application..."
echo "📍 The app will open at: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the application"
echo ""

streamlit run app.py
