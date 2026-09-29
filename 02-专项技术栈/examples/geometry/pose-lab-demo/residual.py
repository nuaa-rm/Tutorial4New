"""无畸变的像素残差 z-project；雅可比匹配左乘六维扰动。"""
import numpy as np
from model import K, transform, project
from lie import hat

def residual(points, observed, T):
    return observed-project(points, T)

def jacobians(point, T):
    X, Y, Z = transform(np.asarray(point)[None, :], T)[0]
    if Z <= 0: raise ValueError("雅可比点须在相机前方")
    Jpi = np.array([[K[0, 0]/Z, 0, -K[0, 0]*X/Z**2],
                    [0, K[1, 1]/Z, -K[1, 1]*Y/Z**2]])
    return (-Jpi @ np.column_stack([np.eye(3), -hat([X, Y, Z])]),
            -Jpi @ T[:3, :3])
