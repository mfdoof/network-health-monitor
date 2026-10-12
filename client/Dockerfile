# Build from client/: docker build client
FROM node:24-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Runs as a non-root user and listens on 8080
FROM nginxinc/nginx-unprivileged:1.30-alpine
# Filled in by the image's envsubst step at startup
COPY templates/default.conf.template /etc/nginx/templates/default.conf.template
ENV NGINX_ENVSUBST_FILTER=^TRUSTED_PROXY_IP$
ENV TRUSTED_PROXY_IP=127.0.0.1
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 8080
