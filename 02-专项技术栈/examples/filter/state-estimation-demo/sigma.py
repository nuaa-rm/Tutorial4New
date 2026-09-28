"""缩放无迹变换；下三角 Cholesky 使用列方向。"""
import numpy as np
from linear import covariance


def sigma_points(x, P, alpha=1., beta=2., kappa=0.):
    P = covariance(P); n = len(x)
    if not np.isfinite([alpha, beta, kappa]).all() or alpha <= 0 or beta < 0:
        raise ValueError("无迹变换参数无效")
    lam = alpha**2*(n+kappa)-n
    scale = n+lam
    if scale <= 0:
        raise ValueError("n+lambda 必须为正")
    L = np.linalg.cholesky(scale*P)
    points = np.vstack([x, x+L.T, x-L.T])
    wm = np.full(2*n+1, 1/(2*scale)); wm[0] = lam/scale
    wc = wm.copy(); wc[0] += 1-alpha**2+beta
    return points, wm, wc


def moments(points, wm, wc):
    mean = wm @ points
    errors = points-mean
    P = np.einsum("i,ij,ik->jk", wc, errors, errors)
    return mean, covariance(P)
