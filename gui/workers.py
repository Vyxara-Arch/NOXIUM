from PyQt6.QtCore import QThread, pyqtSignal


class TaskWorker(QThread):
    finished = pyqtSignal(object)

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            res = self.func(*self.args, **self.kwargs)
            self.finished.emit((True, res))
        except Exception as e:
            self.finished.emit((False, str(e)))
