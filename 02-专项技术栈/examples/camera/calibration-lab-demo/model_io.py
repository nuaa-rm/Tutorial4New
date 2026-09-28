"""保存 ROS 标定 YAML；它不是节点参数文件。"""
from pathlib import Path
import cv2
import numpy as np
import yaml


def save_yaml(path, K, D, size, name="front"):
    R = np.eye(3)
    new_K, _ = cv2.getOptimalNewCameraMatrix(K, D, tuple(size), 0., tuple(size))
    P = np.column_stack((new_K, np.zeros(3)))
    save_matrices(path, K, D, R, P, size, name)


def save_matrices(path, K, D, R, P, size, name):
    matrix = lambda a: {"rows": a.shape[0], "cols": a.shape[1],
                         "data": a.reshape(-1).tolist()}
    data = {"image_width": int(size[0]), "image_height": int(size[1]),
            "camera_name": name, "distortion_model": "plumb_bob",
            "camera_matrix": matrix(K), "distortion_coefficients": matrix(D.reshape(1, 5)),
            "rectification_matrix": matrix(R), "projection_matrix": matrix(P)}
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(yaml.safe_dump(data, sort_keys=False))
    temporary.replace(path)


def load_yaml(path):
    data = yaml.safe_load(Path(path).read_text())
    K = np.array(data["camera_matrix"]["data"]).reshape(3, 3)
    D = np.array(data["distortion_coefficients"]["data"])
    R = np.array(data["rectification_matrix"]["data"]).reshape(3, 3)
    P = np.array(data["projection_matrix"]["data"]).reshape(3, 4)
    size = (data["image_width"], data["image_height"])
    if data["distortion_model"] != "plumb_bob" or len(D) != 5:
        raise ValueError("本项目只接收五参数 plumb_bob")
    if min(size) <= 0 or K[0, 0] <= 0 or K[1, 1] <= 0:
        raise ValueError("尺寸或焦距无效")
    if not all(np.isfinite(a).all() for a in (K, D, R, P)):
        raise ValueError("参数含非有限值")
    return K, D, R, P, size
