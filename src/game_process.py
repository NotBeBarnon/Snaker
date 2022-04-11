# -*- coding:utf-8 -*-
# @Time        : 2022/1/5 16:12
# @Author      : Tuffy
# @Description :
import importlib
import random
import threading
from multiprocessing import Process
from multiprocessing.connection import Connection
from typing import Tuple, List, Any

import pygame
from loguru import logger

from .models.snack import Snack
from .models.snake import Snake
from .settings import WIN_WIDTH, WIN_HEIGHT, WIN_ROWS_NUM, WIN_COLS_NUM, SNAKE_INIT_POS, GAME_END_SCORE, GENERATE_SNACK_TIME, GENERATE_MOVE_TIME, \
    BACK_MUSIC_FILE, OVER_MUSIC_FILE, START_MUSIC_FILE, EAT_MUSIC_FILE, MUSIC_END_EVENT, EAT_SNACK_EVENT, GAME_OVER_EVENT, EAT_ERROR_EVENT, EAT_ERROR_MUSIC_FILE
from .tools.draws import draw_grid, draw_over
from .tools.exceptions import GameOverException


class GameProcess(Process):
    def __init__(self, move_conn, snack_conn, name="CowaveSnake"):
        super().__init__(daemon=True)
        self.move_conn: Connection = move_conn
        self.snack_conn: Connection = snack_conn
        self.name = name

    # @staticmethod
    # def wait_event(start_event: threading.Event):
    #     # 设置背景音乐
    #     pygame.mixer.init()
    #     back_music = pygame.mixer.Sound(str(BACK_MUSIC_FILE))
    #     start_music = pygame.mixer.Sound(str(START_MUSIC_FILE))
    #     eat_music = pygame.mixer.Sound(str(EAT_MUSIC_FILE))
    #     over_music = pygame.mixer.Sound(str(OVER_MUSIC_FILE))
    #     back_music_channel = back_music.play(-1)
    #
    #     pygame.event.set_allowed((
    #         pygame.QUIT,
    #         pygame.KEYDOWN,
    #         pygame.KEYUP,
    #         pygame.USEREVENT,
    #         MUSIC_END_EVENT,
    #         EAT_SNACK_EVENT,
    #         GAME_OVER_EVENT,
    #     ))
    #     is_alive = True
    #     is_start = False
    #
    #     while is_alive:
    #         # 循环获取事件，监听事件
    #         for event in pygame.event.get():
    #             logger.debug(event)
    #             # 判断用户是否点了关闭按钮
    #             if event.type == pygame.QUIT:
    #                 # 卸载所有pygame模块
    #                 is_alive = False
    #                 pygame.quit()
    #                 break
    #
    #             if event.type == pygame.KEYUP:
    #                 if event.key in (pygame.K_SPACE, pygame.K_RETURN):
    #                     if not is_start:
    #                         # 开始游戏
    #                         logger.debug(f"开始游戏")
    #                         is_start = True
    #                         back_music_channel.set_volume(0.2)
    #                         start_music.play()
    #                         start_event.set()
    #
    #             if event.type == MUSIC_END_EVENT:
    #                 back_music_channel.set_volume(1)
    #
    #             if event.type == EAT_SNACK_EVENT:
    #                 back_music_channel.set_volume(0.2)
    #                 eat_music.play()
    #
    #             if event.type == GAME_OVER_EVENT:
    #                 back_music.stop()
    #                 over_music.play()

    def game_thread(self, start_event: threading.Event, game_window):
        # 绘制网格，初始化矩阵，蛇和食物
        draw_grid(WIN_COLS_NUM, WIN_ROWS_NUM, game_window)
        game_matrix = [[0 for _ in range(WIN_COLS_NUM)] for _ in range(WIN_ROWS_NUM)]
        cowave_snake = Snake(game_window, game_matrix, SNAKE_INIT_POS)
        # 等待游戏开始
        start_event.wait()
        logger.info(f"-------- [Game Start] 游戏开始 --------")
        while True:
            # 生成食物 [游戏矩阵，蛇头坐标，蛇移动方向，蛇身体，窗格大小]
            self.snack_conn.send((
                game_matrix,
                cowave_snake.head,
                cowave_snake.direction,
                [cube_.get_pos() for cube_ in cowave_snake.body],
                (WIN_ROWS_NUM, WIN_COLS_NUM)
            ))
            snack_pos_: Tuple[int, int] = self.snack_conn.recv()
            snack_ = Snack(game_window, game_matrix, snack_pos_)

            # 生成蛇的移动路线 [游戏矩阵，食物坐标，蛇头坐标，蛇移动方向，蛇身体，窗格大小]
            self.move_conn.send((
                game_matrix,
                snack_pos_,
                cowave_snake.head,
                cowave_snake.direction,
                [cube_.get_pos() for cube_ in cowave_snake.body],
                (WIN_ROWS_NUM, WIN_COLS_NUM),
            ))
            move_path_: List[str] = self.move_conn.recv()

            try:
                _ = [cowave_snake.move(dir_) for dir_ in move_path_]
            except GameOverException as goe:
                logger.debug(goe)
                pygame.event.post(pygame.event.Event(GAME_OVER_EVENT))
                break
            except Exception as exc:
                logger.error(f"程序错误:{exc}")
                break
            # 达到分值游戏结束
            if cowave_snake.get_score() >= GAME_END_SCORE:
                break
            # 移动完没吃到食物重新生成
            snack_.del_snack()

        text_ = f"{cowave_snake.get_survival_time()}s Over: {cowave_snake.get_score()}"
        draw_over(game_window, text_)
        logger.info(f"-------- [Game Over] 游戏结束 --------")
        logger.info(f"-------- {text_} --------")

    def run(self):
        # 初始化Pygame
        pygame.init()
        pygame.event.set_blocked(None)
        game_window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
        pygame.display.set_caption(self.name)
        clock = pygame.time.Clock()
        clock.tick(30)

        # 设置背景音乐
        pygame.mixer.init()
        back_music = pygame.mixer.Sound(str(BACK_MUSIC_FILE))
        start_music = pygame.mixer.Sound(str(START_MUSIC_FILE))
        eat_music = pygame.mixer.Sound(str(EAT_MUSIC_FILE))
        eat_error_music = pygame.mixer.Sound(str(EAT_ERROR_MUSIC_FILE))
        over_music = pygame.mixer.Sound(str(OVER_MUSIC_FILE))
        back_music_channel = back_music.play(-1)
        # 设置事件
        pygame.event.set_allowed((
            pygame.QUIT,
            pygame.KEYUP,
            pygame.USEREVENT,
            MUSIC_END_EVENT,
            EAT_SNACK_EVENT,
            GAME_OVER_EVENT,
            EAT_ERROR_EVENT,
        ))

        # 创建游戏线程
        start_event = threading.Event()
        game_thread = threading.Thread(target=self.game_thread, args=(start_event, game_window))
        game_thread.start()

        is_alive = True
        is_start = False
        # 启动事件监听循环
        while True:
            # 循环获取事件，监听事件
            event = pygame.event.wait()
            logger.debug(event)
            # 判断用户是否点了关闭按钮
            if event.type == pygame.QUIT:
                # 卸载所有pygame模块
                is_alive = False
                pygame.quit()
                break

            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    if not is_start:
                        # 开始游戏
                        is_start = True
                        back_music_channel.set_volume(0.2)
                        start_music.play()
                        start_event.set()

            if event.type == MUSIC_END_EVENT:
                back_music_channel.set_volume(1)

            if event.type == EAT_SNACK_EVENT:
                back_music_channel.set_volume(0.2)
                eat_music.play()

            if event.type == EAT_ERROR_EVENT:
                back_music_channel.set_volume(0.2)
                eat_error_music.play()

            if event.type == GAME_OVER_EVENT:
                back_music.stop()
                over_music.play()
        game_thread.join()

    # def old_run(self):
    #     import pygame
    #
    #     from .models.snack import Snack
    #     from .models.snake import Snake
    #     from .tools.draws import draw_grid, draw_over
    #     from .tools.exceptions import GameOverException
    #
    #     # 初始化Pygame
    #     pygame.init()
    #     game_window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    #     pygame.display.set_caption(self.name)
    #     clock = pygame.time.Clock()
    #     clock.tick(30)
    #     # 绘制网格，初始化矩阵，蛇和食物
    #     draw_grid(WIN_COLS_NUM, WIN_ROWS_NUM, game_window)
    #     game_matrix = [[0 for _ in range(WIN_COLS_NUM)] for _ in range(WIN_ROWS_NUM)]
    #     cowave_snake = Snake(game_window, game_matrix, SNAKE_INIT_POS)
    #
    #     # 设置游戏事件监听线程
    #     start_event = threading.Event()
    #     event_thread = threading.Thread(target=self.wait_event, args=(start_event,))
    #     event_thread.start()
    #
    #     start_event.wait()
    #     logger.info(f"-------- [Game Start] 游戏开始 --------")
    #     while True:
    #         # 生成食物 [游戏矩阵，蛇头坐标，蛇移动方向，蛇身体，窗格大小]
    #         self.snack_conn.send((
    #             game_matrix,
    #             cowave_snake.head,
    #             cowave_snake.direction,
    #             [cube_.get_pos() for cube_ in cowave_snake.body],
    #             (WIN_ROWS_NUM, WIN_COLS_NUM)
    #         ))
    #         snack_pos_: Tuple[int, int] = self.snack_conn.recv()
    #         snack_ = Snack(game_window, game_matrix, snack_pos_)
    #
    #         # 生成蛇的移动路线 [游戏矩阵，食物坐标，蛇头坐标，蛇移动方向，蛇身体，窗格大小]
    #         self.move_conn.send((
    #             game_matrix,
    #             snack_pos_,
    #             cowave_snake.head,
    #             cowave_snake.direction,
    #             [cube_.get_pos() for cube_ in cowave_snake.body],
    #             (WIN_ROWS_NUM, WIN_COLS_NUM),
    #         ))
    #         move_path_: List[str] = self.move_conn.recv()
    #
    #         try:
    #             _ = [cowave_snake.move(dir_) for dir_ in move_path_]
    #         except GameOverException as goe:
    #             logger.debug(goe)
    #             break
    #         except Exception as exc:
    #             logger.error(f"程序错误:{exc}")
    #             break
    #         # 达到分值游戏结束
    #         if cowave_snake.get_score() >= GAME_END_SCORE:
    #             break
    #         # 移动完没吃到食物重新生成
    #         snack_.del_snack()
    #     pygame.event.post(pygame.event.Event(GAME_OVER_EVENT))
    #
    #     text_ = f"{cowave_snake.get_survival_time()}s Over: {cowave_snake.get_score()}"
    #     draw_over(game_window, text_)
    #     logger.info(f"-------- [Game Over] 游戏结束 --------")
    #     logger.info(f"-------- {text_} --------")
    #
    #     event_thread.join()


class MoveProcess(Process):
    def __init__(self, move_conn, fn_model=None):
        super().__init__(daemon=True)
        self.fn_model = fn_model or "GenerateMove"
        self.move_conn: Connection = move_conn

    def run(self):
        from src.tools.limit_thread import LimitThread
        func_ = getattr(importlib.import_module(self.fn_model), "fnGenerateMove", None)
        while True:
            logger.debug(f"-------- [Move Process]等待数据 --------")
            data_ = self.move_conn.recv()
            try:
                t = LimitThread(target=func_, args=data_)
                t.start()
                result = t.wait_result(GENERATE_MOVE_TIME)
            except Exception as exc:
                logger.debug(f"调用移动路线计算方法失败:{exc}")
                result = None
            if result:
                self.move_conn.send(result)
            else:
                # 生成移动方向
                move_ = ["D", "U", "R", "L"]
                if data_[3] == "D":
                    move_.pop(1)
                elif data_[3] == "U":
                    move_.pop(0)
                elif data_[3] == "R":
                    move_.pop(3)
                elif data_[3] == "L":
                    move_.pop(2)
                self.move_conn.send([random.choice(move_)])


class SnackProcess(Process):
    def __init__(self, snack_conn, fn_model=None):
        super().__init__(daemon=True)
        self.fn_model = fn_model or "GenerateSnack"
        self.snack_conn: Connection = snack_conn

    @staticmethod
    def get_median(value, min_value, max_value):
        return min(max(value, min_value), max_value)

    @staticmethod
    def check_result(
            result: Any,
            game_matrix,
            head,
            direction,
            body,
            win_size
    ):
        try:
            if len(result) == 2:
                if result[0] < 0 or result[0] >= win_size[1]:
                    raise Exception(f"x坐标超出界限:{result[0]}")
                if result[1] < 0 or result[1] >= win_size[0]:
                    raise Exception(f"y坐标超出界限:{result[1]}")
                if game_matrix[result[1]][result[0]]:
                    raise Exception(f"{result}为蛇身体")
                return result
        except Exception as exc:
            logger.warning(f"对抗程序生成食物失败，自动生成食物: {exc}")
        i = 1
        while True:
            for snack_ in [
                (SnackProcess.get_median(head[0] + i, 0, win_size[1] - 1), head[1]),
                (SnackProcess.get_median(head[0] - i, 0, win_size[1] - 1), head[1]),
                (head[0], SnackProcess.get_median(head[1] + i, 0, win_size[0] - 1)),
                (head[0], SnackProcess.get_median(head[1] - i, 0, win_size[0] - 1)),
                (
                        SnackProcess.get_median(head[0] + i, 0, win_size[1] - 1),
                        SnackProcess.get_median(head[1] + i, 0, win_size[0] - 1)
                ),
                (
                        SnackProcess.get_median(head[0] - i, 0, win_size[1] - 1),
                        SnackProcess.get_median(head[1] + i, 0, win_size[0] - 1)
                ),
                (
                        SnackProcess.get_median(head[0] + i, 0, win_size[1] - 1),
                        SnackProcess.get_median(head[1] - i, 0, win_size[0] - 1)
                ),
                (
                        SnackProcess.get_median(head[0] - i, 0, win_size[1] - 1),
                        SnackProcess.get_median(head[1] - i, 0, win_size[0] - 1)
                ),
            ]:
                if game_matrix[snack_[1]][snack_[0]]:
                    continue
                return snack_
            i += 1

    def run(self):
        from src.tools.limit_thread import LimitThread
        func_ = getattr(importlib.import_module(self.fn_model), "fnGenerateSnack", None)
        while True:
            logger.debug(f"-------- [Snack Process]等待数据 --------")
            data_ = self.snack_conn.recv()
            try:
                t = LimitThread(target=func_, args=data_)
                t.start()
                result = t.wait_result(GENERATE_SNACK_TIME)
            except Exception as exc:
                logger.warning(f"调用食物生成方法失败:{exc}")
                result = None

            self.snack_conn.send(self.check_result(result, *data_))
