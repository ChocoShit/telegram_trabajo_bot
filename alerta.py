#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Envía un mensaje de alerta a través del bot de Telegram desde el portátil.

Uso:
  python alerta.py "Texto de la alerta"
  python alerta.py "Trabajo terminado" --ids 6933795477
"""
import asyncio
import os
import sys
from pathlib import Path

from telegram import Bot
from telegram.request import HTTPXRequest


def load_env():
    p = Path(__file__).resolve().parent / ".env"
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


async def main():
    if len(sys.argv) < 2:
        print("Uso: python alerta.py \"Texto de la alerta\"")
        sys.exit(1)

    load_env()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    user_ids = os.getenv("TELEGRAM_USER_IDS", "")
    if not token:
        print("ERROR: TELEGRAM_BOT_TOKEN no está definido en .env")
        sys.exit(1)

    texto = " ".join(sys.argv[1:])
    request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0, write_timeout=30.0, pool_timeout=30.0)
    bot = Bot(token=token, request=request)

    ids = [int(x.strip()) for x in user_ids.split(",") if x.strip().isdigit()]
    for uid in ids:
        await bot.send_message(chat_id=uid, text=f"🔔 *Alerta del portátil*\n\n{texto}", parse_mode="Markdown")
        print(f"Enviado a {uid}")


if __name__ == "__main__":
    asyncio.run(main())