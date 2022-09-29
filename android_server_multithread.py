import socket
from tokenize import Double
import joblib
from collections import Counter
import pandas as pd
import os
import json
import datetime
import time
from threading import Thread
import pygame
import gpio

file = open("eventsTEST.JSON")
listJson = json.load(file)


def cls():
    return
    os.system('cls' if os.name=='nt' else 'clear')

def playSound(mp3file):
    pygame.mixer.init()
    pygame.mixer.music.load(mp3file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy() == True:
        continue

def toggleLight(id, on):
    gpio.set_light(id, on)

def assistant():
    while True:
        time.sleep(30)
        print("Assistant Started")

        now = datetime.datetime.now()
        currentHour = now.hour
        currentMinute = now.minute

        for event in listJson:
            currentTimeInMinutes = currentHour*60 + currentMinute
            eventTimeBeginningInMinutes = event["timeWindow"]["beginning"]["hour"]*60 + event["timeWindow"]["beginning"]["minutes"]
            eventTimeEndInMinutes = event["timeWindow"]["end"]["hour"] * 60 + event["timeWindow"]["end"]["minutes"]

            if (eventTimeBeginningInMinutes < currentTimeInMinutes and eventTimeEndInMinutes > currentTimeInMinutes
            and not event["isComplete"]):
                event["isInTimeWindow"] = True
                if not event["isLightTurned"]:
                    event["isLightTurned"] = True
                    print("Light ON for", event["activityName"])
                    toggleLight(event["ledId"], True)
                #Remind
                playSound(event["voiceReminders"][0])
            elif event["isLightTurned"] and event["isInTimeWindow"] and not event["isComplete"]:
                event["isInTimeWindow"] = False
                event["isLightTurned"] = False
                print("Light OFF for", event["activityName"])
                toggleLight(event["ledId"], False)
            else:
                event["isInTimeWindow"] = False

# data settings
data_size = 100  # sending 16 bytes = 128 bits (binary touch states, for example)

# server settings
HOST = '172.20.10.4'
PORT = 8776
EXPORT_FOLDER_PATH='./training_data'
server_address = (HOST, PORT)

model = joblib.load('./decision_tree.pkl')

# start up server
print('Setting up server on:', server_address)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    server_socket.bind(server_address)
except socket.error as err:
    print("Bind Filed, Error Code", str(err[0]), " Message: ", err[1])

print("Socket Bind Success!")
server_socket.listen(10)
print("Socket Listening")

# wait for connection
print('Waiting for a client connection...')
connection, client_address = server_socket.accept()
print('Connected to:', client_address)


print("Starting Assistant")
Thread(target = assistant).start()

# listen for data for forever
window = []
export_df = pd.DataFrame(columns=['time', 'seconds_elapsed', 'Ax', 'Ay', 'Az', 'Gx' ,'Gy', 'Gz', 'Activity'])
current_recording_activity = None
needs_to_save = False
classified = False

while True:
    data = connection.recv(data_size)
    received_string = data.decode("utf-8")
    if received_string != "":
        # print('Received', received_string)
        # print(window,'\n',  properties, '\n', received_string)
        properties = received_string.split(",")

        #print(properties)

        # last item in the sent data identifies the activity bein recorded
        # if that activity is Null then we should classify the incoming data
        if(len(properties) != 9):
            continue
        if(properties[-1] == 'Null'):
            # classify activity / start analysis
            if(needs_to_save):
                # save dataframe from previous recording when analysys starts again
                # analysis indicates end of recording
                date_and_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                export_df.to_csv('%s/%s_%s.csv'%(EXPORT_FOLDER_PATH, current_recording_activity, date_and_time))
                print(export_df.head(5))
                export_df = pd.DataFrame(columns=['time', 'seconds_elapsed', 'Ax', 'Ay', 'Az', 'Gx' ,'Gy', 'Gz', 'Activity'])
                needs_to_save = False
                window = []
                cls()
            try:
                parsed = list(map(lambda x: float(x), properties[2:8]))
                window.append(parsed) #skip over magnetometer data
            except:
                print(received_string)
                print('bad data overlap')

            if(len(window) == 30):
                predictions = model.predict(window[0:30])
                count = Counter(predictions)
                cls()
                count = {k: v for k, v in sorted(count.items(), key=lambda item: item[1], reverse=True)}
                #for key in count.keys():
                #    print('%s:%d%%'%(key, int(round(count.get(key)/30*100, 0))))
                #
                print("Highest Prediction: ", list(count.keys())[0] )
                for event in listJson:
                    if (not event["isComplete"] and event["isInTimeWindow"] and event["condition"] ==  list(count.keys())[0] ):
                        event["isComplete"] = True
                        event["isLightTurned"] = False
                        print(event["condition"], " is Done")
                        print("LIGHT OFF for", event["activityName"])
                        toggleLight(event["ledId"], False)

            if len(window) == 40:
                predictions = model.predict(window[10:40])
                count = Counter(predictions)
                count = {k: v for k, v in sorted(count.items(), key=lambda item: item[1], reverse=True)}
                cls()
                #for key in count.keys():
                #    print('%s:%d%%'%(key, int(round(count.get(key)/30*100, 0))))
                #
                print("Highest Prediction: ", list(count.keys())[0] )
                for event in listJson:
                    if (not event["isComplete"] and event["isInTimeWindow"] and event["condition"] ==  list(count.keys())[0] ):
                        event["isComplete"] = True
                        event["isLightTurned"]
                        print(event["condition"], " is Done")
                        print("LIGHT OFF for", event["activityName"])
                        toggleLight(event["ledId"], False)
                window = []
            classified = True
        else:
            # record activity
            if(classified):
                window = []
                classified = False
                needs_to_save = True
            print('record')
            print(len(window))
            try:
                parsed = list(map(lambda x: float(x), properties[0:8])) # do not pase the activity, bcs it's a string
                current_recording_activity = properties[-1]
                window.append(parsed[0:8] + [properties[-1]]) #skip over magnetometer data 
            except:
                print('bad data overlap')
            if(len(window) == 25):
                print('add to df')
                # save all 100 measurements
                for measurement in window:
                    new_row = pd.Series({'time': measurement[0], 'seconds_elapsed': measurement[1], 'Ax': measurement[2], 'Ay': measurement[3], 'Az': measurement[4], 'Gx': measurement[5], 'Gy': measurement[6], 'Gz': measurement[7], 'Activity': measurement[-1] })
                    print(new_row.head(4))
                    export_df = pd.concat([export_df, new_row.to_frame().T], ignore_index=True)
                window = []

                


