# -*- coding:utf-8 -*-
# @Time        : 2021/12/30 15:55
# @Author      : Tuffy
# @Description :
from typing import Tuple

import pygame
import pygame.freetype

from src.settings import CUBE_HEIGHT, CUBE_WIDTH, SNAKE_EYES_COLOR, SNAKE_COLOR, NOT_COLOR, SNACK_COLOR, WIN_HEIGHT, WIN_WIDTH


def draw_grid(cols, rows, surface, width=CUBE_WIDTH, height=CUBE_HEIGHT, color=(255, 255, 255)):
    """
    绘制网格线
    Args:
        cols: 列数
        rows: 行数
        surface:  窗口
        width: 单元格宽度
        height: 单元格高度
        color: 线条颜色 (R,G,B) 格式
    """
    win_width = width * cols
    win_height = height * rows
    x = 0
    for l_ in range(cols - 1):
        x += width
        pygame.draw.line(surface, color, (x, 0), (x, win_height))
    y = 0
    for l_ in range(rows - 1):
        y += width
        pygame.draw.line(surface, color, (0, y), (win_width, y))


def draw_over(surface: pygame.Surface,
              text: str,
              width=WIN_WIDTH,
              height=WIN_HEIGHT,
              font_size=36,
              font_color=SNAKE_COLOR,
              back_color=(255, 255, 255)):
    """
    绘制游戏结束画面
    Args:
        surface: 游戏窗口
        text: 显示内容
        width: 窗口宽度
        height: 窗口高度
        font_size: 字体大小
        font_color: 字体颜色
        back_color: 背景颜色
    """
    # 设置字体
    over_rect_ = pygame.draw.rect(surface, back_color, (
        (0, height // 4),
        (width, height // 2)
    ))
    over_font_: pygame.freetype.Font = pygame.freetype.SysFont("微软雅黑", font_size, True)
    over_surface_, _ = over_font_.render(text, font_color)
    show_rect_ = over_surface_.get_rect()
    show_rect_.center = over_rect_.center
    surface.blit(over_surface_, show_rect_)
    # 设置居中
    pygame.display.update()


class Cube(object):
    def __init__(self, x, y, width=CUBE_WIDTH, height=CUBE_HEIGHT):
        """
        格子
        Args:
            x: 格子所属列
            y: 格子所属行
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def get_pos(self) -> Tuple[int, int]:
        """
        获取单元格坐标
        Returns: (x,y)
        """
        return self.x, self.y

    def draw(self, surface, color):
        """
        Args:
            color: 颜色
            surface: 游戏窗口
        """

        pygame.draw.rect(surface, color, (
            (self.x * self.width + 1, self.y * self.height + 1),
            (self.width - 2, self.height - 2)
        ))


class SnakeCube(Cube):
    def draw_body(self, surface, color=SNAKE_COLOR):
        return super().draw(surface, color)

    def draw_not(self, surface, color=NOT_COLOR):
        return super().draw(surface, color)

    def draw_eyes(self, across: bool, surface, color=SNAKE_EYES_COLOR):
        """
        绘制眼睛
        Args:
            across: 眼睛方向 True 代表蛇正在上下行驶，眼睛是横着的
        """
        self.draw_body(surface)
        if across:
            dis_x = self.width // 4  # 眼睛离两侧的距离
            dis_y = self.width // 2  # 眼睛离两侧的距离
            e1 = (self.x * self.width + dis_x, self.y * self.height + dis_y)
            e2 = ((self.x + 1) * self.width - dis_x, self.y * self.height + dis_y)
        else:
            dis_x = self.width // 2  # 眼睛离两侧的距离
            dis_y = self.width // 4  # 眼睛离两侧的距离
            e1 = (self.x * self.width + dis_x, self.y * self.height + dis_y)
            e2 = (self.x * self.width + dis_x, (self.y + 1) * self.height - dis_y)

        pygame.draw.circle(surface, color, e1, 3)
        pygame.draw.circle(surface, color, e2, 3)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class SnackCube(Cube):

    def draw_snack(self, surface, color=SNACK_COLOR):
        return super().draw(surface, color)

    def draw_not(self, surface, color=NOT_COLOR):
        return super().draw(surface, color)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
