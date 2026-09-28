"""加性独立噪声的 UKF；先加 Q，再重新取点传播观测。"""
import numpy as np
from linear import covariance
from sigma import sigma_points, moments


def step(x, P, F, Q, z, R, observe, alpha=1.):
    points, wm, wc = sigma_points(x, P, alpha=alpha)
    propagated = points @ F.T
    prior, Pprior = moments(propagated, wm, wc)
    Pprior = covariance(Pprior+Q)
    if z is None:
        return prior, Pprior, None, None
    if not np.isfinite(R) or R <= 0:
        raise ValueError("R 为正有限方差")
    points, wm, wc = sigma_points(prior, Pprior, alpha=alpha)
    measurements = np.array([observe(point) for point in points])
    expected = float(wm @ measurements)
    dx = points-prior; dz = measurements-expected
    S = float(np.sum(wc*dz**2)+R)
    if S <= 0:
        raise ValueError("创新方差不为正")
    cross = np.sum(wc[:, None]*dx*dz[:, None], axis=0)
    K = cross/S
    residual = float(z-expected)
    posterior = prior+K*residual
    Ppost = covariance(Pprior-np.outer(K, K)*S)
    return posterior, Ppost, residual, S
