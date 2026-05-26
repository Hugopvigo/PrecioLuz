import asyncio
import logging
import os
import signal
import sys

from telegram.ext import ApplicationBuilder

from bot.scheduler import setup_scheduler
from bot.db import init_db
from bot.handlers import register_handlers

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger("bot.main")

shutdown_event = asyncio.Event()


def _signal_handler(_sig, _frame):
    logger.info("Signal received, initiating graceful shutdown...")
    shutdown_event.set()


async def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.critical("TELEGRAM_BOT_TOKEN not set")
        sys.exit(1)

    await init_db()

    app = ApplicationBuilder().token(token).build()
    register_handlers(app)

    scheduler = setup_scheduler(app)
    scheduler.start()
    logger.info("Scheduler started")

    loop = asyncio.get_running_loop()
    for sig in (signal.SIGTERM, signal.SIGINT):
        loop.add_signal_handler(sig, _signal_handler)

    await app.initialize()
    await app.start()
    await app.updater.start_polling()

    logger.info("PrecioLuz Bot running")

    await shutdown_event.wait()

    logger.info("Shutting down...")
    scheduler.shutdown(wait=False)
    await app.updater.stop()
    await app.stop()
    await app.shutdown()
    logger.info("Goodbye")


if __name__ == "__main__":
    asyncio.run(main())
