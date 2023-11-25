import asyncio
import websockets
import json
import actions
from random import randint
import os
import requests
from websockets.exceptions import ConnectionClosedError

BASE_DOMAIN = "s://gptexec.evolutio.io"
# BASE_DOMAIN = "://localhost:8000"

async def test_websocket():
    userhome = os.path.expanduser("~")
    configfilepath = f"{userhome}/.jarvis-config.json"
    device_key = None
    if not os.path.exists(configfilepath):
        user_devicekey = input("Enter your devices key: ")
        if not user_devicekey:
            print("No devices key provided. Exiting...")
            exit(1)
        device_name = input("Enter a device name: ")
        if not device_name:
            print("No device name provided. Exiting...")
            exit(1)
        device_description = input("Add a device description (optional): ")
        device_key = register_device(user_devicekey, device_name, device_description)
        with open(configfilepath, "w") as file:
            json.dump({"device_key": device_key}, file)
    else:
        with open(configfilepath, "r") as file:
            config = json.load(file)
            device_key = config["device_key"]
    uri = f"ws{BASE_DOMAIN}/ws"
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                await websocket.send(device_key)
                print("Connected. waiting for commands...")
                while True:
                    msg = json.loads(await websocket.recv())
                    action = {
                        "id": randint(0, 1000000),
                        "function": {
                            "name": msg["function"],
                            "arguments": msg["arguments"]
                        }
                    }
                    actionresult = actions.exec_action(action)
                    await websocket.send(json.dumps(actionresult))
        except  ConnectionClosedError:
            print("Connection closed. Reconnecting...")
            await asyncio.sleep(5)

def register_device(user_devicekey, device_name, device_description):
    uri = f"http{BASE_DOMAIN}/api/registerdevice"
    data = {
        "user_devicekey": user_devicekey,
        "device_name": device_name,
        "device_description": device_description
    }
    r = requests.post(uri, json=data)
    if r.status_code != 200:
        print(f"Error registering device: {r.status_code} - {r.text}")
        exit(1)
    result = r.json()
    if not result["success"]:
        print(f"Error registering device: {result['message']}")
        exit(1)
    device_key = result["key"]
    return device_key


def main():
    asyncio.get_event_loop().run_until_complete(test_websocket())

if __name__ == "__main__":
    main()