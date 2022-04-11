# -*- coding:utf-8 -*-
# @Time        : 2022/1/5 14:05
# @Author      : Tuffy
# @Description :  
from typing import List, Tuple

import pygame
from loguru import logger
from pygame import Surface

from src.tools.draws import SnackCube
from src.settings import SNACK_COLOR, EAT_ERROR_EVENT


class Snack(object):
    def __init__(self, game_window: Surface,
                 game_matrix: List[List[int]],
                 pos: Tuple[int, int],
                 *,
                 color: Tuple[int, int, int] = SNACK_COLOR):
        """
        食物
        Args:
            game_window: 游戏窗口
            game_matrix: 游戏矩阵   "s"代表蛇的身体  0代表空白格子  1代表食物
            color: 食物的颜色 (r,g,b)
            pos: 食物的坐标 (x, y)
        """
        super().__init__()
        self.game_window: Surface = game_window
        self.game_matrix: List[List[int]] = game_matrix
        self.color: Tuple[int, int, int] = color
        self.pos: Tuple[int, int] = pos

        self.cube: SnackCube = SnackCube(self.pos[0], self.pos[1])
        self.__init_snack()

    def __init_snack(self):
        self.game_matrix[self.cube.y][self.cube.x] = 1
        self.cube.draw_snack(self.game_window)
        logger.debug(f"<食物坐标>:{self.cube.get_pos()}")
        pygame.display.update()

    def del_snack(self):
        if self.game_matrix[self.cube.y][self.cube.x] == 1:
            pygame.event.post(pygame.event.Event(EAT_ERROR_EVENT))
        if self.game_matrix[self.cube.y][self.cube.x] == "s":
            return
        self.cube.draw_not(self.game_window)
        self.game_matrix[self.cube.y][self.cube.x] = 0
