# FROM node:20-alpine AS builder

# WORKDIR /app
# RUN npm install -g uglify-js
# COPY src/ .
# RUN node --test
# RUN find . -type f -name '*.js' -exec uglifyjs {} -c -m -o {} \;

FROM nginx

COPY nginx.conf /etc/nginx/conf.d/default.conf
RUN rm -rf /usr/share/nginx/html/*
# COPY --from=builder /app /usr/share/nginx/html

EXPOSE 9000