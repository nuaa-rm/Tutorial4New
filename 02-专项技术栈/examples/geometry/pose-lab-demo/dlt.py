"""已知内参的归一化DLT；本章只接受至少六个非共面对应。"""
import cv2
import numpy as np

def normalize(points):
    center = points.mean(axis=0)
    scale = np.sqrt(points.shape[1])/np.sqrt(np.mean(np.sum((points-center)**2, axis=1)))
    T = np.eye(points.shape[1]+1)
    T[:-1, :-1] *= scale; T[:-1, -1] = -scale*center
    return (points-center)*scale, T

def rotation_projection(M):
    U, _, Vt = np.linalg.svd(M)
    return U @ np.diag([1., 1., np.linalg.det(U @ Vt)]) @ Vt

def solve(points, pixels, K, distortion=None):
    points = np.asarray(points, float); pixels = np.asarray(pixels, float)
    if len(points) < 6 or len(pixels) != len(points):
        raise ValueError("至少六组对应点")
    if np.linalg.matrix_rank(points-points.mean(axis=0)) < 3:
        raise ValueError("本DLT示例不接受共面或共线点")
    uv = cv2.undistortPoints(pixels.reshape(-1, 1, 2), K, distortion).reshape(-1, 2)
    p, N3 = normalize(points); uv, N2 = normalize(uv)
    homogeneous = np.column_stack([p, np.ones(len(p))])
    rows = []
    for P, (u, v) in zip(homogeneous, uv):
        rows.extend([np.r_[P, np.zeros(4), -u*P],
                     np.r_[np.zeros(4), P, -v*P]])
    A = np.array(rows)
    if np.linalg.matrix_rank(A) < 11:
        raise ValueError("DLT约束不足")
    _, _, Vt = np.linalg.svd(A)
    M = np.linalg.solve(N2, Vt[-1].reshape(3, 4)) @ N3
    if np.linalg.det(M[:, :3]) < 0: M = -M
    scale = np.linalg.svd(M[:, :3], compute_uv=False).mean()
    T = np.eye(4); T[:3, :3] = rotation_projection(M[:, :3]/scale)
    T[:3, 3] = M[:, 3]/scale
    return T
