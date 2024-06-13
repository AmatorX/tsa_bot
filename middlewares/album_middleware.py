import asyncio
from typing import Any, Dict, Union

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


class AlbumMiddleware(BaseMiddleware):
    def __init__(self, latency: Union[int, float] = 0.1):
        self.latency = latency
        self.album_data = {}

    def collect_album_messages(self, event: Message):
        """Collect messages belonging to the same media group (album)."""
        key = event.media_group_id or event.message_id  # Use message_id for single photos
        if key not in self.album_data:
            self.album_data[key] = {"messages": [], "is_last": False}
        self.album_data[key]["messages"].append(event)

    async def __call__(self, handler, event: Message, data: Dict[str, Any]) -> Any:
        self.collect_album_messages(event)

        await asyncio.sleep(self.latency)

        key = event.media_group_id or event.message_id  # Use message_id for single photos
        messages_len = len(self.album_data[key]["messages"])
        if not event.media_group_id or messages_len >= 2:
            self.album_data[key]["is_last"] = True

        if self.album_data[key]["is_last"]:
            album_messages = self.album_data[key]["messages"]
            album_messages.sort(key=lambda x: x.message_id)
            if album_messages[-1].message_id == event.message_id:
                data["album"] = album_messages
                await handler(event, data)
                del self.album_data[key]
