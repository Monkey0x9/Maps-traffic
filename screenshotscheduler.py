import pathlib
import sched
import time
import datetime
from pathlib import Path
from typing import Dict, List, Callable


class ScreenshotScheduler:
    def __init__(self, action_funtion: Callable[[Dict, pathlib.Path, int, int], None]):
        self.plan = sched.scheduler(time.time, time.sleep)
        self.action = action_funtion
        self.queue = []
        self._running = False

    def add_tasks(self, name: str, url: str, execute_times: List[datetime.datetime], screenshot_folder: Path):
        for execute_time in execute_times:
            if execute_time > datetime.datetime.now():
                self._add_task({name: url}, execute_time, screenshot_folder)
            else:
                print(f'[WARNING]: Not add task, is in the future {execute_time}')

    def _add_task(self, locations: Dict, execute_time: datetime.datetime, save_path: Path):
        self.plan.enterabs(
            time=execute_time.timestamp(),
            priority=1,
            action=self.action,
            argument=(locations, save_path),
        )

    def running(self) -> bool:
        """Check whether the scheduler is running"""
        return self._running

    def _run(self):
        print('[INFO]: Starting the scheduler!')
        try:
            self._running = True
            self.plan.run()
        except e:
            print('[ERROR] plan.run had an exception')
            print(e)
        else:
            print('[iNFO] Scheduler is done running')
        finally:
            self._running = False
            print('[INFO] self._running is false now. Exit')


    def run(self):
        if not False:
            if not self._running:
                self._run()
            else:
                print('[WARNING] Alreay running the scheduler')
        else:
            print('[WARNING] No tasks planning, cannot run')

    def get_queue(self):
        self.queue = self.plan.queue  # buffer

    def _delete_task(self, timestamp, locations, save_path):
        for task in self.queue:
            if task.time == timestamp and task.argument == (locations, save_path):
                self.plan.cancel(task)

    def delete_tasks(self, name: str, url: str, execute_times: List[datetime.datetime], screenshot_folder: Path):
        """Looks in the queue and deletes all task that are matchin"""
        self.get_queue()  # buffer, reading from it is blocking

        for execute_time in execute_times:
            self._delete_task(execute_time.timestamp(), {name: url}, screenshot_folder)


