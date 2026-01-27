import psutil
from PyQt6.QtWidgets import QFrame, QProgressBar, QLabel, QStackedWidget, QVBoxLayout
from PyQt6.QtCore import QTimer, QPropertyAnimation, QParallelAnimationGroup
from PyQt6.QtWidgets import QGraphicsOpacityEffect

class SystemMonitorWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setMinimumSize(260, 150)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        l_title = QLabel("System Vitality")
        l_title.setProperty("tone", "muted")
        l_title.setStyleSheet("font-weight: 600; font-size: 14px;")
        layout.addWidget(l_title)

        self.cpu_bar = QProgressBar()
        self.cpu_bar.setTextVisible(False)
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setFixedHeight(10)

        self.lbl_cpu = QLabel("CPU: 0%")
        self.lbl_cpu.setProperty("tone", "accent")
        self.lbl_cpu.setStyleSheet("font-size: 13px; font-weight: 600;")

        layout.addWidget(self.lbl_cpu)
        layout.addWidget(self.cpu_bar)
        layout.addSpacing(8)

        self.ram_bar = QProgressBar()
        self.ram_bar.setTextVisible(False)
        self.ram_bar.setRange(0, 100)
        self.ram_bar.setFixedHeight(10)

        self.lbl_ram = QLabel("RAM: 0%")
        self.lbl_ram.setProperty("tone", "accent-secondary")
        self.lbl_ram.setStyleSheet("font-size: 13px; font-weight: 600;")

        layout.addWidget(self.lbl_ram)
        layout.addWidget(self.ram_bar)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(2000)
        self.update_stats()

    def update_stats(self):
        try:
            c = psutil.cpu_percent()
            r = psutil.virtual_memory().percent
            self.cpu_bar.setValue(int(c))
            self.lbl_cpu.setText(f"CPU: {c}%")
            self.ram_bar.setValue(int(r))
            self.lbl_ram.setText(f"RAM: {r}%")
        except Exception:
            pass


class FadeStack(QStackedWidget):
    """Stacked widget with fade animation."""

    def __init__(self):
        super().__init__()
        self.fade_anim = None

    def on_fade_finished(self):
        self.currentWidget().setGraphicsEffect(None)
        self.setCurrentIndex(self.next_idx)
        self.widget(self.next_idx).setGraphicsEffect(None)

    def fade_to_index(self, index):
        if index == self.currentIndex():
            return

        self.next_idx = index
        current_widget = self.currentWidget()
        next_widget = self.widget(index)

        if not current_widget or not next_widget:
            self.setCurrentIndex(index)
            return

        self.eff1 = QGraphicsOpacityEffect(self)
        self.eff2 = QGraphicsOpacityEffect(self)
        current_widget.setGraphicsEffect(self.eff1)
        next_widget.setGraphicsEffect(self.eff2)

        next_widget.show()
        next_widget.raise_()

        self.anim_group = QParallelAnimationGroup()

        anim1 = QPropertyAnimation(self.eff1, b"opacity")
        anim1.setDuration(300)
        anim1.setStartValue(1)
        anim1.setEndValue(0)

        anim2 = QPropertyAnimation(self.eff2, b"opacity")
        anim2.setDuration(300)
        anim2.setStartValue(0)
        anim2.setEndValue(1)

        self.anim_group.addAnimation(anim1)
        self.anim_group.addAnimation(anim2)
        self.anim_group.finished.connect(self.on_fade_finished)
        self.anim_group.start()
