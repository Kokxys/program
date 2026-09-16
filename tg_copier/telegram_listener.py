import logging
from datetime import datetime, timezone
from typing import Callable, Dict, Iterable, Set

from telethon import TelegramClient, events

logger = logging.getLogger(__name__)


class TelegramListener:
    def __init__(
        self,
        api_id: int,
        api_hash: str,
        session_name: str,
        channel_ids: Iterable[int],
        on_message: Callable[[int, str], None],
    ) -> None:
        self.client = TelegramClient(session_name, api_id, api_hash)
        self.channel_ids: Set[int] = set(channel_ids)
        self.on_message = on_message

    async def start(self) -> None:
        self.client.add_event_handler(self._handle_message, events.NewMessage())
        await self.client.start()
        logger.info("Telegram listener started")
        await self.client.run_until_disconnected()

    async def _handle_message(self, event: events.NewMessage.Event) -> None:
        if not event.is_channel:
            return
        channel_id = event.chat_id
        if channel_id not in self.channel_ids:
            return
        message_time = event.message.date
        if message_time is None:
            return
        age_seconds = (datetime.now(timezone.utc) - message_time).total_seconds()
        if age_seconds > 60:
            logger.info("Ignoring old message from %s", channel_id)
            return
        text = event.message.message or ""
        if not text.strip():
            return
        logger.info("Received message from %s", channel_id)
        self.on_message(channel_id, text)
