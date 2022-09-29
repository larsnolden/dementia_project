import json


file = open("eventsKris.JSON")
list = json.load(file)

currentHour = 7
currentMinute = 0

def progressTime(currentHour, currentMinute):
    currentMinute += 10
    if (currentMinute == 60):
        currentMinute = 0
        currentHour += 1

    print("Time:", currentHour, currentMinute)

    return (currentHour, currentMinute)



while True:

    activitiesInTimeWindow = []

    inputActivity = ""
    while (inputActivity != "end"):
        inputActivity = input("Enter an activity for this time window: ")
        activitiesInTimeWindow.append(inputActivity)
        #For each reading of activity
        for event in list:
            if (not event["isComplete"] and event["isInTimeWindow"] and event["activityName"] == inputActivity):
                event["isComplete"] = True
                print(event["activityName"], " is Done")
                #Off light
                #Good Job Sound??

    print(activitiesInTimeWindow)

    #Every 10 minutes
    currentHour, currentMinute = progressTime(currentHour, currentMinute)
    if (currentHour == 22):
        break

    for event in list:
        currentTimeInMinutes = currentHour*60 + currentMinute
        eventTimeBeginningInMinutes = event["timeWindow"]["beginning"]["hour"]*60 + event["timeWindow"]["beginning"]["minutes"]
        eventTimeEndInMinutes = event["timeWindow"]["end"]["hour"] * 60 + event["timeWindow"]["end"]["minutes"]

        if (eventTimeBeginningInMinutes < currentTimeInMinutes and eventTimeEndInMinutes > currentTimeInMinutes
        and not event["isComplete"]):
            event["isInTimeWindow"] = True
            if not event["isLightTurned"]:
                event["isLightTurned"] = True
                print("Light ON for", event["activityName"])
        elif event["isLightTurned"]:
            event["isInTimeWindow"] = False
            event["isLightTurned"] = False
            print("Light OFF for", event["activityName"])
            #TODO turn off light for event
            print("Outside of time frame", "You did not do it")
        else:
            event["isInTimeWindow"] = False


