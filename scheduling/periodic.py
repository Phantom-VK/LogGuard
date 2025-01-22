import threading
import time
def periodic_task():
    print("Executing periodic task")
    threading.Timer(10,periodic_task).start()