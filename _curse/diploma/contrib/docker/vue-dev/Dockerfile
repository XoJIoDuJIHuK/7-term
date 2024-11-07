FROM node:18-alpine

WORKDIR /app

COPY ./contrib/front/ /app/

RUN npm install


#FROM nginx:latest
#
#COPY --from=builder /app/dist /usr/share/nginx/html
