import functools
import json
from asyncio import get_event_loop
from mail.mail_service import mail_service

import aio_pika

from ws_handler import ws_handler


class AMQPHandler:
    EXCHANGE_NAME = "email"
    EXCHANGE_RETRY_NAME = "email_retry"
    QUEUE_NAME = "email_queue"
    QUEUE_RETRY_NAME = "email_retry_queue"

    def __init__(self):
        self.connection = None
        self.channel = None

    async def init(self):
        self.connection = await aio_pika.connect_robust(
            "amqp://guest:guest@localhost:5672/", loop=get_event_loop()
        )
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=100)
        exchange = await self.channel.declare_exchange(
            self.EXCHANGE_NAME,
            aio_pika.ExchangeType.FANOUT,
            durable=True,
        )
        await self.channel.declare_exchange(
            self.EXCHANGE_RETRY_NAME,
            aio_pika.ExchangeType.FANOUT,
            durable=True,
        )
        queue = await self.channel.declare_queue(
            name=self.QUEUE_NAME,
            exclusive=True,
            durable=True,
            arguments={"x-dead-letter-exchange": self.EXCHANGE_RETRY_NAME},
        )
        queue2 = await self.channel.declare_queue(
            name=self.QUEUE_RETRY_NAME,
            exclusive=True,
            durable=True,
            arguments={
                "x-dead-letter-exchange": self.EXCHANGE_NAME,
                "x-message-ttl": 60000,
            },
        )
        await queue.bind(exchange)
        await queue2.bind(exchange)
        await queue.consume(self.handle_email_request)
        return self.connection

    @classmethod
    async def handle_email_request(cls, message: aio_pika.IncomingMessage):
        async with message.process(ignore_processed=True):
            print(f"Message: {json.loads(message.body)}")
            try:
                mail_service.mock_raise_exception_send_email()
                message.ack()
            except Exception as e:
                print(f"Error: {e}")
                await message.reject()

    async def publish(self, data: dict):
        message = aio_pika.Message(
            body=json.dumps(data).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        exchange = await self.channel.declare_exchange(
            self.EXCHANGE_NAME, aio_pika.ExchangeType.FANOUT, durable=True
        )
        await exchange.publish(message, routing_key=self.QUEUE_NAME)


amqp_handler_v2 = AMQPHandler()
