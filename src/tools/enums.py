# -*- coding:utf-8 -*-
# @Time        : 2021/12/30 15:26
# @Author      : Tuffy
# @Description :
from enum import Enum


class DirectionEnum(str, Enum):
    """
    运动方向
    """
    up = "U"
    down = "D"
    left = "L"
    right = "R"
