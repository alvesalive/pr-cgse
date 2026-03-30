FROM node:20-slim
WORKDIR /app
COPY package*.json ./
RUN npm config set strict-ssl false && npm install --legacy-peer-deps
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview", "--", "--host", "0.0.0.0", "--port", "3000"]
