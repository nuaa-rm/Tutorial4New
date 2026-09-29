"""逐tick演示有记忆的顺序、选择和有界恢复；不是Nav2插件。"""
import argparse
import json
from collections import deque

SUCCESS, FAILURE, RUNNING = "Success", "Failure", "Running"


class Script:
    def __init__(self, name, statuses, log):
        self.name, self.statuses, self.log = name, deque(statuses), log

    def tick(self):
        status = self.statuses[0]
        if len(self.statuses) > 1:
            self.statuses.popleft()
        self.log.append([self.name, status])
        return status


class Control:
    def __init__(self, children, sequence):
        self.children, self.sequence, self.index = children, sequence, 0

    def tick(self):
        advance = SUCCESS if self.sequence else FAILURE
        while self.index < len(self.children):
            status = self.children[self.index].tick()
            if status == RUNNING:
                return RUNNING
            if status != advance:
                self.index = 0
                return status
            self.index += 1
        self.index = 0
        return advance


class Recovery:
    def __init__(self, task, actions, retries):
        self.task, self.actions, self.limit = task, actions, retries
        self.used, self.recovering = 0, False

    def tick(self):
        if not self.recovering:
            status = self.task.tick()
            if status != FAILURE or self.used == self.limit:
                return status
            self.recovering = True
        status = self.actions[self.used % len(self.actions)].tick()
        if status == FAILURE:
            return FAILURE
        if status == SUCCESS:
            self.used += 1
            self.recovering = False
        return RUNNING


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--fail", action="store_true")
    cli.add_argument("--stuck", action="store_true")
    args = cli.parse_args(); log = []
    task = Script("navigate", [FAILURE] if args.fail else
                  [FAILURE, FAILURE, SUCCESS], log)
    actions = [Script("clear", [SUCCESS], log),
               Script("wait", [RUNNING] if args.stuck else [RUNNING, SUCCESS], log)]
    root = Recovery(task, actions, retries=2)
    for ticks in range(1, 11):
        status = root.tick()
        if status != RUNNING:
            break
    if status == RUNNING:
        status = "Timeout"  # 本演示10tick预算耗尽，交给上层任务处理。
    print(json.dumps({"status": status, "retries": root.used,
                      "ticks": ticks, "log": log}))
