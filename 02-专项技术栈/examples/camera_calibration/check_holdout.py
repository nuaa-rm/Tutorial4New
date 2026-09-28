import cv2
import numpy as np

data = np.load("calibration.npz")
K, D = data["K"], data["dist"]
img = cv2.imread("validation.png")
if img is None:
    raise ValueError("找不到 validation.png")
size = (img.shape[1], img.shape[0])
if tuple(data["size"]) != size:
    raise ValueError("验证图与标定图分辨率不一致")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
ok, corners = cv2.findChessboardCorners(gray, (9, 6))
if not ok:
    raise ValueError("未找到完整的 9x6 内角点")
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
corners = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
obj = np.zeros((54, 3), np.float32)
obj[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2) * 0.025
ok, rvec, tvec = cv2.solvePnP(obj, corners, K, D)
if not ok:
    raise ValueError("位姿求解失败")
pred, _ = cv2.projectPoints(obj, rvec, tvec, K, D)
err = np.linalg.norm(pred.reshape(-1, 2) - corners.reshape(-1, 2), axis=1)
print("验证 RMS / pixel:", np.sqrt(np.mean(err**2)))
print("最大角点残差 / pixel:", err.max())
new_K, roi = cv2.getOptimalNewCameraMatrix(K, D, size, 1.0, size)
out = cv2.undistort(img, K, D, None, new_K)
if not cv2.imwrite("undistorted.png", out):
    raise IOError("无法保存图像")
np.savez("rectified_model.npz", K=new_K, size=size, roi=roi)
