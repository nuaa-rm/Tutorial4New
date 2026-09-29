"""先核对投影、尺寸变换、刚体逆和位姿方向。"""
import json
import numpy as np
from model import K, pose, transform, project

point = np.array([[.2, .1, 2.]])
pixel = project(point, np.eye(4))
far = project(point*np.array([1., 1., 2.]), np.eye(4))
resized = K.copy(); resized[:2] *= .5
crop = resized.copy(); crop[0, 2] -= 20
assert np.allclose(pixel, [[400, 280]])
assert np.allclose(far, [[360, 260]])
T = pose([0., 0., np.pi/2], [1., 0., 0.])
p = np.array([[0., 2., 3.]])
q = transform(p, T)
inverse = np.eye(4); inverse[:3, :3] = T[:3, :3].T
inverse[:3, 3] = -T[:3, :3].T @ T[:3, 3]
assert np.allclose(q, [[-1, 0, 3]]) and np.allclose(transform(q, inverse), p)
print(json.dumps({"pixel": pixel.tolist(), "double_depth": far.tolist(),
    "half_size": project(point, np.eye(4), resized).tolist(),
    "crop_left20": project(point, np.eye(4), crop).tolist(),
    "transformed": q.tolist(), "camera_center": inverse[:3, 3].tolist()}))
