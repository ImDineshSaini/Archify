#!/bin/bash

echo "Setting up Archify frontend locally..."

# Check Node version
node_version=$(node --version 2>&1)
echo "Node version: $node_version"

# Install dependencies
echo "Installing npm dependencies..."
cd frontend
npm install

echo ""
echo "✅ Frontend setup complete!"
echo ""
echo "To run the frontend:"
echo "cd frontend && npm run dev"
echo ""
echo "Frontend will be available at: http://localhost:3000"
