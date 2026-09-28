"""两个有限事件，模拟丢确认与重试；不是生产级可靠投递服务。"""
from queue import Queue, Full

pending = Queue(maxsize=2)
pending.put_nowait((1, "buy"))
pending.put_nowait((2, "buy"))
try:
    pending.put_nowait((3, "buy"))
except Full:
    print("队列已满，第三个事件明确拒绝，交给上层处理")

executed = {}
def receive(event):
    sequence, action = event
    if sequence in executed:
        assert executed[sequence] == action
        return sequence  # 同号重试只回确认，不重复执行
    assert len(executed) < 2  # 此次实验只有两个事件
    executed[sequence] = action
    print("实际执行事件", sequence, action)
    return sequence

while not pending.empty():
    event = pending.get_nowait()
    for attempt in range(1, 4):
        acknowledgment = receive(event)
        if event[0] == 1 and attempt == 1:
            acknowledgment = None  # 模拟第一次确认丢失
        print("事件", event[0], "发送次数", attempt, "确认", acknowledgment)
        if acknowledgment == event[0]:
            pending.task_done()
            break
    else:
        raise RuntimeError("三次未确认，报告投递失败，不能假装已完成")
assert executed == {1: "buy", 2: "buy"}
print("两次购买各执行一次，状态覆盖槽不能代替事件队列")
