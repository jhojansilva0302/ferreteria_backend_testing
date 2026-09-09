# Ferretería Backend API & Automation Testing

Proyecto backend en Django REST Framework y suites de pruebas automatizadas con **Postman/Newman CLI** y **Cypress**.

## 🚀 Características
- **API Backend**: Django 6 + Django REST Framework + PostgreSQL.
- **Autenticación**: Token Authentication (`/api/v1/auth/`).
- **Módulo Inventario**: CRUD completo de productos con cálculo automático de IVA (19%).
- **Pruebas Automatizadas**:
  - Pruebas unitarias/integración en Django (`python manage.py test`).
  - Pruebas API en Postman & Newman CLI con generación de reporte HTML.
  - Pruebas E2E / Integración en Cypress (`npx cypress run`).

## 🛠️ Instalación y Configuración

1. **Clonar e instalar dependencias**:
   ```powershell
   git clone https://github.com/Andrescg18/ferreteria_testing.git
   cd ferreteria_backend_testing
   ```

2. **Entorno Virtual e Instalación de Python**:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt # o dependencias del venv
   ```

3. **Migraciones de Base de Datos**:
   ```powershell
   python manage.py migrate
   ```

4. **Iniciar el Servidor**:
   ```powershell
   python manage.py runserver
   ```

## 🧪 Pruebas

- **Pruebas Django**:
  ```powershell
  python manage.py test
  ```

- **Newman CLI (Postman)**:
  ```powershell
  npx newman run pruebas_postman/Ferreteria_API.postman_collection.json -e pruebas_postman/Entorno_Local.postman_environment.json
  ```

- **Cypress E2E**:
  ```powershell
  npx cypress run --spec "cypress/e2e/ferreteria_api_spec.cy.js"
  ```
