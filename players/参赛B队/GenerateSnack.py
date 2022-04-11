# -*- coding:utf-8 -*-
# @Time        : 2022/1/4 14:30
# @Author      : Tuffy
# @Description :
import random
import time
from typing import Tuple, Any, List
from src import settings
from src.settings import GENERATE_SNACK_TIME

hf = 4


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
    snake_head = body[-1]
    width = settings.WIN_COLS_NUM
    height = settings.WIN_ROWS_NUM
    # 检查食物的位置
    # check_snake(head)
    if len(body) >= 2 * width:
        # 找的在蛇头附近的难吃的点
        ret_body = []
        for y in range(settings.WIN_ROWS_NUM):
            temp_l = game_matrix[y].copy()
            temp_l = [str(i) for i in temp_l]
            new_str = ''.join(temp_l)
            index = new_str.find('s0s')
            if index != -1:
                ret_body.append((index + 1, y))
            # index = new_str.find('s00s')
            # if index != -1:
            #     ret_body.append((index + 1, y))
            #     ret_body.append((index + 2, y))

        location_bet_snack_and_head = {}
        for temp_snack in ret_body:
            if temp_snack[0] == snake_head[0] or temp_snack[1] == snake_head[1]:
                continue
            location = (temp_snack[0] - snake_head[0]) ** 2 + (temp_snack[1] - snake_head[1]) ** 2
            location_bet_snack_and_head[location] = temp_snack
        if location_bet_snack_and_head:
            new_list = list(location_bet_snack_and_head)
            index = new_list.index(max(new_list))
            location_key = new_list[index]
            return location_bet_snack_and_head[location_key]

    if snake_head[0] <= width / 2 and snake_head[1] <= height / 2:
        # 蛇头左上， 食物右下
        for i in range(3):
            vir_snack = (width - 1, height - 1)
            if vir_snack not in body:
                return vir_snack
    if snake_head[0] <= width / 2 and snake_head[1] > height / 2:
        # 蛇头左下， 食物右上
        vir_snack = (width - 1, 0)
        if vir_snack not in body:
            return vir_snack
    if snake_head[0] > width / 2 and snake_head[1] <= height / 2:
        # 蛇头右上， 食物左下
        vir_snack = (0, height - 1)
        if vir_snack not in body:
            return vir_snack

    if snake_head[0] > width / 2 and snake_head[1] > height / 2:
        # 蛇头右下， 食物左上
        vir_snack = (0, 0)
        if vir_snack not in body:
            return vir_snack
    # sssssssssssssss
    if snake_head[0] <= width / 2 and snake_head[1] <= height / 2:
        # 蛇头左上， 食物右下
        for i in range(3):
            vir_snack = (random.randint(int(width / hf * (hf - 1)), int(width - 1)),
                         random.randint(int(height / hf * (hf - 1)), int(height - 1)))
            if vir_snack not in body:
                return vir_snack
    if snake_head[0] <= width / 2 and snake_head[1] > height / 2:
        # 蛇头左下， 食物右上
        for i in range(3):
            vir_snack = (random.randint(int(width / hf * (hf - 1)), int(width - 1)), random.randint(0, int(height / 4)))
            if vir_snack not in body:
                return vir_snack
    if snake_head[0] > width / 2 and snake_head[1] <= height / 2:
        # 蛇头右上， 食物左下
        for i in range(3):
            vir_snack = (
            random.randint(0, int(width / hf)), random.randint(int(height / hf * (hf - 1)), int(height - 1)))
            if vir_snack not in body:
                return vir_snack
    if snake_head[0] > width / 2 and snake_head[1] > height / 2:
        # 蛇头右下， 食物左上
        for i in range(3):
            vir_snack = (random.randint(0, int(width / hf)), random.randint(0, int(height / hf)))
            if vir_snack not in body:
                return vir_snack

    while True:
        snack = (random.randint(0, width - 1), random.randint(0, height - 1))
        if snack not in body:
            return snack

def check_snake(snake):
    hahaha = (GENERATE_SNACK_TIME / 5) * 4
    time.sleep(hahaha)


def is_tail_inside(psnake, pboard, pfood):
    tempBoard = pboard[:]
    tempSnake = psnake[:]
    HEAD = 0
    mapWidth = 0
    # 将蛇尾看作食物
    vFood = tempSnake[-1]
    # 食物看作蛇身(重复赋值了)
    result = True
    tempBoard = 0
    for move_direction in ['left', 'right', 'up', 'down']:
        idx = tempSnake[0]['x'] + tempSnake[HEAD]['y'] * mapWidth
        endIdx = tempSnake[-1]['x'] + tempSnake[-1]['y'] * mapWidth
        result = False
    return result