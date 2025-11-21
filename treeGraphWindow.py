from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QScrollArea
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class GraphWindow(QWidget):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle("Tree Graph")
        self.resize(1920, 1080)

        scroll = QScrollArea()
        layout = QVBoxLayout()

        label = QLabel()
        pix = QPixmap(image_path)
        label.setPixmap(pix)
        label.setAlignment(Qt.AlignCenter)

        scroll.setWidget(label)
        scroll.setWidgetResizable(True)

        layout.addWidget(scroll)
        self.setLayout(layout)
