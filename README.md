# Telegram Trabajo Bot

Bot de Telegram para conectar con tu portátil desde el móvil:
- Avisar cuando hayas terminado de trabajar
- Enviar pedidos/tareas desde el móvil
- Consultar el estado de la sesión de trabajo

## Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/ChocoShit/telegram_trabajo_bot.git
   cd telegram_trabajo_bot
   ```

2. Crea un entorno virtual e instala dependencias:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   # source .venv/bin/activate  # Linux/Mac
   pip install -r requirements.txt
   ```

3. Crea el archivo `.env` copiando el ejemplo:
   ```bash
   copy .env.example .env   # Windows
   # cp .env.example .env   # Linux/Mac
   ```

4. Edita `.env` con tu token de BotFather y tu ID de Telegram.

5. Ejecuta el bot:
   ```bash
   python bot.py
   ```

## Comandos

| Comando | Descripción |
|---------|-------------|
| `/start` | Muestra la ayuda |
| `/trabajo` | Inicia una sesión de trabajo |
| `/fin` | Finaliza la sesión y avisa |
| `/estado` | Indica si hay trabajo en curso |
| `/pedido <texto>` | Registra un pedido/tarea |
| `/ping` | Comprueba que el bot responde |

## Estructura

- `bot.py` — código principal del bot
- `.env` — credenciales (no se sube a GitHub)
- `.env.example` — plantilla de credenciales
- `data/` — archivos de sesiones y pedidos (generados al ejecutar)
- `requirements.txt` — dependencias de Python
