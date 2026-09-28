"""真实 socket 对检查归属；状态覆盖与优先级使用固定时间。"""
import socket
from state import Session

session = Session()
old_tx, old_rx = socket.socketpair()
new_tx, new_rx = socket.socketpair()
with old_tx, old_rx, new_tx, new_rx:
    old_rx.settimeout(1)
    new_rx.settimeout(1)
    first = session.connect(old_tx)
    for value in [10, 20, 30]:
        session.put(first, "position", value, at=0)
    session.put(first, "status", "ready", at=0)
    assert len(session.slots) == 2
    assert session.take(first, now=0, max_age=2) == ("position", 30)
    print("优先消费最新位置: 30；剩余槽数:", len(session.slots))

    second = session.connect(new_tx)
    assert not session.slots and old_rx.recv(1) == b""
    assert not session.put(first, "position", 99, at=1)
    assert session.put(second, "position", 42, at=1)
    assert not session.disconnect(first)
    new_tx.sendall(b"ok")
    assert new_rx.recv(2) == b"ok"
    assert session.take(second, now=1, max_age=2) == ("position", 42)
    print("忽略旧代次", first, "；新代次", second, "仍能发送 ok 和位置 42")
    assert session.disconnect(second)
