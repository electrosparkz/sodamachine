from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

import time
import sched
import threading


class SodaState(object):
    def __init__(self, *args, **kwargs):

        self.file_name = 'state.yaml'

        with open(self.file_name, 'r') as filehandle:
            raw_state = load(filehandle, Loader=Loader)

        self.syrup_remaining = raw_state['syrup_remaining']

        self.scheduler = sched.scheduler(time.time, time.sleep)

        self.last_state = None

        self._start_periodic_save()

    def _start_periodic_save(self, interval=5):
        def update(obj):
            obj.save_state()
            obj.scheduler.enter(interval, interval + 30, update, (obj,))

        update(self)
        update_thread = threading.Thread(target=lambda x: x.run(), args=(self.scheduler,), daemon=True)
        update_thread.start()

    def save_state(self):
        temp_state = {
            'syrup_remaining': self.syrup_remaining
        }
        print("State saved")

        if temp_state != self.last_state:
            self.last_state = temp_state
            with open(self.file_name, 'w') as fileout:
                dump(temp_state, fileout, Dumper=Dumper)
