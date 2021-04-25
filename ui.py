import datetime
import json
import socket
import sys
from urllib import request, parse

import cv2 as cv
import copy
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, \
    QLineEdit, QMessageBox
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
        self.rect = [[self.width() * 0.4, self.height() * 0.4], [self.width() * 0.6, self.height() * 0.6]]
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
        self.configure = Configure(self.width() * 0.9, self.height() * 0.3)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.video_area)
        layout.addStretch()
        layout.addWidget(self.configure)
        layout.addStretch()
        self.setLayout(layout)
        self.show()


class SingleGroup(QWidget):
    def __init__(self, width, height):
        super().__init__()
        self.setFixedSize(width, height)

        self.title = QLabel()
        self.title.setFixedSize(width * 0.8, height * 0.2)
        self.video = QLabel()
        self.video.setFixedSize(width, height * 0.7)
        self.video.setScaledContents(True)
        self.up = QPushButton()
        self.up.setText('Up')
        self.down = QPushButton()
        self.down.setText('Down')

        button_layout = QVBoxLayout()
        button_layout.addWidget(self.up)
        button_layout.addWidget(self.down)
        title_layout = QHBoxLayout()
        title_layout.addWidget(self.title)
        title_layout.addLayout(button_layout)
        layout = QVBoxLayout()
        layout.addLayout(title_layout)
        layout.addWidget(self.video)
        layout.addStretch()
        self.setLayout(layout)


class ShowBox(QWidget):
    def __init__(self, width, height):
        super().__init__()
        self.setFixedSize(width, height)
        print("show box : w {} h {}".format(self.width(), self.height()))

        self.origin = SingleGroup(self.width(), self.height() * 0.3)
        self.origin.title.setText('原图')
        self.origin.up.setVisible(False)
        self.origin.down.setVisible(False)
        self.binary = SingleGroup(self.width(), self.height() * 0.3)
        self.binary.title.setText('二值化图像，请调整阈值以正常显示数字')
        self.dilate = SingleGroup(self.width(), self.height() * 0.3)
        self.dilate.title.setText('膨胀后图像，请调整膨胀程度以使每个数字连成一个整体')
        # title = ['原图', 'R通道', '滤波', '二值化', '膨胀', '定位']
        # self.labels = []
        # for i in range(0, len(title)):
        #     self.labels.append(SingleGroup(self.width() * 0.45, self.height() * 0.3))
        #     self.labels[-1].title.setText(title[i])
        #     self.labels[-1].title.setAlignment(Qt.AlignCenter)
        #
        # layout_l = QVBoxLayout()
        # layout_r = QVBoxLayout()
        # layout_l.addStretch()
        # layout_r.addStretch()
        # for i in range(0, 3):
        #     layout_l.addWidget(self.labels[i * 2])
        #     layout_l.addStretch()
        #     layout_r.addWidget(self.labels[i * 2 + 1])
        #     layout_r.addStretch()
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.origin)
        layout.addStretch()
        layout.addWidget(self.binary)
        layout.addStretch()
        layout.addWidget(self.dilate)
        layout.addStretch()
        self.setLayout(layout)

        self.show()


number = {
    "0": [
        [0, 255, 255, 255, 0],
        [255, 0, 0, 0, 255],
        [255, 0, 0, 255, 255],
        [255, 0, 255, 0, 255],
        [255, 255, 0, 0, 255],
        [255, 0, 0, 0, 255],
        [0, 255, 255, 255, 0]
    ],
    "1": [
        [0, 0, 255, 0, 0],
        [255, 255, 255, 0, 0],
        [0, 0, 255, 0, 0],
        [0, 0, 255, 0, 0],
        [0, 0, 255, 0, 0],
        [0, 0, 255, 0, 0],
        [255, 255, 255, 255, 255]
    ],
    "2": [
        [0, 255, 255, 255, 0],
        [255, 0, 0, 0, 255],
        [0, 0, 0, 0, 255],
        [0, 0, 0, 255, 0],
        [0, 0, 255, 0, 0],
        [0, 255, 0, 0, 0],
        [255, 255, 255, 255, 255]
    ],
    "3": [
        [255, 255, 255, 255, 255],
        [0, 0, 0, 255, 0],
        [0, 0, 255, 0, 0],
        [0, 0, 0, 255, 0],
        [0, 0, 0, 0, 255],
        [255, 0, 0, 0, 255],
        [0, 255, 255, 255, 0]
    ],
    "4": [
        [0, 0, 0, 255, 0],
        [0, 0, 255, 255, 0],
        [0, 255, 0, 255, 0],
        [255, 0, 0, 255, 0],
        [255, 255, 255, 255, 255],
        [0, 0, 0, 255, 0],
        [0, 0, 0, 255, 0]
    ],
    "5": [
        [255, 255, 255, 255, 255],
        [255, 0, 0, 0, 0],
        [255, 255, 255, 255, 0],
        [0, 0, 0, 0, 255],
        [0, 0, 0, 0, 255],
        [255, 0, 0, 0, 255],
        [0, 255, 255, 255, 0]
    ],
    "6": [
        [0, 0, 255, 255, 0],
        [0, 255, 0, 0, 0],
        [255, 0, 0, 0, 0],
        [255, 255, 255, 255, 0],
        [255, 0, 0, 0, 255],
        [255, 0, 0, 0, 255],
        [0, 255, 255, 255, 0]
    ],
    "7": [
        [255, 255, 255, 255, 255],
        [0, 0, 0, 0, 255],
        [0, 0, 0, 255, 0],
        [0, 0, 255, 0, 0],
        [0, 255, 0, 0, 0],
        [0, 255, 0, 0, 0],
        [0, 255, 0, 0, 0]
    ],
    "8": [
        [0, 255, 255, 255, 0],
        [255, 0, 0, 0, 255],
        [255, 0, 0, 0, 255],
        [0, 255, 255, 255, 0],
        [255, 0, 0, 0, 255],
        [255, 0, 0, 0, 255],
        [0, 255, 255, 255, 0]
    ],
    "9": [
        [0, 255, 255, 255, 0],
        [255, 0, 0, 0, 255],
        [255, 0, 0, 0, 255],
        [0, 255, 255, 255, 255],
        [0, 0, 0, 0, 255],
        [0, 0, 0, 255, 0],
        [0, 255, 255, 0, 0]
    ]
}


def sub(a, b):
    s = 0
    for i in range(len(a)):
        for j in range(len(a[0])):
            if a[i][j] > b[i][j]:
                s += a[i][j] - b[i][j]
            else:
                s += b[i][j] - a[i][j]
    return s


def match(img):
    score = {}
    for key, val in number.items():
        score[key] = sub(val, img)
    return min(score, key=lambda x: score[x])


# order of number
def __lt__(self, y):
    if self[0] < y[0]:
        return True
    else:
        return False


class MainWindow(QWidget):
    def __init__(self, src):
        super().__init__()
        desktop = QApplication.desktop()

        self.setFixedSize(desktop.width() * 0.9, desktop.height() * 0.45)
        self.move(desktop.width() * 0.05, desktop.height() * 0.05)
        self.setWindowTitle('读数监控')
        self.setFont(QFont('Microsoft YaHei'))
        self.setStyleSheet('font:18px')
        print("main window : w {} h {}".format(self.width(), self.height()))

        self.valid_interval = [-0x3f3f3f3f, 0x3f3f3f3f]
        self.to_miao_code = []
        self.exceed_cnt = 0
        self.last_alarm_time = datetime.datetime.now() - datetime.timedelta(minutes=5)

        self.frame = None
        self.binary_threshold = 120
        self.dilate_iteration = 3

        self.cap = cv.VideoCapture(src, cv.CAP_DSHOW)
        self.timer = QTimer()

        self.timer.start(100)
        self.timer.timeout.connect(self.show_frame)

        self.video_box = VideoBox(self.width() * 0.45, self.height())
        self.show_box = ShowBox(self.width() * 0.45, self.height())
        self.show_box.binary.up.clicked.connect(self.on_binary_up_click)
        self.show_box.binary.down.clicked.connect(self.on_binary_down_click)
        self.show_box.dilate.up.clicked.connect(self.on_dilate_up_click)
        self.show_box.dilate.down.clicked.connect(self.on_dilate_down_click)

        self.layout = QHBoxLayout()
        self.layout.addWidget(self.video_box)
        self.layout.addWidget(self.show_box)
        self.setLayout(self.layout)

        self.video_box.configure.button.clicked.connect(self.on_configure_button_click)

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
        self.show_box.origin.video.setPixmap(QPixmap.fromImage(img))
        grey = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        _, binary = cv.threshold(grey, self.binary_threshold, 255, cv.THRESH_BINARY)
        img = QImage(binary.data.tobytes(), binary.shape[1], binary.shape[0], binary.shape[1], QImage.Format_Grayscale8)
        self.show_box.binary.video.setPixmap(QPixmap.fromImage(img))
        kernel = np.ones((3, 3), np.int8)
        dilate = cv.dilate(binary, kernel, iterations=self.dilate_iteration)
        img = QImage(dilate.data.tobytes(), dilate.shape[1], dilate.shape[0], dilate.shape[1], QImage.Format_Grayscale8)
        self.show_box.dilate.video.setPixmap(QPixmap.fromImage(img))

        self.show_box.update()

        contours, _ = cv.findContours(dilate, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
        bounding = []
        for c in contours:
            x, y, w, h = cv.boundingRect(c)
            if w * h * 10 > len(dilate) * len(dilate[0]) and h / w > 1:
                bounding.append([x, y, w, h])
        bounding = sorted(bounding)
        num = ""
        for b in bounding:
            rec = cv.resize(dilate[b[1]:b[1] + b[3], b[0]:b[0] + b[2]], (5, 7))
            # print(len(rec), len(rec[0]))
            num += match(rec)
        print(num)
        try:
            num = int(num)/100
        except:
            num = -0x3f3f3f3f
        self.video_box.configure.indicating_number.setText('当前读数为 ' + str(num))
        if num < self.valid_interval[0] or num > self.valid_interval[1]:
            if self.exceed_cnt > 10 and ((datetime.datetime.now() - self.last_alarm_time).seconds > 300):
                self.last_alarm_time = datetime.datetime.now()
                for dst in self.to_miao_code:
                    cur_msg = '您好：\n'
                    cur_msg += '当前示数{}已不在您的预设区间[{}, {}]\n'.format(num, self.valid_interval[0], self.valid_interval[1])
                    cur_msg += '发送自\n{}\n{}\n{}'.format(socket.gethostbyname(socket.gethostname()),
                                                        socket.gethostname(),
                                                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    page = request.urlopen('http://miaotixing.com/trigger?'
                                           + parse.urlencode({'id': dst, 'text': cur_msg, 'type': 'json'}))
                    jsonObj = json.loads(page.read())
                    if jsonObj['code'] == 0:
                        print('成功')
                    else:
                        print('失败，错误原因：{}，{}'.format(jsonObj['code'], jsonObj['msg']))
            self.exceed_cnt += 1
        else:
            self.exceed_cnt = 0

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

    def on_configure_button_click(self):
        try:
            self.valid_interval[0] = int(self.video_box.configure.itl_edit1.text())
            self.valid_interval[1] = int(self.video_box.configure.itl_edit2.text())
            self.to_miao_code = [i for i in self.video_box.configure.alter_edit.text().split(',')]
        except Exception as e:
            QMessageBox(QMessageBox.Warning, '错误', '输入参数有误！{}'.format(str(e))).exec_()
        else:
            QMessageBox(QMessageBox.Information, '通知', '已成功设置！\n有效区间[{}, {}]\n被通知人 {}'.format(
                self.valid_interval[0], self.valid_interval[1], self.to_miao_code)).exec_()

    def on_binary_up_click(self):
        if self.binary_threshold <= 245:
            self.binary_threshold += 10

    def on_binary_down_click(self):
        if self.binary_threshold >= 10:
            self.binary_threshold -= 10

    def on_dilate_up_click(self):
        if self.dilate_iteration <= 10:
            self.dilate_iteration += 1

    def on_dilate_down_click(self):
        if self.dilate_iteration >= 1:
            self.dilate_iteration -= 1

    def __del__(self):
        try:
            self.cap.release()
        except RuntimeError:
            print("capture has been released")
        try:
            self.timer.stop()
        except RuntimeError:
            print("timer has been stopped")


if __name__ == '__main__':
    main_app = QApplication(sys.argv)
    window = MainWindow(1)
    sys.exit(main_app.exec_())
