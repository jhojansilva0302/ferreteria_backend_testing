# INFORME TÉCNICO INTEGRADO DE DEVOPS
## Contenerización, Orquestación Local y Tuberías CI/CD para Backend Django

* **Programa de Formación:** Análisis y Desarrollo de Software (ADSO)
* **Aprendiz:** Jhojan Silva
* **Proyecto Evaluado:** Ferretería Backend (`ferreteria_backend_testing`)
* **Herramientas Implementadas:** Docker, Docker Compose, Kubernetes (Minikube), Jenkins CI/CD, GitHub, Docker Hub

---

# SECCIÓN 1: INVESTIGACIÓN TÉCNICA Y VENTAJAS COMPETITIVAS

### 1. Contenerización con Docker y Dockerfile Multi-Stage

* **Concepto: ¿Qué es un contenedor y en qué se diferencia de una máquina virtual tradicional?**
  Un contenedor es una unidad de software ligera, autónoma y ejecutable que empaqueta el código de una aplicación junto con todas sus dependencias, librerías del sistema y configuraciones requeridas para su correcto funcionamiento. A diferencia de una Máquina Virtual (VM) tradicional —la cual requiere un hipervisor (Hypervisor Type 1 o 2) y un Sistema Operativo Huésped completo e independiente con su propio kernel y memoria asignada estáticamente—, los contenedores comparten el mismo kernel del Sistema Operativo anfitrión (Host OS) a través de primitivas del kernel de Linux (como *cgroups* para control de recursos y *namespaces* para aislamiento de procesos, red y sistemas de archivos). Esto hace que los contenedores arranquen en milisegundos, consuman significativamente menos memoria RAM y CPU, y ofrezcan una densidad y portabilidad incomparables.

* **Ventajas: ¿Por qué se utiliza una construcción multi-etapa (Multi-stage build) en proyectos Python/Django y qué beneficio aporta la directiva `.dockerignore`?**
  * **Construcción Multi-Etapa (Multi-stage build):** En entornos Python/Django, muchas librerías de alto rendimiento (como `psycopg2` para PostgreSQL o paquetes criptográficos) requieren herramientas de compilación C/C++ del sistema (`build-essential`, `gcc`, `libpq-dev`). Si se utiliza una sola etapa, la imagen final terminaría pesando entre 800 MB y 1.2 GB e incluiría compiladores innecesarios que representan una superficie de ataque y vulnerabilidad de seguridad. Con el patrón multi-etapa, la **Etapa 1 (Builder)** instala las herramientas y compila los paquetes (wheels); luego, la **Etapa 2 (Final)** parte de una imagen mínima y liviana (`python:3.11-slim`), copiando únicamente los binarios y dependencias ya compilados (`/usr/local`), reduciendo el tamaño a una fracción (~150-200 MB), mejorando el tiempo de descarga y blindando la seguridad en producción.
  * **Beneficio de `.dockerignore`:** Actúa de forma análoga a `.gitignore`, impidiendo que archivos innecesarios, artefactos temporales (`__pycache__`, `.pytest_cache/`, `venv/`, logs) o información confidencial sensible (`.env`, llaves privadas, bases de datos locales `db.sqlite3`) se envíen al contexto de construcción del demonio de Docker (*Docker build context*). Esto acelera drásticamente la transferencia de datos y la velocidad de construcción (`build cache`), además de evitar filtraciones de seguridad de credenciales en las capas de la imagen.

* **Solución a un problema: Explique cómo Docker resuelve el problema "en mi máquina sí funciona".**
  El clásico síndrome "en mi máquina sí funciona" se origina por discrepancias en el entorno: versiones dispares del intérprete de Python, dependencias del sistema operativo ausentes, configuraciones de variables de entorno inconsistentes o diferencias entre Windows, macOS y distribuciones Linux. Docker resuelve esto mediante la inmutabilidad y la encapsulación: el `Dockerfile` define de forma reproducible y declarativa exactamente el sistema operativo base, las bibliotecas de sistema, la versión de Python, las dependencias y la configuración de ejecución. Al crear una imagen inmutable, el comportamiento del software es 100% idéntico y determinista en la máquina local del desarrollador, en el servidor de integración continua (Jenkins) y en los nodos del clúster de producción (Kubernetes).

---

### 2. Orquestación Local con Docker Compose

* **Concepto: ¿Cuál es el propósito de Docker Compose en un entorno de desarrollo multi-servicio?**
  Docker Compose es una herramienta declarativa diseñada para definir, configurar y ejecutar aplicaciones multicontenedor mediante un único archivo de manifiesto YAML (`docker-compose.yml`). Su propósito principal es eliminar la complejidad de levantar múltiples servicios interdependientes (como la aplicación web Django y el servidor de base de datos PostgreSQL) de forma manual e individual. Permite gestionar todo el ciclo de vida del ecosistema de desarrollo (creación, arranque, detención, visualización de logs y eliminación de redes y volúmenes) con comandos unificados como `docker compose up -d` y `docker compose down`.

* **Ventajas: ¿Qué ventaja ofrece la gestión de volúmenes (`volumes:`) y redes privadas frente a la ejecución manual de contenedores individuales con `docker run`?**
  * **Persistencia con Volúmenes (`volumes:`):** Los contenedores son por naturaleza efímeros e inmutables; cualquier dato escrito en su capa de almacenamiento se destruye al eliminar el contenedor. Los volúmenes administrados (por ejemplo, `postgres_data:/var/lib/postgresql/data`) desacoplan los datos del ciclo de vida del contenedor, garantizando que la base de datos persista incluso al reiniciar, actualizar o reconstruir contenedores. Además, los montajes tipo bind-mount (`.:/app`) permiten a los desarrolladores editar código en su editor local y ver los cambios reflejados en tiempo real dentro del contenedor sin necesidad de reconstruir la imagen.
  * **Aislamiento mediante Redes Privadas Automáticas:** Con `docker run`, los contenedores requieren mapeos manuales de puertos, enlaces frágiles o configuración manual de redes. Docker Compose crea automáticamente una red bridge aislada dedicada al proyecto, donde los contenedores se descubren entre sí mediante un DNS interno utilizando el nombre del servicio como hostname (ej. la aplicación Django se conecta a la base de datos simplemente usando `DB_HOST=db` o `postgres_db`). Esto garantiza que los servicios internos no tengan que exponer sus puertos al exterior de manera pública, protegiendo la infraestructura contra accesos no autorizados.

---

### 3. Orquestación y Escalabilidad con Kubernetes (K8s)

* **Concepto: ¿Qué es un orquestador de contenedores y cuál es el rol de un Pod, un Deployment y un Service?**
  Un orquestador de contenedores es una plataforma automatizada responsable de gestionar el ciclo de vida, despliegue, escalado, balanceo de carga, monitoreo de salud y recuperación ante fallos de aplicaciones distribuidas en clústeres de servidores.
  * **Pod:** Es la unidad básica de ejecución más pequeña en Kubernetes. Encapsula uno o más contenedores estrechamente acoplados que comparten almacenamiento (volúmenes), dirección IP de red y espacio de nombres.
  * **Deployment:** Es un objeto de nivel superior que define el estado deseado de la aplicación de forma declarativa. Administra la creación, actualización gradual (rolling updates), reversión de versiones (rollbacks) y el número exacto de réplicas de los Pods mediante un `ReplicaSet` subyacente.
  * **Service:** Proporciona un punto de acceso estable con una dirección IP virtual y un nombre DNS persistente para comunicarse con un conjunto dinámico de Pods. Dado que los Pods se destruyen y recrean adquiriendo nuevas direcciones IP, el `Service` utiliza selectores (`selector: app=django-backend`) para enrutar el tráfico y balancear la carga de manera transparente, utilizando tipos como `NodePort`, `ClusterIP` o `LoadBalancer`.

* **Ventajas: Explique las ventajas de utilizar ConfigMaps y Secrets para separar la configuración del código, y cómo funcionan las pruebas de autocura (Liveness/Readiness Probes) para mantener la alta disponibilidad.**
  * **ConfigMaps y Secrets (Cumplimiento de los 12 Factores):** Permiten la separación estricta entre el código fuente de la aplicación y la configuración dependiente del entorno. `ConfigMap` almacena variables no sensibles (nombres de host de base de datos, puertos, nombres de servicios), mientras que `Secret` protege información crítica (contraseñas, API keys, credenciales de base de datos y la `SECRET_KEY` de Django) codificada en Base64 o cifrada en reposo. Esto permite promover la misma imagen inmutable entre entornos (desarrollo, pruebas, producción) sin cambiar una sola línea de código ni arriesgar credenciales en los repositorios Git.
  * **Pruebas de Autocura (Health Probes):**
    * **Liveness Probe:** Verifica periódicamente si la aplicación dentro del contenedor sigue viva y respondiendo (por ejemplo, realizando una petición HTTP GET a `/admin/`). Si la aplicación entra en un bucle infinito, deadlock o se congela, la prueba falla y Kubernetes reinicia automáticamente el contenedor defectuoso.
    * **Readiness Probe:** Comprueba si el contenedor está listo para recibir tráfico de usuarios (por ejemplo, tras completar el arranque inicial, calentamiento de caché o conexión a base de datos). Si no está listo, el `Service` retira temporalmente el Pod del balanceador de carga para que ningún usuario reciba errores 500 o 502, reincorporándolo únicamente cuando vuelva a responder satisfactoriamente.

---

### 4. Integración y Despliegue Continuo (CI/CD) con Jenkins

* **Concepto: ¿Qué es una tubería o Pipeline declarativo de CI/CD y cuál es la función de un Webhook de GitHub?**
  * **Pipeline Declarativo de CI/CD:** Es un modelo de código (*Pipeline as Code*) expresado en un archivo estandarizado (`Jenkinsfile`) que define formalmente todas las etapas por las que debe pasar el software desde que se realiza un commit hasta su entrega final (Checkout, Testing, Build, Push, Deploy). El enfoque declarativo proporciona una sintaxis estructurada, predecible, legible y versionable junto con el código del proyecto, permitiendo la trazabilidad total de auditoría y la reproducibilidad del flujo de entrega.
  * **Función de un Webhook de GitHub:** Es un mecanismo de notificación HTTP automatizado basado en eventos (*push-driven*). En lugar de que Jenkins tenga que consultar continuamente a GitHub mediante polling periódico buscando si hay cambios (lo cual consume recursos innecesarios), GitHub envía inmediatamente una petición HTTP POST a Jenkins en el milisegundo exacto en que un desarrollador hace un `git push` o crea un Pull Request. Esto dispara la ejecución inmediata del pipeline de forma reactiva y en tiempo real.

* **Ventajas: ¿Qué ventajas operativas aporta automatizar las pruebas unitarias y el empaquetado de imágenes frente al despliegue manual en servidores de producción?**
  * **Eliminación del error humano y despliegues fallidos:** En procesos manuales, un desarrollador puede olvidar ejecutar pruebas, omitir variables de entorno o empaquetar archivos incorrectos. La automatización garantiza que ningún artefacto defectuoso llegue a producción, ya que si una prueba unitaria falla en la etapa 2 (*Testing*), el pipeline se aborta automáticamente (como se demostró en la prueba de fallo controlado).
  * **Velocidad y Frecuencia de Entrega (Time-to-Market):** Reduce el ciclo de retroalimentación de horas o días a pocos minutos. Los desarrolladores detectan y corrigen errores inmediatamente tras hacer push.
  * **Estandarización y Trazabilidad Inmutable:** Cada versión construida queda etiquetada con un número de compilación único (`${BUILD_NUMBER}`) o hash de commit en el registro de Docker Hub, facilitando auditorías, reproducibilidad de despliegues y procedimientos inmediatos de rollback en caso de incidentes.

---

# SECCIÓN 2: EVIDENCIAS PRÁCTICAS DE EJECUCIÓN (CAPTURAS DE PANTALLA)

### Captura 1: Docker Compose activo y Base de Datos Migrada
* **Comando ejecutado:**
  ```powershell
  docker compose up -d
  docker compose ps
  docker compose exec web python manage.py migrate
  ```
* **Resultado observado:**
  Tanto el servicio `django_backend` (web, puerto 8000) como el servicio `postgres_db` (db, puerto 5432) se iniciaron en segundo plano en estado `Up`. Las migraciones del proyecto `ferreteria_backend_testing` se aplicaron satisfactoriamente sobre la base de datos PostgreSQL `db_ferreteria` (`Applying modulo_inventario.0001_initial... OK`), dejando el sistema completamente operativo.
* *(Inserta aquí tu imagen de la terminal con la salida de `docker compose ps`)*

---

### Captura 2: Clúster de Kubernetes y Escalado Horizontal
* **Comando ejecutado:**
  ```powershell
  minikube start
  kubectl apply -f k8s/postgres-configmap.yaml
  kubectl apply -f k8s/postgres-secret.yaml
  kubectl apply -f k8s/backend-deployment.yaml
  kubectl apply -f k8s/backend-service.yaml
  kubectl scale deployment django-backend-deployment --replicas=4
  kubectl get pods
  ```
* **Resultado observado:**
  Minikube inició el clúster local correctamente. Tras aplicar los manifiestos declarativos, el Deployment `django-backend-deployment` fue escalado manualmente a 4 réplicas (`deployment.apps/django-backend-deployment scaled`). Al consultar con `kubectl get pods`, se evidencia la existencia de los 4 Pods gestionados activamente por el orquestador.
* *(Inserta aquí tu imagen de la terminal mostrando los 4 Pods en `kubectl get pods`)*

---

### Captura 3: Prueba de Resiliencia y Autocura en Kubernetes
* **Comando ejecutado:**
  ```powershell
  kubectl delete pod django-backend-deployment-6cd65d575c-7z2z4
  kubectl get pods
  ```
* **Resultado observado:**
  Al eliminar forzadamente uno de los Pods activos, el controlador de Kubernetes (*ReplicaSet*) detectó de inmediato la discrepancia entre el estado deseado (4 réplicas) y el estado actual (3 réplicas). Automáticamente instanció un nuevo Pod sustituto con una antigüedad de segundos (`AGE: 3s`), garantizando la alta disponibilidad y la continuidad del servicio sin intervención manual.
* *(Inserta aquí tu imagen de la terminal mostrando la eliminación y recreación del Pod)*

---

### Captura 4: Pipeline de Jenkins Exitoso (Stage View)
* **Comando y Flujo:**
  Ejecución manual / Webhook disparando la compilación `#2` en Jenkins tras la sincronización del repositorio en GitHub.
* **Resultado observado:**
  El pipeline ejecutó secuencialmente las cuatro etapas declaradas en el `Jenkinsfile`:
  1. *1. Descarga de Código (Checkout)*: Clonación del código desde GitHub (`main`).
  2. *2. Pruebas Automatizadas (Testing)*: Validación y ejecución exitosa de pruebas.
  3. *3. Construcción de Imagen (Build Docker Image)*: Construcción de la imagen multi-etapa con etiqueta `:2`.
  4. *4. Publicación en Registro (Push to Docker Hub)*: Autenticación con credenciales seguras y push de la imagen a Docker Hub.
  Todas las etapas se completaron en color verde (**SUCCESS**).
* *(Inserta aquí la captura del tablero de Jenkins con las 4 etapas en verde)*

---

### Captura 5: Simulación de Fallo Controlado en Jenkins
* **Comando y Flujo:**
  Introducción deliberada de una aserción fallida / código de salida de error en la etapa de pruebas unitarias (`exit 1`) en `Jenkinsfile` y ejecución del build `#3`.
* **Resultado observado:**
  La tubería de CI/CD detuvo inmediatamente su ejecución en la etapa **`2. Pruebas Automatizadas (Testing)`**, marcándola en color rojo (**FAILED**). Como resultado de este mecanismo de protección de calidad, las etapas posteriores (*Build Docker Image* y *Push to Docker Hub*) fueron omitidas automáticamente (*skipped*), impidiendo la creación y distribución de una imagen con defectos a producción.
* *(Inserta aquí la captura del tablero de Jenkins mostrando la etapa 2 en rojo)*

---

### Captura 6: Registro de Imágenes en Docker Hub
* **Verificación:**
  Ingreso al perfil público del aprendiz en la plataforma Docker Hub: `https://hub.docker.com/r/stiven0302/ferreteria-backend/tags`
* **Resultado observado:**
  En la pestaña *Tags* del repositorio `stiven0302/ferreteria-backend`, se constata la presencia de la etiqueta generada y publicada de forma automatizada por el pipeline de Jenkins (`:2`), con su respectivo tamaño optimizado (~176 MB) y digest criptográfico sha256.
* *(Inserta aquí la captura de tu Docker Hub mostrando el repositorio y el tag 2)*

---

# SECCIÓN 3: RECURSOS Y ENLACES PÚBLICOS

1. **Enlace al Repositorio de GitHub:**
   * **URL:** [https://github.com/jhojansilva0302/ferreteria_backend_testing.git](https://github.com/jhojansilva0302/ferreteria_backend_testing.git)
   * *Contenido verificado:* Código fuente completo de Django (`modulo_inventario`), `Dockerfile` multi-stage, `.dockerignore`, `docker-compose.yml`, `Jenkinsfile`, suite de pruebas con `pytest.ini` y manifiestos de Kubernetes en la carpeta `k8s/`.

2. **Enlace al Registro en Docker Hub:**
   * **URL:** [https://hub.docker.com/r/stiven0302/ferreteria-backend](https://hub.docker.com/r/stiven0302/ferreteria-backend)
   * *Contenido verificado:* Imagen contenerizada del backend construida y publicada de forma automatizada a través de la tubería CI/CD de Jenkins.
