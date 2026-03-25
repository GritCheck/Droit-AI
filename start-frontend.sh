#!/bin/bash

echo "🚀 Starting Droit AI Frontend..."
echo "================================"

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the frontend directory"
    echo "💡 Run: cd frontend && ./start-frontend.sh"
    exit 1
fi

# Check if .env.local exists
if [ ! -f ".env.local" ]; then
    echo "❌ Error: .env.local file not found"
    echo "💡 Creating .env.local with default configuration..."
    cat > .env.local << EOF
NEXT_PUBLIC_SERVER_URL=http://localhost:8000
NODE_ENV=development
EOF
    echo "✅ Created .env.local"
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start the development server
echo "🌐 Starting development server on http://localhost:3000"
echo "📊 Dashboard will be available at: http://localhost:3000/dashboard"
echo ""
echo "💡 Make sure the backend is running on http://localhost:8000"
echo "🔧 Backend start: cd ../backend && python -m uvicorn app.main:app --reload --port 8000"
echo ""
echo "🎉 Starting frontend..."
npm run dev
