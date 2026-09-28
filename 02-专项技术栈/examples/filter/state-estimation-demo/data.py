"""已知真值的分段加速轨迹；不是实车传感器采集。"""
import numpy as np


def generate(steps, dt, seed, bias):
    rng = np.random.default_rng(seed)
    F = np.array([[1., dt], [0., 1.]])
    G = np.array([.5*dt**2, dt])
    x = np.array([1., .3]); truth = []
    for i in range(steps):
        a = .7 if steps//3 <= i < 2*steps//3 else 0.
        x = F @ x+G*a
        truth.append(x.copy())
    truth = np.array(truth)
    noise = rng.normal(0, .2, steps)
    position = truth[:, 0]+noise+bias
    distance = np.hypot(truth[:, 0], 2.)+noise+bias
    return truth, position, distance, F, G
