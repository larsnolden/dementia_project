import schedule as scd
import time

def schedule_assistant(parent_conn, activities):
    current_activity_i = parent_conn.recv()[0]
    current_activity = activities[current_activity_i]
    scd.every(4).seconds.do(assistant, parent_conn, activities)

    while True:
        scd.run_pending()
        time.sleep(1)

def assistant(parent_conn, activities):
    current_activity_i = parent_conn.recv()[0]
    current_activity = activities[current_activity_i]
    print('assistant')
    print(current_activity)

def assistantPrint(current_activity):
    print('current activity: ')
    print(current_activity)
    return
