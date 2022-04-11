# -*- coding:utf-8 -*-
# @Time        : 2022/1/4 14:30
# @Author      : Tuffy
# @Description : 生成食物坐标 (x,y)

import math
import random
from typing import Tuple, Any, List


def fnGenerateSnack(
        game_matrix: List[List[Any]],
        head: Tuple[int, int],
        direction: str,
        body: List[Tuple[int, int]],
        win_size: Tuple[int, int]
) -> Tuple[int, int]:
    """
    生成食物
    Args:
        game_matrix: 游戏矩阵 List[List[int]]， 外层代表行，内层代表列 "s"代表蛇身体所在格子，0代表空白格，1代表食物
        head: 蛇头坐标 (x,y)
        direction: 蛇移动方向 ["D","U","L","R"] 四个其中一个
        body: List[Tuple[x,y]]  整个蛇的身体坐标列表，最后一个元素为蛇头
        win_size: 游戏窗口行列数 (rows, cols)

    Returns:
        食物坐标: (x, y)
    """
    # 获取游戏矩阵中心点坐标 (x,y)
    center_coordinates: Tuple[int, int] = (math.ceil(win_size[0] / 2), math.ceil(win_size[-1] / 2))

    # 计算蛇头与坐标轴中心点的差值
    point_differ: Tuple[int, int] = (head[0] - center_coordinates[0], head[1] - center_coordinates[1])
    if sum(point_differ) == 0:
        # 蛇头就在中心点，计算蛇尾点坐标 (x,y)
        point_differ: Tuple[int, int] = (body[0][0] - center_coordinates[0], body[0][1] - center_coordinates[1])

    _x = win_size[-1] - 1 if point_differ[0] <= 0 else 0
    _y = win_size[0] - 1 if point_differ[-1] <= 0 else 0

    if (_x, _y) not in body:
        return _x, _y

    # 如果极点坐标在蛇身体里，就随机选个点
    empty_points = {(x, y) for x in range(win_size[0]) for y in range(win_size[-1])} - set(body)

    if empty_points:
        return list(empty_points)[random.randint(0, len(empty_points) - 1)]
    else:
        # 没有空点了
        return body[0]
