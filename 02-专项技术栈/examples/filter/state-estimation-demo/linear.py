"""线性预测和 Joseph 更新；矩阵乘法不是逐元素除法。"""
import numpy as np


def covariance(P):
    P = np.asarray(P, float)
    if P.ndim != 2 or P.shape[0] != P.shape[1] or not np.isfinite(P).all():
        raise ValueError("协方差必须是有限方阵")
    if not np.allclose(P, P.T) or np.linalg.eigvalsh(P).min() < -1e-12:
        raise ValueError("协方差须对称半正定")
    return (P+P.T)/2


def predict(x, P, F, Q):
    P, Q = covariance(P), covariance(Q)
    return F @ x, covariance(F @ P @ F.T + Q)


def update(x, P, z, H, R, expected=None):
    P, R = covariance(P), covariance(np.atleast_2d(R))
    if np.linalg.eigvalsh(R).min() <= 0:
        raise ValueError("本演示要求正定观测协方差")
    residual = np.atleast_1d(z) - (H @ x if expected is None else expected)
    S = H @ P @ H.T + R
    K = np.linalg.solve(S, (P @ H.T).T).T
    A = np.eye(len(x)) - K @ H
    return x + K @ residual, covariance(A @ P @ A.T + K @ R @ K.T), residual, S
