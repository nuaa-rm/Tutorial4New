"""生成小地图，并比较四邻接栅格上的 Dijkstra 与 A*。"""
import argparse
import heapq
import json
import math
from pathlib import Path
import numpy as np
from scipy.ndimage import distance_transform_edt


def cell_center(i, j, resolution, origin):
    x, y = (i+.5)*resolution, (j+.5)*resolution
    ox, oy, yaw = origin
    return (ox+math.cos(yaw)*x-math.sin(yaw)*y,
            oy+math.sin(yaw)*x+math.cos(yaw)*y)


def shortest(graph, start, goal, heuristic=lambda node: 0):
    distance, parent, queue = {start: 0}, {}, [(heuristic(start), 0, start)]
    expanded = 0
    while queue:
        _, cost, node = heapq.heappop(queue)
        if cost != distance[node]:
            continue
        expanded += 1
        if node == goal:
            path = [goal]
            while path[-1] != start:
                path.append(parent[path[-1]])
            return list(reversed(path)), cost, expanded
        for other, weight in graph(node):
            if not math.isfinite(weight) or weight < 0:
                raise ValueError("边权必须有限且非负")
            candidate = cost+weight
            if candidate < distance.get(other, math.inf):
                distance[other], parent[other] = candidate, node
                heapq.heappush(queue, (candidate+heuristic(other), candidate, other))
    return [], None, expanded


def make_map():
    # 数组第0行对应地图的最小y；保存图像时再上下翻转。
    occupied = np.zeros((40, 60), dtype=bool)
    occupied[[0, -1], :] = True
    occupied[:, [0, -1]] = True
    occupied[10:30, 27:33] = True
    return occupied


def plan(occupied, margin, astar=True):
    clearance = distance_transform_edt(~occupied)*.1
    blocked = clearance <= margin
    start, goal = (5, 5), (50, 30)
    if blocked[start[1], start[0]] or blocked[goal[1], goal[0]]:
        return [], None, 0
    def graph(node):
        i, j = node
        for x, y in ((i+1, j), (i-1, j), (i, j+1), (i, j-1)):
            if 0 <= x < 60 and 0 <= y < 40 and not blocked[y, x]:
                yield (x, y), 1
    heuristic = lambda n: abs(n[0]-goal[0])+abs(n[1]-goal[1])
    return shortest(graph, start, goal, heuristic if astar else lambda n: 0)


if __name__ == "__main__":
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("--margin", type=float, default=.35)
    cli.add_argument("--blocked", action="store_true")
    cli.add_argument("--output", type=Path, default=Path("out/map"))
    args = cli.parse_args()
    if not math.isfinite(args.margin) or args.margin < 0:
        cli.error("margin必须有限且非负")
    occupied = make_map()
    if args.blocked:
        occupied[:, 30] = True
    args.output.mkdir(parents=True, exist_ok=True)
    pixels = np.flipud(np.where(occupied, 0, 254)).astype(np.uint8)
    (args.output/"map.pgm").write_bytes(b"P5\n60 40\n255\n"+pixels.tobytes())
    (args.output/"map.yaml").write_text(
        "image: map.pgm\nmode: trinary\nresolution: 0.1\n"
        "origin: [0.0, 0.0, 0.0]\nnegate: 0\n"
        "occupied_thresh: 0.65\nfree_thresh: 0.25\n")
    results = {name: plan(occupied, args.margin, use_astar)
               for name, use_astar in (("dijkstra", False), ("astar", True))}
    np.savez(args.output/"grid.npz", occupied=occupied)
    (args.output/"paths.json").write_text(json.dumps(results))
    print(json.dumps({k: {"cost": v[1], "expanded": v[2], "cells": len(v[0])}
                      for k, v in results.items()}))
