import functools
import json
from asyncio import get_event_loop
from mail.mail_service import mail_service

import aio_pika

from ws_handler import ws_handler


class AMQPHandler:
    QUEUE_NAME = "email_queue"

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
            self.QUEUE_NAME,
            aio_pika.ExchangeType.FANOUT,
        )
        queue = await self.channel.declare_queue(exclusive=True)
        await queue.bind(exchange)
        on_message_callback = functools.partial(
            self.handle_email_request, args={"channel": self.channel}
        )
        await queue.consume(on_message_callback)
        return self.connection

    @classmethod
    async def handle_email_request(
        cls, message: aio_pika.IncomingMessage, **kwargs: dict
    ):
        print(f"kwargs: {kwargs['args']}")
        args = kwargs["args"]
        async with message.process():
            print(f"Message: {json.loads(message.body)}")
            mail_service.mock_send_email()

    async def publish(self, data: dict):
        message = aio_pika.Message(
            body=json.dumps(data).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        exchange = await self.channel.declare_exchange(
            self.QUEUE_NAME, aio_pika.ExchangeType.FANOUT
        )
        await exchange.publish(message, routing_key=self.QUEUE_NAME)


amqp_handler_v2 = AMQPHandler()
