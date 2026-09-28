"""保存 .npy 及元数据；哈希仅检查文件一致性，不认证发送者。"""
import hashlib
import json
from pathlib import Path
import numpy as np


def save_record(folder, iq, metadata):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    data = folder / "iq.npy"
    iq = iq.astype(np.complex64)
    np.save(data, iq, allow_pickle=False)
    metadata = dict(metadata, sample_count=len(iq), dtype=iq.dtype.str,
                    sha256=hashlib.sha256(data.read_bytes()).hexdigest())
    (folder / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n")


def load_record(folder):
    folder = Path(folder)
    metadata = json.loads((folder / "metadata.json").read_text())
    data = folder / "iq.npy"
    if hashlib.sha256(data.read_bytes()).hexdigest() != metadata["sha256"]:
        raise ValueError("IQ 文件哈希不符")
    iq = np.load(data, allow_pickle=False)
    if (iq.ndim != 1 or iq.dtype.str != metadata["dtype"]
            or iq.dtype.kind != "c" or iq.dtype.itemsize != 8
            or len(iq) != metadata["sample_count"]):
        raise ValueError("IQ 形状、类型或数量与约定不符")
    if metadata["sample_rate_hz"] <= 0 or not np.isfinite(iq).all():
        raise ValueError("采样率或样本数值无效")
    return iq, metadata
