import socketio


class TaskNamespace(socketio.AsyncNamespace):
    async def on_join(self, sid: str, username: str) -> None:
        await self.enter_room(sid, f"user_{username}")
