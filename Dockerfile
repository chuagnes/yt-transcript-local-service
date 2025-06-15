# Dockerfile for Flask + yt-dlp + Puppeteer backend

FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y wget gnupg curl ca-certificates ffmpeg chromium chromium-driver git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Node.js (for Puppeteer)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs

# Install Python dependencies
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install yt-dlp
RUN pip install yt-dlp

# Install Puppeteer and dependencies
COPY package.json ./
RUN npm install

# Copy app code
COPY . .

# Puppeteer Chromium path fix
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium
ENV CHROME_BIN=/usr/bin/chromium

CMD ["python", "app.py"]