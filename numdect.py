import cv2 as cv
import numpy as np

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


def num_identify(img):
    # cv.imshow('test', img)
    grey = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # cv.imshow('test', grey)
    # _, binary = cv.threshold(grey, 1.4 * sum(map(sum, grey)) / (len(grey) * len(grey[0])), 255, cv.THRESH_BINARY)
    _, binary = cv.threshold(grey, 230, 255, cv.THRESH_BINARY)
    # cv.imshow('test', binary)
    kernel = np.ones((3, 3), np.int8)
    dilate = cv.dilate(binary, kernel, iterations=3)
    cv.imshow('test', dilate)
    cv.waitKey(0)
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
        num = float(num)
        return num
    except:
        print("number error")
        return -0x3f3f3f3f


if __name__ == '__main__':
    cv.namedWindow('test', cv.WINDOW_AUTOSIZE)
    imgs = ['292.99', '293.06', '300.00', '303.08', '311.15', '314.83', '345.00']
    for i in imgs:
        img = cv.imread('data/sample/' + i + '.jpg')
        num_identify(img)
    cv.waitKey(0)
