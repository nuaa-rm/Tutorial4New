"""看定位修正如何改map->odom，以及两面无限长墙的退化。"""
import json
import numpy as np

# 只取平移便于手算；齐次矩阵的乘法与三维情形相同。
def translation(x, y):
    t = np.eye(3); t[:2, 2] = [x, y]
    return t

odom_base = translation(2, .5)
map_base = translation(2.3, .5)
map_odom = map_base @ np.linalg.inv(odom_base)
corrected = translation(2.2, .5) @ np.linalg.inv(odom_base)
# 两堵沿x无限延伸的墙，只提供y方向约束；不是完整雷达模型。
normals = np.array([[0., 1.], [0., -1.]])
hessian = normals.T @ normals
result = {"map_odom_xy": map_odom[:2, 2].tolist(),
          "corrected_xy": corrected[:2, 2].tolist(),
          "odom_base_unchanged": odom_base[:2, 2].tolist(),
          "wall_eigenvalues": np.linalg.eigvalsh(hessian).tolist(),
          "wall_shift_x_residual": (normals @ np.array([100., 0.])).tolist()}
print(json.dumps(result))
