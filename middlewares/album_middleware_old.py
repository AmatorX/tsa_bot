import asyncio
from typing import Any, Dict, Union

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


class AlbumMiddleware(BaseMiddleware):
    def __init__(self, latency: Union[int, float] = 0.1):
        self.latency = latency
        self.album_data = (
            {}
        )  # Dictionary to hold the media_group_id and corresponding messages

    def collect_album_messages(self, event: Message):
        """Collect messages belonging to the same media group (album)."""
        if event.media_group_id not in self.album_data:
            self.album_data[event.media_group_id] = {"messages": [], "is_last": False}
        self.album_data[event.media_group_id]["messages"].append(event)

    async def __call__(self, handler, event: Message, data: Dict[str, Any]) -> Any:
        if not event.media_group_id:
            return await handler(event, data)

        self.collect_album_messages(event)

        await asyncio.sleep(self.latency)

        if (
            len(self.album_data[event.media_group_id]["messages"]) >= 2
        ):  # Assuming an album has at least 2 messages
            self.album_data[event.media_group_id]["is_last"] = True

        if self.album_data[event.media_group_id]["is_last"]:
            album_messages = self.album_data[event.media_group_id]["messages"]
            album_messages.sort(key=lambda x: x.message_id)
            if album_messages[-1].message_id == event.message_id:
                data["album"] = album_messages
                await handler(event, data)
                del self.album_data[
                    event.media_group_id
                ]  # Remove the media group from tracking