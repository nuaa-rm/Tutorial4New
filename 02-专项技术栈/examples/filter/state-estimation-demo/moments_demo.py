"""重建相关协方差、检验线性传播及非线性近似的边界。"""
import json
import numpy as np
from sigma import sigma_points, moments

x = np.array([1., 2.]); P = np.array([[1., .3], [.3, .5]])
points, wm, wc = sigma_points(x, P)
mean, rebuilt = moments(points, wm, wc)
assert np.allclose(mean, x) and np.allclose(rebuilt, P)
A = np.array([[2., 1.], [-1., .5]]); b = np.array([1., -2.])
after, propagated = moments(points @ A.T+b, wm, wc)
assert np.allclose(after, A @ x+b) and np.allclose(propagated, A @ P @ A.T)
# 一维均值0、方差1/3；这里使用高斯常见 beta=2，不知道输入的四阶矩。
p, m, c = sigma_points(np.zeros(1), np.array([[1/3]]))
values = p**2+p
y, V = moments(values, m, c)
rng = np.random.default_rng(42)
uniform = rng.uniform(-1, 1, 200000)
transformed = uniform**2+uniform
print(json.dumps({"reconstructed_mean": mean.tolist(), "reconstructed_P": rebuilt.tolist(),
    "affine_mean": after.tolist(), "affine_P": propagated.tolist(),
    "uniform_true_mean": 1/3, "uniform_true_variance": 19/45,
    "linearized_mean": 0., "linearized_variance": 1/3,
    "UT_mean": float(y[0]), "UT_variance": float(V[0, 0]),
    "sample_mean": float(transformed.mean()), "sample_variance": float(transformed.var())}))
