import os
import json
import asyncio
import logging
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import MessageMediaPhoto


load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE_NUMBER = os.getenv("TELEGRAM_PHONE_NUMBER")

BASE_DIR = Path(__file__).resolve().parents[1]
RAW_MESSAGES_DIR = BASE_DIR / "data" / "raw" / "telegram_messages"
RAW_IMAGES_DIR = BASE_DIR / "data" / "raw" / "images"
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=LOG_DIR / "scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

CHANNELS = [
    "CheMed123",
    "lobelia4cosmetics",
    "Tikvahpharm",
]


def clean_channel_name(channel_name: str) -> str:
    return channel_name.lower().replace(" ", "_").replace("-", "_")


def save_json(data, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4, default=str)


async def scrape_channel(client, channel_username: str, limit: int = 100):
    messages = []

    try:
        entity = await client.get_entity(channel_username)
        channel_name = clean_channel_name(getattr(entity, "title", channel_username))

        logging.info(f"Started scraping channel: {channel_name}")

        async for message in client.iter_messages(entity, limit=limit):
            message_date = message.date.strftime("%Y-%m-%d")
            image_path = None

            has_media = message.media is not None

            if isinstance(message.media, MessageMediaPhoto):
                image_dir = RAW_IMAGES_DIR / channel_name
                image_dir.mkdir(parents=True, exist_ok=True)

                image_path = image_dir / f"{message.id}.jpg"
                await client.download_media(message, file=image_path)

            record = {
                "message_id": message.id,
                "channel_name": channel_name,
                "message_date": message.date.isoformat() if message.date else None,
                "message_text": message.message,
                "has_media": has_media,
                "image_path": str(image_path) if image_path else None,
                "views": message.views,
                "forwards": message.forwards,
            }

            messages.append(record)

        if messages:
            scrape_date = datetime.now().strftime("%Y-%m-%d")
            output_path = RAW_MESSAGES_DIR / scrape_date / f"{channel_name}.json"
            save_json(messages, output_path)

        logging.info(f"Finished scraping channel: {channel_name}. Messages: {len(messages)}")

    except Exception as error:
        logging.error(f"Error scraping {channel_username}: {error}")


async def main():
    if not API_ID or not API_HASH:
        raise ValueError("Missing Telegram API credentials. Check your .env file.")

    client = TelegramClient("telegram_scraper_session", int(API_ID), API_HASH)

    async with client:
        for channel_username in CHANNELS:
            await scrape_channel(client, channel_username, limit=100)


if __name__ == "__main__":
    asyncio.run(main())