# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE

import math
import numpy as np
from typing import Tuple, List


class ClickModSet:
    @staticmethod
    def create_click_mod(zoom: int, loc: float = 0.0, scale: float = 0.45, size: Tuple[int, int] = (2000, 2)) -> np.ndarray:
        """
        生成正态分布的鼠标随机点击模型
        
        :param zoom: 缩放比例，约等于偏移像素点
        :param loc: 正态分布的均值
        :param scale: 正态分布的标准差
        :param size: 模型大小，即模型中的坐标总量
        :return: 处理后的坐标数组
        """
        mx, my = np.random.normal(loc=loc, scale=scale, size=size).T

        x_int, y_int = [], []
        for x, y in zip(mx, my):
            if x < 0 and y > 0:
                x_int.append(int(x * zoom * 1.373))
                y_int.append(int(y * zoom * 1.303))
            elif x > 0 and y < 0:
                roll = np.random.randint(0, 9)
                if roll < 5:
                    x_int.append(int(x * zoom * -1.350))
                    y_int.append(int(y * zoom * -1.200))
                elif roll >= 8:
                    x_int.append(int(x * zoom))
                    y_int.append(int(y * zoom))
                else:
                    x_int.append(int(x * zoom * 0.618))
                    y_int.append(int(y * zoom * 0.618))
            else:
                x_int.append(int(x * zoom))
                y_int.append(int(y * zoom))

        x_int = [int(x * 0.816) for x in x_int]
        y_int = [int(y * 0.712) for y in y_int]

        x_int = [int(x * 0.718) if abs(x) > zoom else x for x in x_int]
        y_int = [int(y * 0.618) if abs(y) > zoom * 1.15 else y for y in y_int]

        return np.array(list(zip(x_int, y_int)))

    @staticmethod
    def choice_mod_pos(data_list: np.ndarray) -> Tuple[int, int]:
        """
        从模型中抽取一个坐标
        
        :param data_list: 坐标数据列表
        :return: 选择的坐标
        """
        x, y = data_list[np.random.randint(0, len(data_list) - 1)]

        roll_seed = 20
        if abs(x) <= 50 and abs(y) <= 50:
            roll_seed = 5
        elif 50 < max(abs(x), abs(y)) <= 100:
            roll_seed = 15 if abs(x) > 50 and abs(y) > 50 else 10

        return x + np.random.randint(-roll_seed, roll_seed), y + np.random.randint(-roll_seed, roll_seed)

    @staticmethod
    def pos_rotate(pos: Tuple[int, int], r: float = 90) -> Tuple[int, int]:
        """
        将一个坐标围绕原点（0，0）进行顺时针旋转
        
        :param pos: 原始坐标
        :param r: 旋转角度（度）
        :return: 旋转后的坐标
        """
        x, y = pos
        ang = math.radians(r)
        return int(x * math.cos(ang) + y * math.sin(ang)), int(-x * math.sin(ang) + y * math.cos(ang))


if __name__ == '__main__':
    data = ClickModSet.create_click_mod(50)
    x, y = ClickModSet.choice_mod_pos(data)

    print("原始模型显示前20个坐标:\n", data[:20])
    print("测试坐标旋转，对第一个点旋转180度:", ClickModSet.pos_rotate(data[0], 180))
    print(f"随机取值 ({x},{y})，并旋转90度: {ClickModSet.pos_rotate((x,y), 90)}")
