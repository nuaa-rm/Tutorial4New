"""小规模多项式例子：训练点拟合好，不保证新的点也拟合好。"""
import numpy as np

x = np.array([-1., -.5, 0., .5, 1.])
y = x*x + np.array([0., .15, -.2, .15, 0.])
valid_x = np.array([-.75, -.25, .25, .75])
valid_y = valid_x * valid_x
for degree in (1, 2, 4):
    fit = np.polynomial.Polynomial.fit(x, y, degree)
    train = np.mean((fit(x) - y)**2)
    valid = np.mean((fit(valid_x) - valid_y)**2)
    print(degree, '训练MSE', float(train), '验证MSE', float(valid))
