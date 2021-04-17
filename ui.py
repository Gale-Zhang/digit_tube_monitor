import sys
import cv2 as cv
import copy
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QLineEdit
from PyQt5.QtCore import QTimer, QRect, Qt
from PyQt5.QtGui import QImage, QPixmap, QPainter, QPen, QFont
import numpy as np


class Configure(QWidget):
    def __init__(self, width, height):
        super().__init__()
        self.setFixedSize(width, height)
        print("configure : w {} h {}".format(self.width(), self.height()))

        self.indicating_number = QLabel('当前读数为 null')
        self.indicating_number.setStyleSheet('font:40px')
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

        line1_layout = QHBoxLayout()
        line1_layout.addWidget(self.itl_1)
        line1_layout.addWidget(self.itl_edit1)
        line1_layout.addWidget(self.itl_2)
        line1_layout.addWidget(self.itl_edit2)
        line1_layout.addWidget(self.itl_3)
        line1_layout.addStretch()
        line2_layout = QHBoxLayout()
        line2_layout.addWidget(self.alter_1)
        line2_layout.addWidget(self.alter_2)
        line2_layout.addWidget(self.alter_edit)
        line3_layout = QHBoxLayout()
        line3_layout.addStretch()
        line3_layout.addWidget(self.button)
        line3_layout.addStretch()
        layout = QVBoxLayout()
        layout.addWidget(self.indicating_number)
        layout.addStretch()
        layout.addLayout(line1_layout)
        layout.addLayout(line2_layout)
        layout.addLayout(line3_layout)
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
        self.video_area = VideoArea(self.width() * 0.9, self.height() * 0.5)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.video_area)
        layout.addStretch()
        layout.addWidget(Configure(self.width() * 0.9, self.height() * 0.3))
        layout.addStretch()
        self.setLayout(layout)
        self.show()


class SingleGroup(QWidget):
    def __init__(self, width, height):
        super().__init__()
        self.setFixedSize(width, height)

        self.title = QLabel()
        self.title.setFixedSize(width, height * 0.2)
        self.video = QLabel()
        self.video.setFixedSize(width, height * 0.7)
        self.video.setScaledContents(True)

        layout = QVBoxLayout()
        layout.addWidget(self.title)
        layout.addWidget(self.video)
        layout.addStretch()
        self.setLayout(layout)


class ShowBox(QWidget):
    def __init__(self, width, height):
        super().__init__()
        self.setFixedSize(width, height)
        print("show box : w {} h {}".format(self.width(), self.height()))

        title = ['原图', 'R通道', '滤波', '二值化', '膨胀', '定位']
        self.labels = []
        for i in range(0, len(title)):
            self.labels.append(SingleGroup(self.width() * 0.45, self.height() * 0.3))
            self.labels[-1].title.setText(title[i])
            self.labels[-1].title.setAlignment(Qt.AlignCenter)

        layout_l = QVBoxLayout()
        layout_r = QVBoxLayout()
        layout_l.addStretch()
        layout_r.addStretch()
        for i in range(0, 3):
            layout_l.addWidget(self.labels[i*2])
            layout_l.addStretch()
            layout_r.addWidget(self.labels[i*2+1])
            layout_r.addStretch()
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addLayout(layout_l)
        layout.addStretch()
        layout.addLayout(layout_r)
        layout.addStretch()
        self.setLayout(layout)

        self.show()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        desktop = QApplication.desktop()

        self.setFixedSize(desktop.width() * 0.9, desktop.height() * 0.45)
        self.move(desktop.width() * 0.05, desktop.height() * 0.01)
        self.setWindowTitle('读数监控')
        self.setFont(QFont('Microsoft YaHei'))
        self.setStyleSheet('font:18px')
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
        self.show_box.labels[0].video.setPixmap(QPixmap.fromImage(img))
        # red
        rch = frame[:, :, 0]
        img = QImage(rch.data.tobytes(), rch.shape[1], rch.shape[0], rch.shape[1], QImage.Format_Grayscale8)
        cv.imwrite('test.jpg', rch)
        self.show_box.labels[1].video.setPixmap(QPixmap.fromImage(img))
        # blur
        blr = cv.medianBlur(rch, 3)
        img = QImage(blr.data.tobytes(), blr.shape[1], blr.shape[0], blr.shape[1], QImage.Format_Grayscale8)
        self.show_box.labels[2].video.setPixmap(QPixmap.fromImage(img))
        # binary
        _, bny = cv.threshold(rch, 230, 255, cv.THRESH_BINARY)
        img = QImage(bny.data.tobytes(), bny.shape[1], bny.shape[0], bny.shape[1], QImage.Format_Grayscale8)
        self.show_box.labels[3].video.setPixmap(QPixmap.fromImage(img))
        # dilate
        kernel = np.ones((3, 3), np.int8)
        dil = cv.dilate(bny, kernel, iterations=5)
        img = QImage(dil.data.tobytes(), dil.shape[1], dil.shape[0], dil.shape[1], QImage.Format_Grayscale8)
        self.show_box.labels[4].video.setPixmap(QPixmap.fromImage(img))
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
        self.show_box.labels[5].video.setPixmap(QPixmap.fromImage(img))
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
