FROM node:18-alpine

WORKDIR /app

# Copy package.json and package-lock.json
COPY app/frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend code
COPY app/frontend/ ./

# Build the app
RUN npm run build

# Expose port
EXPOSE 3000

# Start the app
CMD ["npm", "start"] 