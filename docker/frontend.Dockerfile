# Build stage
FROM node:14 AS build

WORKDIR /usr/src/app

COPY frontend_react/package*.json ./

RUN npm install

COPY frontend_react/ .

RUN npm run build

# Nginx stage
FROM nginx:stable-alpine

# Copy the built static files from the build stage
COPY --from=build /usr/src/app/build /usr/share/nginx/html

# Copy the custom Nginx configuration
COPY default.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
