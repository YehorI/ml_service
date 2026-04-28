import os
from dataclasses import dataclass


@dataclass(frozen=True)
class RabbitMQSettings:
    url: str
    queue_name: str
    prefetch_count: int

    @classmethod
    def from_env(cls) -> "RabbitMQSettings":
        host = os.getenv("RABBITMQ_HOST", "rabbitmq")
        port = os.getenv("RABBITMQ_PORT", "5672")
        user = os.getenv("RABBITMQ_USER", "user")
        password = os.getenv("RABBITMQ_PASSWORD", "Passw0rd")
        vhost = os.getenv("RABBITMQ_VHOST", "/")
        url = os.getenv(
            "RABBITMQ_URL",
            f"amqp://{user}:{password}@{host}:{port}/{vhost.lstrip('/')}",
        )
        return cls(
            url=url,
            queue_name=os.getenv("RABBITMQ_PREDICT_QUEUE", "ml.predict"),
            prefetch_count=int(os.getenv("RABBITMQ_PREFETCH", "1")),
        )
