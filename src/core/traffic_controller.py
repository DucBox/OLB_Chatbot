import psutil
import time
from collections import deque

CPU_THRESHOLD = 90     # %
RAM_THRESHOLD = 90     # %
MAX_WAIT_TIME = 30     # giây
MAX_QUEUE_SIZE = 20    # giới hạn queue

traffic_queue = deque()

def is_system_overloaded(cpu_thresh=CPU_THRESHOLD, ram_thresh=RAM_THRESHOLD):

    mem = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=0.2)
    return mem.percent > ram_thresh or cpu > cpu_thresh

def queue_if_overloaded(user_id, query_type="chat"):

    if is_system_overloaded():
        if not any(q["user"] == user_id for q in traffic_queue):
            traffic_queue.append({
                "user": user_id,
                "type": query_type,
                "timestamp": time.time()
            })
        return True
    return False

def check_and_dispatch(user_id):

    global traffic_queue 

    if is_system_overloaded():
        for req in traffic_queue:
            if req["user"] == user_id:
                wait_time = time.time() - req["timestamp"]
                return wait_time >= MAX_WAIT_TIME
        return False
    else:
        traffic_queue = deque([q for q in traffic_queue if q["user"] != user_id])
        return True

def get_current_queue():

    return list(traffic_queue)

def clear_user_from_queue(user_id):

    global traffic_queue
    traffic_queue = deque([q for q in traffic_queue if q["user"] != user_id])
