"""
Message Bus
-----------
Pub/sub event log for all inter-agent communications.
Agents publish messages; the bus records them with timestamps.
The orchestrator and document manager can inspect the full log.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable


@dataclass
class Message:
    sender: str
    recipient: str
    topic: str
    content: str
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class MessageBus:
    """
    Singleton-style message bus shared across all agents in a pipeline run.
    Agents call bus.publish() to log inter-agent queries and responses.
    """

    def __init__(self):
        self._log: list[Message] = []
        self._subscribers: dict[str, list[Callable]] = {}

    def publish(self, sender: str, recipient: str, topic: str, content: str) -> Message:
        msg = Message(sender=sender, recipient=recipient, topic=topic, content=content)
        self._log.append(msg)
        for cb in self._subscribers.get(topic, []):
            cb(msg)
        return msg

    def subscribe(self, topic: str, callback: Callable):
        self._subscribers.setdefault(topic, []).append(callback)

    def get_log(self, sender: str = None, recipient: str = None) -> list[Message]:
        msgs = self._log
        if sender:
            msgs = [m for m in msgs if m.sender == sender]
        if recipient:
            msgs = [m for m in msgs if m.recipient == recipient]
        return msgs

    def format_log(self) -> str:
        lines = []
        for m in self._log:
            lines.append(
                f"[{m.timestamp}] **{m.sender}** → **{m.recipient}** | _{m.topic}_\n{m.content}\n"
            )
        return "\n---\n".join(lines)

    def __len__(self):
        return len(self._log)
