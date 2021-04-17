import cv2 as cv
import numpy as np
from matplotlib import pyplot as plt
import copy

debug = False
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


def plot(img, place, title):
    plt.subplot(place)
    plt.imshow(img, 'gray')
    plt.title(title)


def digital_num_identify(img):
    plot(img, 231, '原图')

    # R channel
    img_red = img[:, :, 2]
    plot(img_red, 232, 'R通道')

    # blur
    blur = cv.medianBlur(img_red, 3)
    plot(blur, 233, '中值滤波')

    # binary
    _, binary = cv.threshold(img_red, 230, 255, cv.THRESH_BINARY)
    plot(binary, 234, '二值化')

    # dilate
    kernel = np.ones((3, 3), np.int8)
    dil = cv.dilate(binary, kernel, iterations=5)
    plot(dil, 235, '膨胀')

    # detect number area
    contours, hierarchy = cv.findContours(dil, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    print('轮廓：{}'.format(hierarchy))

    boundRect = []
    rec = copy.deepcopy(dil)
    for c in contours:
        x, y, w, h = cv.boundingRect(c)
        # 一个筛选，可能需要看识别条件而定，有待优化
        if h / w > 1:
            boundRect.append([x, y, w, h])
            # 画一个方形标注一下，看看圈的范围是否正确
            rec = cv.rectangle(rec, (x, y), (x + w, y + h), 255, 2)
    print('方形轮廓：{}'.format(boundRect))
    plot(rec, 236, '数字区域')

    # order of number
    def __lt__(self, y):
        if self[0] < y[0]:
            return True
        else:
            return False

    bounds = sorted(boundRect)
    num = 0
    for i in bounds:
        num = num * 10 + num_identify(dil, i)
    print(num)

    detect_comma(dil, bounds)

    detect_comma_italic(dil, bounds)

    a = detect_comma(dil, bounds)

    if a != -1:
        # 正体数字检测到小数点的情况
        num = num / pow(10, len(bounds) - a)
    else:
        # 正体无小数点或斜体数字的情况
        a = detect_comma_italic(dil, bounds)

        if a != -1:
            # 斜体数字有小数点的情况
            num = num / pow(10, len(bounds) - 1 - a)
    print(num)
    plt.show()


def num_identify(img, rec):
    x, y, w, h = rec

    if h / w > 3:
        return 1
    else:
        # 更新，改为穿针法
        line1 = img[y:y + h, x + w // 2]
        line2 = img[y + h // 4, x:x + w]
        line3 = img[y + (h // 4) * 3, x:x + w]
        # 检测竖线，从而识别a,g,d笔画
        a, b, c, d, e, f, g = 0, 0, 0, 0, 0, 0, 0
        for i in range(h):
            if line1[i] == 255:
                if i < (h // 3):
                    a = 1
                if i > 2 * (h // 3):
                    d = 1
                if (h // 3) < i < 2 * (h // 3):
                    g = 1
        # 检测横线line2、line3，从而识别b,f笔画并减少时间消耗
        for i in range(w):
            if line2[i] == 255:
                if i < (w // 2):
                    b = 1
                if i > (w // 2):
                    f = 1
            if line3[i] == 255:
                if i < (w // 2):
                    c = 1
                if i > (w // 2):
                    e = 1

        # 不写的眼花缭乱了，直接写就可以了
        if a and b and c and d and e and f and g == 0:
            return 0
        if a and b == 0 and c and d and e == 0 and f and g:
            return 2
        if a and b == 0 and c == 0 and d and e and f and g:
            return 3
        if a == 0 and b and c == 0 and d == 0 and e and f and g:
            return 4
        if a and b and c == 0 and d and e and f == 0 and g:
            return 5
        if a and b and c and d and e and f == 0 and g:
            return 6
        if a and b == 0 and c == 0 and d == 0 and e and f and g == 0:
            return 7
        if a and b and c and d and e and f and g:
            return 8
        if a and b and c == 0 and d and e and f and g:
            return 9

        return -1


def detect_comma(img, bound):
    for i in range(1, len(bound)):

        roi_x1 = bound[i - 1][0] + bound[i - 1][2]
        roi_x2 = bound[i][0]
        roi_y2 = max(bound[i - 1][1] + bound[i - 1][3], bound[i][1] + bound[i][3])
        roi_y1 = roi_y2 - max(bound[i - 1][3], bound[i][3]) // 3
        roi = img[roi_y1:roi_y2, roi_x1:roi_x2]

        contours0, hierarchy0 = cv.findContours(roi, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        boundRect0 = []
        for c in contours0:
            x, y, w, h = cv.boundingRect(c)
            # 一个筛选，可能需要看识别条件而定，有待优化——比如增加小数点的大小判断
            if 0.75 < h / w < 1.25:
                boundRect0.append([x, y, w, h])
                # 画一个方形标注一下，看看圈的范围是否正确
                red_dil = cv.rectangle(roi, (x, y), (x + w, y + h), 255, 2)

                return i

    return -1


# 斜体数字的小数点识别，在数字区域内进行boundRect识别

def detect_comma_italic(img, bounds):
    for i in range(len(bounds)):
        x, y, w, h = bounds[i]
        roi = img[y + 3 * h // 4: y + h, x + 2 * w // 3: x + w]

        contours0, hierarchy0 = cv.findContours(roi, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        boundRect0 = []
        for c in contours0:
            x, y, w, h = cv.boundingRect(c)
            # 一个筛选，可能需要看识别条件而定，有待优化——比如增加小数点的大小判断
            if 0.8 < h / w < 1.2:
                boundRect0.append([x, y, w, h])
                # 画一个方形标注一下，看看圈的范围是否正确
                red_dil = cv.rectangle(roi, (x, y), (x + w, y + h), 255, 2)

                return i

    return -1


def main():
    cap = cv.VideoCapture(1)  # 调整参数实现读取视频或调用摄像头
    while 1:
        ret, frame = cap.read()
        frame = cv.rectangle(frame, (200, 200), (400, 350), 255, 2)
        cv.imshow("cap", frame)
        # digital_num_identify(frame)
        if cv.waitKey(100) & 0xff == ord('q'):
            break
    cap.release()
    cv.destroyAllWindows()


# input_img = cv.imread('data/52.1.jpg')
# digital_num_identify(input_img)
if __name__ == '__main__':
    main()
