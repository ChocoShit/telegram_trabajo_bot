#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Trabajo Bot
--------------------
Bot para conectar con tu portátil desde el móvil por Telegram.
Funciones:
  - /trabajo : marca el inicio de una sesión de trabajo
  - /fin     : marca el final y te avisa por Telegram
  - /estado  : consulta si hay trabajo en curso
  - /pedido  : envía un pedido/tarea al bot (queda registrado)
  - /ping    : comprueba que el bot está vivo

Variables de entorno (en .env):
  TELEGRAM_BOT_TOKEN  - token de BotFather
  TELEGRAM_USER_IDS   - IDs de usuario autorizados (separados por coma)
"""

import os
import sys
import json
import logging
from datetime import datetime
from pathlib import Path
from contextlib import suppress

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Carga de variables de entorno desde .env (sin dependencias externas)
def load_env(path: str = None) -> None:
    if path is None:
        path = Path(__file__).resolve().parent / ".env"
    p = Path(path)
    if not p.is_file():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        if os.environ.get(key):
            continue
        os.environ[key] = value


load_env()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
raw_user_ids = os.getenv("TELEGRAM_USER_IDS")
if not BOT_TOKEN:
    print("ERROR: TELEGRAM_BOT_TOKEN no está definido en .env")
    sys.exit(1)
if not raw_user_ids:
    print("ERROR: TELEGRAM_USER_IDS no está definido en .env")
    sys.exit(1)

USER_IDS = [int(x.strip()) for x in raw_user_ids.split(",") if x.strip().isdigit()]
if not USER_IDS:
    print("ERROR: TELEGRAM_USER_IDS no contiene IDs válidos")
    sys.exit(1)

DATA_DIR = Path(__file__).resolve().parent / "data"
DATA_DIR.mkdir(exist_ok=True)
SESSIONS_FILE = DATA_DIR / "sessions.json"
PEDIDOS_FILE = DATA_DIR / "pedidos.json"


def _load_json(path: Path, default):
    try:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        pass
    return default


def _save_json(path: Path, data) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _es_usuario_autorizado(user_id: int) -> bool:
    return user_id in USER_IDS


def _ahora() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _fecha() -> str:
    return datetime.now().strftime("%Y-%m-%d")


# ---------- Handlers ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not _es_usuario_autorizado(user.id):
        await update.message.reply_text("No estás autorizado para usar este bot.")
        return
    texto = (
        "👋 *Trabajo Bot*\n\n"
        "Comandos disponibles:\n"
        "• `/trabajo` — iniciar sesión de trabajo\n"
        "• `/fin` — terminar sesión y recibir aviso\n"
        "• `/estado` — saber si hay trabajo en curso\n"
        "• `/pedido <texto>` — enviar un pedido/tarea\n"
        "• `/ping` — comprobar que el bot responde\n\n"
        "Desde el móvil puedes usarlo en cualquier momento."
    )
    await update.message.reply_text(texto, parse_mode="Markdown")


async def trabajo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not _es_usuario_autorizado(user.id):
        await update.message.reply_text("No estás autorizado para usar este bot.")
        return

    sessions = _load_json(SESSIONS_FILE, [])
    hoy = _fecha()
    ya_abierta = any(
        s.get("fecha") == hoy and not s.get("fin")
        for s in sessions
    )
    if ya_abierta:
        await update.message.reply_text(
            "⚠️ Ya hay una sesión de trabajo abierta hoy. Usa `/fin` para cerrarla.",
            parse_mode="Markdown",
        )
        return

    sesion = {
        "id": len(sessions) + 1,
        "fecha": hoy,
        "inicio": _ahora(),
        "fin": None,
        "usuario": user.id,
        "usuario_nombre": user.full_name or user.username or "usuario",
    }
    sessions.append(sesion)
    _save_json(SESSIONS_FILE, sessions)

    await update.message.reply_text(
        f"✅ Sesión de trabajo iniciada a las {sesion['inicio'].split(' ')[1]}.\n"
        "Usa `/fin` cuando termines."
    )


async def fin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not _es_usuario_autorizado(user.id):
        await update.message.reply_text("No estás autorizado para usar este bot.")
        return

    sessions = _load_json(SESSIONS_FILE, [])
    hoy = _fecha()
    sesion_abierta = None
    for s in sessions:
        if s.get("fecha") == hoy and not s.get("fin"):
            sesion_abierta = s
            break

    if not sesion_abierta:
        await update.message.reply_text(
            "ℹ️ No hay ninguna sesión de trabajo abierta hoy."
        )
        return

    sesion_abierta["fin"] = _ahora()
    _save_json(SESSIONS_FILE, sessions)

    inicio = sesion_abierta["inicio"].split(" ")[1]
    fin_hora = sesion_abierta["fin"].split(" ")[1]
    await update.message.reply_text(
        f"✅ Sesión de trabajo finalizada.\n"
        f"🕒 Inicio: {inicio}\n"
        f"🕒 Fin: {fin_hora}\n\n"
        "Buen descanso."
    )


async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not _es_usuario_autorizado(user.id):
        await update.message.reply_text("No estás autorizado para usar este bot.")
        return

    sessions = _load_json(SESSIONS_FILE, [])
    hoy = _fecha()
    abierta = any(
        s.get("fecha") == hoy and not s.get("fin") for s in sessions
    )
    if abierta:
        await update.message.reply_text("🟢 Hay una sesión de trabajo abierta hoy.")
    else:
        await update.message.reply_text("🔴 No hay sesión de trabajo abierta hoy.")


async def pedido(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not _es_usuario_autorizado(user.id):
        await update.message.reply_text("No estás autorizado para usar este bot.")
        return

    if not context.args:
        await update.message.reply_text(
            "Uso: `/pedido <texto del pedido>`\n"
            "Ejemplo: `/pedido Revisar el informe de gastos`",
            parse_mode="Markdown",
        )
        return

    texto_pedido = " ".join(context.args)
    pedidos = _load_json(PEDIDOS_FILE, [])
    pedido_nuevo = {
        "id": len(pedidos) + 1,
        "fecha": _fecha(),
        "hora": _ahora().split(" ")[1],
        "usuario": user.id,
        "usuario_nombre": user.full_name or user.username or "usuario",
        "texto": texto_pedido,
        "estado": "pendiente",
    }
    pedidos.append(pedido_nuevo)
    _save_json(PEDIDOS_FILE, pedidos)

    await update.message.reply_text(
        f"📋 Pedido #{pedido_nuevo['id']} registrado:\n"
        f"{texto_pedido}\n\n"
        "Lo tengo anotado."
    )


async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not _es_usuario_autorizado(user.id):
        await update.message.reply_text("No estás autorizado para usar este bot.")
        return
    await update.message.reply_text("🏓 ¡El bot está vivo!")


async def desconocido(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    if not _es_usuario_autorizado(user.id):
        return
    await update.message.reply_text(
        "Comando no reconocido. Usa `/start` para ver la ayuda.",
        parse_mode="Markdown",
    )


# ---------- Main ----------

def main() -> None:
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("trabajo", trabajo))
    app.add_handler(CommandHandler("fin", fin))
    app.add_handler(CommandHandler("estado", estado))
    app.add_handler(CommandHandler("pedido", pedido))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(MessageHandler(filters.COMMAND, desconocido))

    print("🤖 Trabajo Bot iniciado. Presiona Ctrl+C para detener.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        main()
