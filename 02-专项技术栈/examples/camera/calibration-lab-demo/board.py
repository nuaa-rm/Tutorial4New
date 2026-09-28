"""统一板参数；9×6 内角点对应 10×7 个方格。"""
import cv2
import numpy as np

PATTERN = (9, 6)
SQUARE = 0.025
SIZE = (640, 480)


def object_points(square=SQUARE):
    points = np.zeros((54, 3), np.float32)
    points[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2) * square
    return points


def detect(image):
    if image is None:
        raise ValueError("图像读取失败")
    ok, points = cv2.findChessboardCorners(image, PATTERN)
    if not ok:
        return None
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    return cv2.cornerSubPix(image, points, (5, 5), (-1, -1), criteria)
