"""本章针孔模型：列向量变换，数组按行存点，单位米/像素。"""
import cv2
import numpy as np

K = np.array([[800., 0, 320], [0, 800, 240], [0, 0, 1]])
def pose(rotation, translation):
    T = np.eye(4)
    T[:3, :3] = cv2.Rodrigues(np.asarray(rotation, float))[0]
    T[:3, 3] = translation
    return T

def transform(points, T):
    return np.asarray(points) @ T[:3, :3].T + T[:3, 3]

def project(points, T, camera=K):
    q = transform(points, T)
    if not np.isfinite(q).all() or np.any(q[:, 2] <= 0):
        raise ValueError("投影点须在相机前方且有限")
    normalized = q/q[:, 2, None]
    return (normalized @ camera.T)[:, :2]

def sample(seed=42, count=20):
    rng = np.random.default_rng(seed)
    return rng.uniform([-.7, -.5, 3.], [.7, .5, 5.], (count, 3))
