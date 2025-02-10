# COTFAC-VS

Sistema de Cotizaciones y Facturación para VIANG SOLUTION

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/sharkstar03/COTFAC-VS.git
cd COTFAC-VS

python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Editar .env con tus configuraciones

python init_db.py

python run.py


URL: http://localhost:5000
Usuario: admin
Contraseña: admin123



Para ejecutar el proyecto:

1. Primero crea el entorno virtual e instala las dependencias:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt


python init_db.py

python run.py