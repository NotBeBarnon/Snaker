# -*- coding:utf-8 -*-
# @Time        : 2021/12/30 15:46
# @Author      : Tuffy
# @Description :
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from loguru import logger

# 项目根目录
PROJECT_DIR: Path = Path(__file__).parents[1]
if PROJECT_DIR.name == "lib":  # 适配cx_Freeze打包项目后根目录的变化
    PROJECT_DIR = PROJECT_DIR.parent

# 加载环境变量
load_dotenv(PROJECT_DIR.joinpath("project_env"))

CUBE_WIDTH = 25  # 一格的宽度
CUBE_HEIGHT = CUBE_WIDTH  # 一格的高度

WIN_COLS_NUM = 15 # 游戏窗口列数
WIN_ROWS_NUM = WIN_COLS_NUM  # 游戏窗口行数

WIN_WIDTH = WIN_COLS_NUM * CUBE_WIDTH  # 窗口总宽度
WIN_HEIGHT = WIN_ROWS_NUM * CUBE_HEIGHT  # 窗口总高度

SNAKE_INIT_POS = (10, 10)  # 蛇的初始位置

SNAKE_COLOR = (255, 0, 0)  # 蛇的颜色
SNAKE_EYES_COLOR = (0, 0, 0)  # 蛇眼的颜色
SNACK_COLOR = (0, 0, 255)  # 食物颜色
NOT_COLOR = (0, 0, 0)

GAME_TIME = 3 * 60  # 游戏时间 秒数
GENERATE_SNACK_TIME = 0.5  # 食物生成上限时间 秒数
GENERATE_MOVE_TIME = 10  # 移动路线生成上限时间 秒数
GAME_END_SCORE = 120  # 游戏结束分数
MOVE_TIME = 50  # 每次移动蛇的耗时

BACK_MUSIC_FILE = PROJECT_DIR.joinpath(f"media/bkmusic.mp3")
EAT_MUSIC_FILE = PROJECT_DIR.joinpath(f"media/eat.mp3")
EAT_ERROR_MUSIC_FILE = PROJECT_DIR.joinpath(f"media/error.mp3")
START_MUSIC_FILE = PROJECT_DIR.joinpath(f"media/start.mp3")
OVER_MUSIC_FILE = PROJECT_DIR.joinpath(f"media/over.mp3")

# 游戏事件控制
MUSIC_END_EVENT = 32847 + 1
EAT_SNACK_EVENT = 32847 + 2
GAME_OVER_EVENT = 32847 + 3
EAT_ERROR_EVENT = 32847 + 4

# DEBUG控制
DEV = True if os.getenv("DEV", "0") in ("True", "true", "TRUE", "1") else False
# 生产环境控制
PROD = False if DEV or (os.getenv("PROD", "1") in ("False", "0", "FALSE", "false")) else True

# 配置日志
LOGGER_CONFIG = {
    "handlers": [
        {
            "sink": sys.stdout,
            "level": "DEBUG" if DEV else os.getenv("LOG_LEVEL", "info").upper(),
            "enqueue": True,
            "backtrace": True,
            "diagnose": True,
            "catch": True
        },
        {
            "sink": PROJECT_DIR.joinpath("logs/project.log"),
            "rotation": "3 MB",
            "retention": "30 days",
            "level": "INFO",
            "enqueue": True,
            "backtrace": True,
            "diagnose": True,
            "encoding": "utf-8",
            "catch": True
        },
    ]
}
logger.configure(**LOGGER_CONFIG)

DEV and logger.info(f"[DEV - PID:{os.getpid()}] RCUSimulator Server")
PROD and logger.info(f"[PROD - PID:{os.getpid()}] RCUSimulator Server")
