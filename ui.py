import sys
import cv2 as cv
import copy
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit
from PyQt5.QtCore import QTimer, QRect, Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen
import numpy as np


class Configure(QWidget):
    def __init__(self, width, height):
        super().__init__()
        self.setFixedSize(width, height)
        print("configure : w {} h {}".format(self.width(), self.height()))

        self.indicating_number = QLabel('当前读数为 null')
        self.itl_1 = QLabel('当读数小于')
        self.itl_edit1 = QLineEdit()
        self.itl_2 = QLabel('，或大于')
        self.itl_edit2 = QLineEdit()
        self.itl_3 = QLabel('时，发送警告')
        self.alter_1 = QLabel('被通知人喵码')
        self.alter_2 = QLabel('（多个请以英文逗号,分隔）：')
        self.alter_edit = QLineEdit()
        self.button = QPushButton()
        self.button.setText('确认')

        layout = QGridLayout()
        layout.addWidget(self.indicating_number, 0, 0, 1, 5)
        layout.addWidget(self.itl_1, 1, 0)
        layout.addWidget(self.itl_edit1, 1, 1)
        layout.addWidget(self.itl_2, 1, 2)
        layout.addWidget(self.itl_edit2, 1, 3)
        layout.addWidget(self.itl_3, 1, 4)
        layout.addWidget(self.alter_1, 2, 0)
        layout.addWidget(self.alter_2, 2, 1)
        layout.addWidget(self.alter_edit, 2, 2, 1, 3)
        layout.addWidget(self.button, 3, 0, 1, 5)
        self.setLayout(layout)
        self.show()


class VideoArea(QLabel):
    def __init__(self, width, height):
        super().__init__()
        self.setFixedSize(width, height)
        print("video area : w {} h {}".format(self.width(), self.height()))

        self.status = False
        self.rect = [[self.width()*0.4, self.height()*0.4], [self.width()*0.6, self.height()*0.6]]
        self.buf = copy.deepcopy(self.rect)

        self.setScaledContents(True)
        self.show()

    def mousePressEvent(self, event):
        self.status = True
        self.buf[0][0] = event.x()
        self.buf[0][1] = event.y()

    def mouseReleaseEvent(self, event):
        self.status = False
        if 0 < self.buf[0][0] < self.buf[1][0] < self.width() and 0 < self.buf[0][1] < \
                self.buf[1][1] < self.height():
            self.rect = self.buf
        self.buf = copy.deepcopy(self.rect)

    def mouseMoveEvent(self, event):
        if self.status:
            self.buf[1][0] = event.x()
            self.buf[1][1] = event.y()
            # print('[{}, {}],[{}, {}],[{}, {}]'.format(self.x(), self.y(), self.width(),
            #                                           self.height(), event.x(), event.y()))
            self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        rect = QRect(self.buf[0][0], self.buf[0][1], abs(self.buf[1][0] - self.buf[0][0]),
                     abs(self.buf[1][1] - self.buf[0][1]))
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 1, Qt.SolidLine))
        painter.drawRect(rect)


class VideoBox(QWidget):
    def __init__(self, width, height):
        super().__init__()
        self.setFixedSize(width, height)
        print("video box : w {} h {}".format(self.width(), self.height()))
        self.video_area = VideoArea(self.width(), self.height() * 0.5)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.video_area)
        self.layout.addWidget(Configure(self.width(), self.height() * 0.15))
        self.setLayout(self.layout)
        self.show()


class ShowBox(QWidget):
    def __init__(self, width, height):
        super().__init__()
        self.setFixedSize(width, height)
        print("show box : w {} h {}".format(self.width(), self.height()))

        title = ['原图', 'R通道', '滤波', '二值化', '膨胀', '定位']
        self.labels = []
        for i in range(0, len(title)):
            self.labels.append(QLabel(title[i]))
            self.labels[-1].setFixedSize(self.width() * 0.45, self.height() * 0.03)
            self.labels.append(QLabel())
            self.labels[-1].setFixedSize(self.width() * 0.45, self.height() * 0.20)
            self.labels[-1].setScaledContents(True)
        print("len grid: {}".format(len(self.labels)))
        layout = QGridLayout()
        for i in range(0, len(self.labels), 2):
            layout.addWidget(self.labels[i], int(i / 4) * 2, int((i % 4) / 2))
        for i in range(1, len(self.labels), 2):
            layout.addWidget(self.labels[i], int(i / 4) * 2 + 1, int(((i - 1) % 4) / 2))
        self.setLayout(layout)

        self.show()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        desktop = QApplication.desktop()

        self.setFixedSize(desktop.width() * 0.9, desktop.height() * 0.45)
        self.move(desktop.width() * 0.1, desktop.height() * 0.05)
        self.setWindowTitle('Simple')
        print("main window : w {} h {}".format(self.width(), self.height()))

        self.frame = None

        self.cap = cv.VideoCapture(1, cv.CAP_DSHOW)
        self.timer = QTimer()

        self.timer.start(100)
        self.timer.timeout.connect(self.show_frame)

        self.video_box = VideoBox(self.width() * 0.45, self.height())
        self.show_box = ShowBox(self.width() * 0.45, self.height())

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.video_box)
        self.layout.addWidget(self.show_box)
        self.setLayout(self.layout)

        self.show()

    def show_frame(self):
        ret, frame = self.cap.read()
        frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        self.frame = frame
        video_area = self.video_box.video_area
        # frame = cv.resize(frame, (video_area.width(), video_area.height()))
        img = QImage(frame.data, frame.shape[1], frame.shape[0], frame.shape[1] * 3, QImage.Format_RGB888)
        video_area.setPixmap(QPixmap.fromImage(img))
        video_area.update()

        frame = self.get_valid_img()
        img = QImage(frame.data.tobytes(), frame.shape[1], frame.shape[0], frame.shape[1] * 3, QImage.Format_RGB888)
        self.show_box.labels[1].setPixmap(QPixmap.fromImage(img))
        # red
        rch = frame[:, :, 0]
        img = QImage(rch.data.tobytes(), rch.shape[1], rch.shape[0], rch.shape[1], QImage.Format_Grayscale8)
        cv.imwrite('test.jpg', rch)
        self.show_box.labels[3].setPixmap(QPixmap.fromImage(img))
        # blur
        blr = cv.medianBlur(rch, 3)
        img = QImage(blr.data.tobytes(), blr.shape[1], blr.shape[0], blr.shape[1], QImage.Format_Grayscale8)
        self.show_box.labels[5].setPixmap(QPixmap.fromImage(img))
        # binary
        _, bny = cv.threshold(rch, 230, 255, cv.THRESH_BINARY)
        img = QImage(bny.data.tobytes(), bny.shape[1], bny.shape[0], bny.shape[1], QImage.Format_Grayscale8)
        self.show_box.labels[7].setPixmap(QPixmap.fromImage(img))
        # dilate
        kernel = np.ones((3, 3), np.int8)
        dil = cv.dilate(bny, kernel, iterations=5)
        img = QImage(dil.data.tobytes(), dil.shape[1], dil.shape[0], dil.shape[1], QImage.Format_Grayscale8)
        self.show_box.labels[9].setPixmap(QPixmap.fromImage(img))
        # detect number area
        contours, hierarchy = cv.findContours(dil, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        boundRect = []
        rec = copy.deepcopy(dil)
        for c in contours:
            x, y, w, h = cv.boundingRect(c)
            # 一个筛选，可能需要看识别条件而定，有待优化
            if h / w > 1:
                boundRect.append([x, y, w, h])
                # 画一个方形标注一下，看看圈的范围是否正确
                rec = cv.rectangle(rec, (x, y), (x + w, y + h), 255, 2)
        img = QImage(rec.data.tobytes(), rec.shape[1], rec.shape[0], rec.shape[1], QImage.Format_Grayscale8)
        self.show_box.labels[11].setPixmap(QPixmap.fromImage(img))
        self.show_box.update()

    def get_valid_img(self):
        x = self.video_box.video_area.x()
        y = self.video_box.video_area.y()
        w = self.video_box.video_area.width()
        h = self.video_box.video_area.height()
        img_w = self.frame.shape[1]
        img_h = self.frame.shape[0]
        real_x0 = int(self.video_box.video_area.rect[0][0] * img_w / w)
        real_y0 = int(self.video_box.video_area.rect[0][1] * img_h / h)
        real_x1 = int(self.video_box.video_area.rect[1][0] * img_w / w)
        real_y1 = int(self.video_box.video_area.rect[1][1] * img_h / h)
        img = copy.deepcopy(self.frame[real_y0:real_y1, real_x0:real_x1, :])
        return img

    def __del__(self):
        try:
            self.cap.release()
        except RuntimeError:
            print("capture has been released")
        try:
            self.timer.stop()
        except RuntimeError:
            print("timer has been stopped")


main_app = QApplication(sys.argv)
window = MainWindow()
sys.exit(main_app.exec_())
