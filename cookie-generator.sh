#!/bin/bash

set -e  # Exit immediately if a command exits with a non-zero status
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Step 1: Install dependencies
echo "📦 Installing Node.js dependencies..."
npm install puppeteer-core clipboardy

# Step 2: Check if Chrome is already running on port 9222
echo "🔍 Checking if Chrome is already running on port 9222..."
if curl --silent http://localhost:9222/json/version | grep -q "webSocketDebuggerUrl"; then
  echo "✅ Chrome is already running with remote debugging."
else
  echo "🚀 Launching Chrome with remote debugging..."
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
    --remote-debugging-port=9222 \
    --user-data-dir=/tmp/chrome-dev-profile \
    --no-first-run \
    --no-default-browser-check \
    > /dev/null 2>&1 &

  CHROME_PID=$!
  echo "✅ Chrome started (PID $CHROME_PID)"

  # Wait for Chrome to be ready
  echo "⏳ Waiting 5 minutes for Chrome to initialize and for user to login..."
  sleep 300
fi

# Step 3: Run cookie generator script
echo "🔑 Running cookie generator..."
node "$SCRIPT_DIR/cookie_generator.mjs"

echo "✅ Done! Cookie should now be saved in .env"

# Optional tip
echo "🛑 Close Chrome window started by this screen when done using app to free the remote debugging port."