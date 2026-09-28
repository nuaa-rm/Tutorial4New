"""逻辑时间模拟两链路，故障时另一条继续消费，不是实机吞吐测试。"""
import socket
from state import Session

left_tx, left_rx = socket.socketpair()
right_tx, right_rx = socket.socketpair()
with left_tx, left_rx, right_tx, right_rx:
    left, right = Session(), Session()
    a, b = left.connect(left_tx), right.connect(right_tx)
    for second in range(6):
        if second not in [2, 3, 4]:
            left.put(a, "position", 10 + second, at=second)
        right.put(b, "position", 100 + second, at=second)
        item = right.take(b, now=second, max_age=2)
        assert item == ("position", 100 + second)
        print("模拟秒", second, "B 消费", item[1], "A 槽数", len(left.slots))
        if second == 4:
            assert left.take(a, now=second, max_age=2) is None
            assert left.expired == 1
            print("A 过期丢弃:", left.expired, "，此时采用 B 的新值")
    assert left.take(a, now=5, max_age=2) == ("position", 15)
    print("A 恢复，消费 15；两条链路各自维护代次和槽位")
    left.disconnect(a)
    right.disconnect(b)
