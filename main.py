import cv2
import sys
from PyQt5.QtWidgets import  QPushButton, QWidget, QLabel, QApplication
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap

class Thread(QThread):
    changePixmap = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        while True:
            ret, frame = cap.read()
            if ret:
                rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                detected_faces = face_cascade.detectMultiScale(image=rgbImage, scaleFactor=1.3, minNeighbors=4)
                self.draw_found_faces(detected_faces, rgbImage, (255, 0, 255))
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                
                self.changePixmap.emit(p)

    def draw_found_faces(self, detected, image, color: tuple):
        for (x, y, width, height) in detected:
            cv2.rectangle(
                image,
                (x, y),
                (x + width, y + height),
                color,
                thickness=3
            )


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("opredelitel' ebl")
        self.setFixedSize(640, 530)
        self.startBtn = QPushButton("Start", self)
        self.startBtn.move(10, 500)
        self.stopBtn = QPushButton("Stop", self)
        self.stopBtn.move(555, 500)
        self.startBtn.clicked.connect(self.start)
        self.stopBtn.clicked.connect(self.stop)
        self.label = QLabel(self)
        self.label.resize(640, 480)
        self.thread = Thread(self)

    @pyqtSlot(QImage)
    def setImage(self, image):
        self.label.setPixmap(QPixmap.fromImage(image))

    def start(self):
        self.thread.changePixmap.connect(self.setImage)
        self.thread.start()

    def stop(self):
        self.thread.terminate()
        self.label.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())