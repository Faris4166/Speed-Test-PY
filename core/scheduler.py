import threading
import time


class AutoScheduler:
    def __init__(self, interval_sec, callback):
        self.interval = interval_sec
        self.callback = callback
        self.running = False
        self.thread = None

    def start(self):
        if self.running:
            return
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False

    def _loop(self):
        while self.running:
            time.sleep(self.interval)
            if not self.running:
                break
            self.callback()
