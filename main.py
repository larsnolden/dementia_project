import multiprocessing as mp
from android_server import activity_tracking
from assistant import schedule_assistant

import schedule as scd
import time as time


activities = ["Sitting", "Standing", "Walking", "BrushingTeeth", "Eating", "Laying"]

if __name__ == '__main__':
    parent_conn, child_conn = mp.Pipe()
    tracking_process = mp.Process(target=activity_tracking, args=(child_conn, activities))
    assistant_process = mp.Process(target=schedule_assistant, args=(parent_conn, activities))
    tracking_process.start()
    assistant_process.start()
    tracking_process.join()
    assistant_process.join()