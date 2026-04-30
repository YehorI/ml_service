from pydantic_settings import BaseSettings


class MessagingSettings(BaseSettings):
    url: str = "amqp://user:Passw0rd@rabbitmq:5672/"
    queue_name: str = "ml.predict"
    prefetch_count: int = 1


class BillingMessagingSettings(MessagingSettings):
    queue_name: str = "ml.billing"
