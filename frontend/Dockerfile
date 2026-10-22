FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Served from the site root and talking to the API through nginx, not the GitHub Pages snapshot.
ENV VITE_BASE=/ VITE_API_URL=/api
RUN npm run build

FROM nginx:1.27-alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template
ENV API_UPSTREAM=http://api:8000
EXPOSE 80
