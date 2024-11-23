FROM node:10-alpine

WORKDIR /srv/app

COPY package*.json ./
RUN npm install

EXPOSE 55566/tcp

COPY docker/webpack/docker-entrypoint.sh /usr/local/bin/
ENTRYPOINT ["docker-entrypoint.sh"]

CMD ["npm", "run", "start"]
