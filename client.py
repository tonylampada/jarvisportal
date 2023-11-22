import asyncio
import websockets
import json
import actions
from random import randint


async def test_websocket():
    user_id = "tony"
    # uri = "ws://127.0.0.1:8000/ws"  # Substitua pela URL do seu WebSocket
    uri = "wss://gptexec.evolutio.io/ws"  # Substitua pela URL do seu WebSocket
    async with websockets.connect(uri) as websocket:
        await websocket.send(user_id)
        while True:
            msg = json.loads(await websocket.recv())
            action = {
                "id": randint(0, 1000000),
                "function": {
                    "name": msg["function"],
                    "arguments": msg["arguments"]
                }
            }
            actionresult = actions._exec_action(action)
            await websocket.send(json.dumps(actionresult))

# Executar a função de teste do WebSocket
asyncio.get_event_loop().run_until_complete(test_websocket())
