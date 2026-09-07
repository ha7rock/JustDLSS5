"""Bounded background executor. Results are delivered on the Qt GUI thread.

Progress/log producers write a queue; a 50ms GUI timer batches updates. There
is no per-line widget repaint and no disk work in resize/paint/model callbacks.
"""
import queue
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import QObject, QTimer, Signal


class Jobs(QObject):
    completed = Signal(int, object, object)
    events = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pool = ThreadPoolExecutor(max_workers=3, thread_name_prefix="autopilot")
        self.queue = queue.Queue()
        self.next_id = 0
        self.active = set()
        self.timer = QTimer(self)
        self.timer.setInterval(50)
        self.timer.timeout.connect(self.drain)
        self.timer.start()

    def submit(self, function):
        self.next_id += 1
        job_id = self.next_id
        self.active.add(job_id)
        def execute():
            try:
                result = function(lambda kind, value: self.queue.put(("event", job_id, kind, value)))
                self.queue.put(("done", job_id, result, None))
            except Exception as error:
                self.queue.put(("done", job_id, None, (str(error), traceback.format_exc())))
        self.pool.submit(execute)
        return job_id

    def drain(self):
        batch = []
        done = []
        # A noisy backend cannot monopolize a frame.
        for _ in range(300):
            try:
                kind, job_id, value, extra = self.queue.get_nowait()
            except queue.Empty:
                break
            if kind == "done":
                done.append((job_id, value, extra))
            else:
                batch.append((job_id, value, extra))
        if batch:
            self.events.emit(batch)
        for job_id, value, error in done:
            self.active.discard(job_id)
            self.completed.emit(job_id, value, error)

    def shutdown(self):
        self.timer.stop()
        self.pool.shutdown(wait=False, cancel_futures=True)
