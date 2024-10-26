#!/usr/bin/env python3

import threading
import socket
import os
import pickle
from pathlib import Path
from typing import Dict

import database
import maps_traffic
import screenshotscheduler

SOCKET_LOCATION = '/tmp/uds_socket'
SCREENSHOT_PATH = Path.home() / 'screenshots_output'
DATABASE = './database.db'

scheduler = screenshotscheduler.ScreenshotScheduler(maps_traffic.get_screenshots_now)

def main():
    db = database.Database(DATABASE)

    # plan things in database
    for row in db.get_rows_generator():
        create(scheduler, row)
    start()
    # Make sure the socket does not already exist
    try:
        os.unlink(SOCKET_LOCATION)
    except OSError:
        if os.path.exists(SOCKET_LOCATION):
            raise

    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as sock:
        print(f'[Info] Starting server up on {SOCKET_LOCATION}')
        sock.bind(SOCKET_LOCATION)
        sock.listen(1)
        while True:
            # Wait for connection
            connection, client_address = sock.accept()
            with connection:
                while True:
                    data = connection.recv(1024)
                    if data:
                        data_dict = pickle.loads(data)
                        for order, payload in data_dict.items():
                            if order == 'CREATE':
                                db.store(**payload)
                                create(scheduler, payload)
                                start()
                            elif order == 'DELETE':
                                remove(scheduler, payload)
                            elif order == 'DEBUG':
                                scheduler.get_queue()
                                for x in scheduler.queue:
                                    print(x)
                                start()
                                print('run done')

                    else:
                        break


def create(scheduler, data_dict: Dict):
    name, url, execute_times = maps_traffic.import_from_flask(**data_dict)
    scheduler.add_tasks(name, url, execute_times, SCREENSHOT_PATH)

    if not scheduler.running():
        print('[INFO] Scheduler was not running, starting thread')
        #start()


def remove(scheduler: screenshotscheduler.ScreenshotScheduler, data_dict: Dict):
    name, url, execute_times = maps_traffic.import_from_flask(**data_dict)
    scheduler.delete_tasks(name, url, execute_times, SCREENSHOT_PATH)

def start():
    threading.Thread(target=scheduler.run).start()


if __name__ == '__main__':
    main()
