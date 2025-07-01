FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy the rest of the application
COPY . .

# Build the application for production
RUN npm run build

# Install serve to run the production build
RUN npm install -g serve

# Expose the default port
EXPOSE 3000

# Start the production server
CMD ["serve", "-s", "dist", "-l", "3000"]

# Development stage
FROM node:18-alpine as development

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host"] 