# Build stage
FROM node:16-alpine as build-stage

WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install dependencies with specific registry to avoid timeout issues
RUN npm config set registry https://registry.npmjs.org/ && \
    npm install

# Copy project files
COPY . .

# Build app
RUN npm run build

# Production stage
FROM nginx:1.23-alpine as production-stage

# Copy built files from build stage
COPY --from=build-stage /app/dist /usr/share/nginx/html

# Copy custom nginx config for Vue.js routing and API proxying
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
