from fastapi import FastAPI

from amqp import amqp_handler
from rabbitmq.amqp_v2 import amqp_handler_v2
from routes import router

app = FastAPI()

app.include_router(router)


@app.on_event('startup')
async def startup():
    # await amqp_handler.init()
    await amqp_handler_v2.init()
