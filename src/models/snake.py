# -*- coding:utf-8 -*-
# @Time        : 2021/12/30 15:18
# @Author      : Tuffy
# @Description :  蛇 的类
from collections import deque
from typing import Tuple, List

import arrow
import pygame
from loguru import logger
from pygame import Surface

from src.tools.draws import SnakeCube
from src.tools.enums import DirectionEnum
from src.tools.exceptions import GameOverException
from src.settings import MOVE_TIME, SNAKE_COLOR, GAME_TIME, EAT_SNACK_EVENT


class Snake(object):
    def __init__(self, game_window: Surface,
                 game_matrix: List[List[int]],
                 pos: Tuple[int, int],
                 *,
                 color: Tuple[int, int, int] = SNAKE_COLOR,
                 direction: str = DirectionEnum.right.value):
        """
        蛇
        Args:
            game_window: 游戏窗口
            game_matrix: 游戏矩阵   "s"代表蛇的身体  0代表空白格子  1代表食物
            color: 蛇的颜色 (r,g,b)
            pos: 蛇的初始坐标 (x, y)
            direction: 蛇初始的运动方向，枚举类型DirectionEnum，值包括["U", "D", "L", "R"]
        """
        super().__init__()
        self.game_window: Surface = game_window
        self.game_matrix: List[List[int]] = game_matrix
        self.color: Tuple[int, int, int] = color
        self.direction: str = direction
        self.head: Tuple[int, int] = pos

        self.__across_direction = (DirectionEnum.up, DirectionEnum.down)

        # 初始化蛇
        self.start_time = None  # 蛇第一次开始移动的时间
        self.end_time = None  # 蛇死亡的时间
        self.body: deque[SnakeCube] = deque()
        self.__init_snake()
        self.__max_rows = len(game_matrix)
        self.__max_cols = len(game_matrix[0])

    def __init_snake(self):
        self.body.append(SnakeCube(max(self.head[0] - 1, 0), self.head[1]))
        self.game_matrix[self.body[-1].y][self.body[-1].x] = "s"
        self.add_node()
        pygame.display.update()

    def move(self, direction: str):
        if self.start_time is None:
            self.start_time = arrow.now()
            logger.info(f"游戏开始时间: {self.start_time}")
        logger.debug(f"<蛇头方向>:{self.direction} - <移动方向>: {direction}")
        next_cube_ = self.head  # next_cube_: 下个位置的坐标 (x,y)
        if direction == DirectionEnum.up:
            next_cube_ = (self.head[0], self.head[1] - 1)
        elif direction == DirectionEnum.down:
            next_cube_ = (self.head[0], self.head[1] + 1)
        elif direction == DirectionEnum.left:
            next_cube_ = (self.head[0] - 1, self.head[1])
        elif direction == DirectionEnum.right:
            next_cube_ = (self.head[0] + 1, self.head[1])
        # TODO: 判断是否可移动
        # 1.撞到身体或墙壁，结束游戏
        if next_cube_[0] < 0 or next_cube_[0] >= self.__max_cols:
            raise GameOverException("GameOver: 撞墙")
        if next_cube_[1] < 0 or next_cube_[1] >= self.__max_rows:
            raise GameOverException("GameOver: 撞墙")
        if self.game_matrix[next_cube_[1]][next_cube_[0]] == "s":
            if next_cube_ != self.body[0].get_pos():
                raise GameOverException("GameOver: 撞身体")

        # 2.吃到食物，增加一节（通过不删除尾部来实现增加）
        # 3.正常移动，删除尾部一节
        if self.game_matrix[next_cube_[1]][next_cube_[0]] == 1:
            pygame.event.post(pygame.event.Event(EAT_SNACK_EVENT))
        else:
            self.del_node()

        # 执行移动
        self.head = next_cube_
        self.direction = direction
        self.add_node()
        # 移动完成刷新画面
        pygame.display.update()
        pygame.time.delay(MOVE_TIME)

        # 计算游戏超时
        if self.get_survival_time() >= GAME_TIME:
            self.end_time = arrow.now()
            raise GameOverException("GameOver: 游戏时间耗尽")

    def add_node(self):
        """
        贪吃蛇头部增加一节
        """
        self.body[-1].draw_body(self.game_window)
        self.body.append(SnakeCube(self.head[0], self.head[1]))
        self.game_matrix[self.body[-1].y][self.body[-1].x] = "s"
        self.body[-1].draw_eyes(self.direction in self.__across_direction, self.game_window)

    def del_node(self):
        """
        贪吃蛇尾部删除一节
        """
        del_cube_ = self.body.popleft()
        del_cube_.draw_not(self.game_window)
        if del_cube_ not in self.body:
            self.game_matrix[del_cube_.y][del_cube_.x] = 0

    def get_score(self):
        return len(self.body) - 2

    def get_survival_time(self):
        start_time_tamp_ = self.start_time
        if start_time_tamp_ is None:
            start_time_tamp_ = arrow.now()

        if self.end_time is None:
            return arrow.now().int_timestamp - start_time_tamp_.int_timestamp
        return self.end_time.int_timestamp - start_time_tamp_.int_timestamp
