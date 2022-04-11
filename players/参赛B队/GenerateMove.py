# -*- coding:utf-8 -*-
# @Time        : 2022/1/4 14:30
# @Author      : Tuffy
# @Description :
import datetime
from time import time
from typing import List, Any, Tuple
from src import settings

# 地图的大小
from src.settings import WIN_ROWS_NUM, GAME_END_SCORE

mapWidth = settings.WIN_COLS_NUM
mapHeight = settings.WIN_ROWS_NUM
# 定义方向
UP = 1
DOWN = 2
LEFT = 3
RIGHT = 4
# 圈圈的大小
FIELD_SIZE = mapWidth * mapHeight
# 不同东西在矩阵里用不同的数字表示
FOOD = 0
FREE_PLACE = (mapWidth + 1) * (mapHeight + 1)
SNAKE_PLACE = 2 * FREE_PLACE
# 错误码
ERR = -404
# 虚拟运动运动方向字典
moveDirections = {
    'left': -1,
    'right': 1,
    'up': -mapWidth,
    'down': mapWidth
}
# 返回的字典对照
sMove = {
    'left': "L",
    'right': "R",
    'up': "U",
    'down': "D"
}
# 贪吃蛇头部下标
HEAD = 0
# 计算特殊移动位
TTG = (GAME_END_SCORE / 5) * 4
# 随特殊移动的步数
DEFAULT_TTG = 5


def fnGenerateMove(
        game_matrix: List[List[Any]],
        snack: Tuple[int, int],
        head: Tuple[int, int],
        defaultDirection: str,
        body: List[Tuple[int, int]],
        win_size: Tuple[int, int]
) -> List[str]:
    """
    生成移动路线
    Args:
        game_matrix: 游戏矩阵 List[List[int]]， 外层代表行，内层代表列 "s"代表蛇身体所在格子，0代表空白格，1代表食物
        snack: 食物坐标 (x,y)
        head: 蛇头坐标 (x,y)
        defaultDirection: 蛇移动方向 ["D","U","L","R"] 四个其中一个
        body: List[Tuple[x,y]]  整个蛇的身体坐标列表，最后一个元素为蛇头
        win_size: 游戏窗口行列数 (rows, cols)

    Returns:
        移动路线: List[str]  例如 ["U", "L", "L"]
    """
    # 画出来一维地图
    board = [0] * FIELD_SIZE
    #  开始时向右移动
    defaultDirection = RIGHT
    # 蛇的坐标
    snakeCoordinate = list()
    # 翻转转换蛇头位置, 整理出蛇在地图的所有位置
    body.reverse()
    for one in body:
        snakeCoordinate.append({"x": one[0], "y": one[1]})
    # 食物的初始坐标
    food = {"x": snack[0], "y": snack[1]}
    # 返回结果
    moveList = list()
    # 结束标识
    isOver = False
    direction_list = []
    while True:
        if isOver:
            break
        # 重置board地图
        snake_num = len(snakeCoordinate)
        reset_board = board_reset(snakeCoordinate, board, food)
        board = reset_board
        result, refresh_board = board_refresh(snakeCoordinate, food, board)
        board = refresh_board
        if result:
            if not direction_list:
                direction_list = find_safe_way(snakeCoordinate, board, food, snake_num)
            bestMove = direction_list[0]
            del direction_list[0]
            # else:
            #     bestMove = find_safe_way(snakeCoordinate, board, food)[0]
        else:
            bestMove = follow_tail(snakeCoordinate, board, food)
        if bestMove == ERR:
            bestMove = any_possible_move(snakeCoordinate, board, food)
        if bestMove != ERR:
            moveList.append(sMove.get(bestMove))
            newHead = find_snake_head(snakeCoordinate, bestMove)
            snakeCoordinate.insert(0, newHead)
            headIdx = snakeCoordinate[HEAD]['x'] + snakeCoordinate[HEAD]['y'] * mapWidth
            endIdx = snakeCoordinate[-1]['x'] + snakeCoordinate[-1]['y'] * mapWidth
            if (snakeCoordinate[HEAD]['x'] == food['x']) and (snakeCoordinate[HEAD]['y'] == food['y']):
                board[headIdx] = SNAKE_PLACE
                if len(snakeCoordinate) < FIELD_SIZE:
                    isOver = True
            else:
                board[headIdx] = SNAKE_PLACE
                board[endIdx] = FREE_PLACE
                del snakeCoordinate[-1]
    return moveList


# 各种方案均无效时，随便走一步
def any_possible_move(psnake, pboard, pfood, snake_num=None):
    bestMove = ERR
    resetBoard = board_reset(psnake, pboard, pfood)
    pboard = resetBoard
    result, refreshBoard = board_refresh(psnake, pfood, pboard)
    pboard = refreshBoard
    minDistance = SNAKE_PLACE
    for moveDirection in ['left', 'right', 'up', 'down']:
        idx = psnake[HEAD]['x'] + psnake[HEAD]['y'] * mapWidth
        if is_move_possible(idx, moveDirection) and (pboard[idx + moveDirections[moveDirection]] < minDistance):
            minDistance = pboard[idx + moveDirections[moveDirection]]
            bestMove = moveDirection
    return bestMove


# 则需要找一条安全的路径
def find_safe_way(psnake, pboard, pfood, snake_num=None):
    safeMove = ERR
    realSnake = psnake[:]
    realBoard = pboard[:]
    vPsnake, vPboard, direction_list = virtual_move(psnake, pboard, pfood)         # 耗时最多
    # 如果虚拟运行后，蛇头蛇尾间有通路，则选最短路运行
    if is_tail_inside(vPsnake, vPboard, pfood):
        safeMove = choose_shortest_safe_move(realSnake, realBoard)
        direction_list.append(safeMove)
        # if snake_num in [80,85,89]:
        #     print(f"snake_numsnake_numsnake_numsnake_numsnake_numsnake_num:{snake_num}")
        #     # safeMove = follow_tail(realSnake, realBoard, pfood)
        #     direction_list = [safeMove]
            # return direction_list
        if snake_num and snake_num > TTG:
            for i in range(DEFAULT_TTG):
                bestMove = follow_tail(vPsnake, vPboard, pfood)
                # print(f"bestMovebestMovebestMovebestMovebestMovebestMovebestMove:{bestMove}")
                direction_list.append(bestMove)
    else:
        safeMove = follow_tail(realSnake, realBoard, pfood)
        direction_list = [safeMove]
    return direction_list


# 让蛇头朝着蛇尾运行一步
def follow_tail(psnake, pboard, pfood):
    tempSnake = psnake[:]
    tempBoard = board_reset(tempSnake, pboard, pfood)
    # 将蛇尾看作食物
    endIdx = tempSnake[-1]['x'] + tempSnake[-1]['y'] * mapWidth
    tempBoard[endIdx] = FOOD
    vFood = tempSnake[-1]
    # 食物看作蛇身
    pfoodIdx = pfood['x'] + pfood['y'] * mapWidth
    tempBoard[pfoodIdx] = SNAKE_PLACE
    # 计算每个位置到蛇尾的长度
    result, refreshTboard = board_refresh(tempSnake, vFood, tempBoard)
    tempBoard = refreshTboard
    # 还原
    tempBoard[endIdx] = SNAKE_PLACE
    return choose_longest_safe_move(tempSnake, tempBoard)


def choose_longest_safe_move(psnake, pboard):
    bestMove = ERR
    maxDistance = -1
    for moveDirection in ['left', 'right', 'up', 'down']:
        idx = psnake[HEAD]['x'] + psnake[HEAD]['y'] * mapWidth
        if is_move_possible(idx, moveDirection) and (
                pboard[idx + moveDirections[moveDirection]] > maxDistance) and (
                pboard[idx + moveDirections[moveDirection]] < FREE_PLACE):
            maxDistance = pboard[idx + moveDirections[moveDirection]]
            bestMove = moveDirection
    return bestMove


# 防止蛇进入死路
def is_tail_inside(psnake, pboard, pfood):
    tempBoard = pboard[:]
    tempSnake = psnake[:]
    # 将蛇尾看作食物
    endIdx = tempSnake[-1]['x'] + tempSnake[-1]['y'] * mapWidth
    tempBoard[endIdx] = FOOD
    vFood = tempSnake[-1]
    # 食物看作蛇身(重复赋值了)
    pfoodIdx = pfood['x'] + pfood['y'] * mapWidth
    tempBoard[pfoodIdx] = SNAKE_PLACE
    # 求得每个位置到蛇尾的路径长度
    result, refreshTboard = board_refresh(tempSnake, vFood, tempBoard)
    tempBoard = refreshTboard
    for move_direction in ['left', 'right', 'up', 'down']:
        idx = tempSnake[HEAD]['x'] + tempSnake[HEAD]['y'] * mapWidth
        endIdx = tempSnake[-1]['x'] + tempSnake[-1]['y'] * mapWidth
        if is_move_possible(idx, move_direction) and (idx + moveDirections[move_direction] == endIdx) and (
                len(tempSnake) > 3):
            result = False
    return result


# 虚拟地运行,确认路线
def virtual_move(psnake, pboard, pfood):
    tempSnake = psnake[:]
    tempBoard = pboard[:]
    resetTboard = board_reset(tempSnake, tempBoard, pfood)
    tempBoard = resetTboard
    foodEated = False

    ss = 0
    direction_list = []
    while not foodEated:
        refresh_tboard = board_refresh(tempSnake, pfood, tempBoard)[1]
        tempBoard = refresh_tboard

        moveDirection = choose_shortest_safe_move(tempSnake, tempBoard)

        direction_list.append(moveDirection)   # todo

        snakeCoords = tempSnake[:]
        tempSnake.insert(0, find_snake_head(snakeCoords, moveDirection))

        cc = time()
        # 如果新的蛇头正好是食物的位置
        if tempSnake[HEAD] == pfood:
            resetTboard = board_reset(tempSnake, tempBoard, pfood)
            tempBoard = resetTboard
            pfoodIdx = pfood['x'] + pfood['y'] * mapWidth
            tempBoard[pfoodIdx] = SNAKE_PLACE
            foodEated = True
        else:
            newHeadIdx = tempSnake[0]['x'] + tempSnake[0]['y'] * mapWidth
            tempBoard[newHeadIdx] = SNAKE_PLACE
            endIdx = tempSnake[-1]['x'] + tempSnake[-1]['y'] * mapWidth
            tempBoard[endIdx] = FREE_PLACE
            del tempSnake[-1]
    # print(f"direction_list：{direction_list}")
    return tempSnake, tempBoard, direction_list


def find_snake_head(snake_Coords, direction):
    if direction == 'up':
        newHead = {'x': snake_Coords[HEAD]['x'],
                   'y': snake_Coords[HEAD]['y'] - 1}
    elif direction == 'down':
        newHead = {'x': snake_Coords[HEAD]['x'],
                   'y': snake_Coords[HEAD]['y'] + 1}
    elif direction == 'left':
        newHead = {'x': snake_Coords[HEAD]['x'] - 1,
                   'y': snake_Coords[HEAD]['y']}
    elif direction == 'right':
        newHead = {'x': snake_Coords[HEAD]['x'] + 1,
                   'y': snake_Coords[HEAD]['y']}
    return newHead


def choose_shortest_safe_move(psnake, pboard):
    bestMove = ERR
    minDistance = SNAKE_PLACE
    for move_direction in ['left', 'right', 'up', 'down']:
        idx = psnake[HEAD]['x'] + psnake[HEAD]['y'] * mapWidth
        if is_move_possible(idx, move_direction) and (pboard[idx + moveDirections[move_direction]] < minDistance):
            minDistance = pboard[idx + moveDirections[move_direction]]
            bestMove = move_direction
    return bestMove


def board_refresh(psnake, pfood, pboard):
    tempBoard = pboard[:]
    pfoodIdx = pfood['x'] + pfood['y'] * mapWidth
    queue = []
    queue.append(pfoodIdx)
    inqueue = [0] * FIELD_SIZE
    found = False
    while len(queue) != 0:
        idx = queue.pop(0)
        if inqueue[idx] == 1:
            continue
        inqueue[idx] = 1
        for moveDirection in ['left', 'right', 'up', 'down']:
            if is_move_possible(idx, moveDirection):
                if (idx + moveDirections[moveDirection]) == (psnake[HEAD]['x'] + psnake[HEAD]['y'] * mapWidth):
                    found = True
                # 该点不是蛇身(食物是0才可以这样子写)
                if tempBoard[idx + moveDirections[moveDirection]] < SNAKE_PLACE:
                    if tempBoard[idx + moveDirections[moveDirection]] > tempBoard[idx] + 1:
                        tempBoard[idx + moveDirections[moveDirection]] = tempBoard[idx] + 1
                    if inqueue[idx + moveDirections[moveDirection]] == 0:
                        queue.append(idx + moveDirections[moveDirection])
    return (found, tempBoard)


# 检查位置idx是否可以向当前move方向运动
def is_move_possible(idx, move_direction):
    flag = False
    if move_direction == 'left':
        if idx % mapWidth > 0:
            flag = True
        else:
            flag = False
    elif move_direction == 'right':
        if idx % mapWidth < mapWidth - 1:
            flag = True
        else:
            flag = False
    elif move_direction == 'up':
        if idx > mapWidth - 1:
            flag = True
        else:
            flag = False
    elif move_direction == 'down':
        if idx < FIELD_SIZE - mapWidth:
            flag = True
        else:
            flag = False
    return flag


# 判断该位置是否为空
def Is_Cell_Free(idx, psnake):
    location_x = idx % mapWidth
    location_y = idx // mapWidth
    idx = {'x': location_x, 'y': location_y}
    return (idx not in psnake)


# 重置board
def board_reset(psnake, pboard, pfood):
    tempBoard = pboard[:]
    pfoodIdx = pfood['x'] + pfood['y'] * mapWidth
    for i in range(FIELD_SIZE):
        if i == pfoodIdx:
            tempBoard[i] = FOOD
        elif Is_Cell_Free(i, psnake):
            tempBoard[i] = FREE_PLACE
        else:
            tempBoard[i] = SNAKE_PLACE
    return tempBoard
