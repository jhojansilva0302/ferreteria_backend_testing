# ==========================================
# ETAPA 1: Builder (Compilación de paquetes)
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar paquetes
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos e instalar wheels
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================
# ETAPA 2: Final (Imagen liviana de ejecución)
# ==========================================
FROM python:3.11-slim AS final

WORKDIR /app

# Instalar librerías de tiempo de ejecución para PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copiar paquetes instalados desde la etapa anterior
COPY --from=builder /usr/local /usr/local
COPY . /app/

# Asegurar que los binarios ejecutables estén en el PATH
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Buenas prácticas de seguridad: Crear usuario no raíz (non-root)
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]