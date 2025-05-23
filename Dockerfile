FROM node:20 AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ENV REACT_APP_API_BASE=/api
RUN npm run build

FROM nginx:1.27-alpine
ENV PORT 8080
EXPOSE 8080
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
HEALTHCHECK CMD curl -f http://localhost:8080 || exit 1
CMD ["nginx", "-g", "daemon off;"] 