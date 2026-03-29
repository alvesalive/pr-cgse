FROM python:3.11-slim
WORKDIR /app

# Instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia código (stub initial)
COPY . .

# O docker-compose fará o run do script de seed && o uvicorn
CMD ["sh", "-c", "python seed.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
