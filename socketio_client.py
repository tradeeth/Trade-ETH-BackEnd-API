import asyncio
import json
import logging
from time import sleep, time
from websockets import connect
from websockets.exceptions import ConnectionClosed

ENGINEIO_PING_INTERVAL = 25
ENGINEIO_PING_TIMEOUT = 60

ENGINEIO_OPEN = "0"
ENGINEIO_CLOSE = "1"
ENGINEIO_PING = "2"
ENGINEIO_PONG = "3"
ENGINEIO_MESSAGE = "4"
ENGINEIO_IGNORABLE = frozenset([])

SOCKETIO_OPEN = "0"
SOCKETIO_EVENT = "2"
SOCKETIO_IGNORABLE = frozenset((SOCKETIO_OPEN, ))

LOG_FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'

class SocketIOClient:
    def __init__(self, ws_url):
        self.ws_url = ws_url
        self.callbacks = {}

        self.__configure_loggers()
        self.ws = None
        self.last_pong = None

    def on(self, event_name):
        def set_handler(handler):
            self.callbacks[event_name] = handler
            return handler
        return set_handler

    async def start(self):
        logger = logging.getLogger('websockets')
        logger.info("Connecting to %s", self.ws_url)
        try:
            async with connect(self.ws_url) as websocket:
                self.ws = websocket
                if "connect" in self.callbacks:
                    await self.callbacks["connect"](websocket, "connect")
                async for message in websocket:
                    await self.engineio_consumer(message)
        except ConnectionClosed as err:
            if "disconnect" in self.callbacks:
                await self.callbacks["disconnect"](websocket, "disconnect")
            logger.error("Connection closed: %s", str(err))

    async def emit(self, event, payload):
        logger = logging.getLogger('socketio')
        json_payload = json.dumps([event, payload])
        msg = ENGINEIO_MESSAGE + SOCKETIO_EVENT + json_payload
        logger.debug("Send '%s'", msg)
        await self.ws.send(msg)

    async def engineio_consumer(self, message):
        logger = logging.getLogger('engineio')

        if len(message) > 0:
            if message[0] == ENGINEIO_MESSAGE:
                logger.debug("message: '%s'", message[1:65])
                await self.socketio_consumer(message[1:])
            elif message[0] == ENGINEIO_OPEN:
                self.last_pong = None
                asyncio.ensure_future(self.engineio_ping())
                logger.debug("Pinger started")
            elif message[0] == ENGINEIO_PONG:
                logger.debug("Pong received")
                self.last_pong = time()
            elif message[0] in ENGINEIO_IGNORABLE:
                logger.debug("Ignorable engine.io type '%s' with message '%s...'", message[0], message[:65])
            else:
                logger.warn("Unknown engine.io type '%s' with message '%s...'", message[0], message[:65])
        else:
            logger.debug("Got an empty message")

    async def engineio_ping(self):
        logger = logging.getLogger('engineio')

        while self.ws.open:
            await asyncio.sleep(ENGINEIO_PING_INTERVAL)
            alive = (not self.last_pong) or (time() - self.last_pong < ENGINEIO_PING_INTERVAL + ENGINEIO_PING_TIMEOUT)
            if alive:
                await self.ws.send(ENGINEIO_PING)
                logger.debug("Ping sent")
            else:
                logger.warn("Pong timeout: %i seconds since last pong, disconnect", time() - last_pong)
                await self.ws.close()

    async def socketio_consumer(self, message):
        logger = logging.getLogger('socketio')
        if len(message) > 0:
            if message[0] == SOCKETIO_EVENT:
                logger.debug("event: '%s'", message[1:65])
                await self.consume_socketio_event(message[1:])
            elif message[0] in SOCKETIO_IGNORABLE:
                logger.debug("ignorable type '%s' with message '%s...'", message[0], message[:65])
            else:
                logger.warn("unknown type '%s' with message '%s...'", message[0], message[:65])
        else:
            logger.debug("Got an empty message")

    async def consume_socketio_event(self, json_payload):
        try:
            event_name, payload = json.loads(json_payload)
        except json.JSONDecodeError as error:
            if "error" in self.callbacks:
                await self.callbacks["error"](self.ws, "error", error)
        else:
            if event_name in self.callbacks:
                await self.callbacks[event_name](self.ws, event_name, payload)

    def __configure_loggers(self):
        logging.basicConfig(format=LOG_FORMAT)
        for (logger_name, logger_level) in (('websockets', logging.WARN), ('engineio', logging.WARN), ('socketio', logging.DEBUG)):
            logging.getLogger(logger_name).setLevel(logger_level)