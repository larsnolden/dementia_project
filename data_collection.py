#!/usr/bin/env python
import socket
import sys
import asyncio
import websockets
import time
import numpy as np
import json
import joblib
import pandas as pd

SOCKET_PORT = 8766
WEBSOCKET_PORT = 8765

model = joblib.load('./decision_tree.pkl')
acitivies = ['Downstairs', 'Running', 'Sitting', 'Standing', 'Upstairs', 'Walking']
current_sensor_data = []


# data settings
data_size = 256  # sending 16 bytes = 128 bits (binary touch states, for example)

def predict(sensor_data):
    # TODO: add model
    random_index = np.random.randint(0, 5, 1)[0]
    response = {}
    response['activity'] = acitivies[random_index]
    return json.dumps(response)

async def get_resp(reader):
    while True:
        resp = await reader.read(5000)
        if resp == b'':
            break
        print(resp.decode())

async def handleWebsocket(websocket):
    print('Established Websocket connection')
    while True:
        # resp = await reader.read(data_size)
        # if resp == b'':
        #     break
        # print(resp.decode())
        # pass current sensor_data
        activity_prediction = predict(current_sensor_data)
        await websocket.send(activity_prediction)

async def handleSocket(reader, writer):
    request = None
    while request != 'quit':
        request = (await reader.read(255)).decode('utf8')
        response = str(eval(request)) + '\n'
        writer.write(response.encode('utf8'))
        await writer.drain()
    writer.close()

async def main():
    print(model.predict([[0.46309182,8.785124,4.195067,0.06750061,0.50915617,0.42271876,-8.16,-49.62,-6.7799997]])[0])
    socket_server = await asyncio.start_server(handleSocket, 'localhost', SOCKET_PORT)
    await websockets.serve(
        lambda websocket, path: handleWebsocket(websocket, path),
        'localhost', WEBSOCKET_PORT
    )
    # await get_resp(reader)

asyncio.run(main())

