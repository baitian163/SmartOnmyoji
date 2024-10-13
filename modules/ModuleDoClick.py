# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE

from os.path import abspath, dirname
from time import sleep
import random
import win32com.client
from win32gui import SetForegroundWindow, GetWindowRect
from win32api import MAKELONG, SendMessage
from win32con import WM_LBUTTONUP, WM_LBUTTONDOWN, WM_ACTIVATE, WA_ACTIVE
from pyautogui import position, click, moveTo
from typing import List, Tuple, Optional

from modules.ModuleClickModSet import ClickModSet
from modules.ModuleHandleSet import HandleSet
from modules.ModuleGetConfig import ReadConfigFile


class DoClick:
    def __init__(self, pos: Tuple[int, int], click_mod: List[Tuple[int, int]], handle_num: int = 0):
        self.click_mod = click_mod
        self.handle_num = handle_num
        self.pos = pos
        self.rc = ReadConfigFile()
        self.other_setting = self.rc.read_config_other_setting()
        self.ex_click_probability = float(self.other_setting[10])  # 从配置文件读取是否有设置额外偏移点击概率

    def windows_click(self) -> Tuple[bool, List[Tuple[int, int]]]:
        """点击目标位置,可后台点击（仅兼容部分窗体程序）"""
        if self.pos is None:
            return False, []

        pos = self.pos
        click_pos_list = []
        x1, y1, x2, y2 = GetWindowRect(self.handle_num)
        width = int(x2 - x1)
        height = int(y2 - y1)

        px, py = self.get_p_pos(self.click_mod, width, height, pos)

        cx = int(px + pos[0])
        cy = int(py + pos[1]) - 40  # 减去40是因为window这个框占用40单位的高度

        long_position = MAKELONG(cx, cy)
        SendMessage(self.handle_num, WM_ACTIVATE, WA_ACTIVE, 0)
        SendMessage(self.handle_num, WM_LBUTTONDOWN, 0, long_position)  # 模拟鼠标按下
        sleep(random.uniform(0.05, 0.15))  # 点击弹起改为随机
        SendMessage(self.handle_num, WM_LBUTTONUP, 0, long_position)  # 模拟鼠标弹起

        click_pos_list.append((cx, cy))

        # 模拟真实点击、混淆点击热区
        if self.ex_click_probability > 0:  # 如果配置文件设置了额外随机点击
            ex_pos = self.get_ex_click_pos(self.ex_click_probability, width, height, (cx, cy), px, py)
            if ex_pos is not None:
                sleep(random.uniform(0.05, 0.15))  # 点击弹起改为随机
                long_position = MAKELONG(ex_pos[0], ex_pos[1])
                SendMessage(self.handle_num, WM_LBUTTONDOWN, 0, long_position)  # 模拟鼠标按下
                sleep(random.uniform(0.05, 0.15))  # 点击弹起改为随机
                SendMessage(self.handle_num, WM_LBUTTONUP, 0, long_position)  # 模拟鼠标弹起
                click_pos_list.append(ex_pos)

        return True, click_pos_list

    def adb_click(self, device_id: str) -> Tuple[bool, List[Tuple[int, int]]]:
        """数据线连手机点击"""
        if self.pos is None:
            return False, []

        click_pos_list = []
        pos = self.pos
        screen_size = HandleSet.get_screen_size(device_id)
        height = int(screen_size[0])
        width = int(screen_size[1])

        px, py = self.get_p_pos(self.click_mod, width, height, pos)

        cx = int(px + pos[0])
        cy = int(py + pos[1])

        command = abspath(dirname(__file__)) + rf'\adb.exe -s {device_id} shell input tap {cx} {cy}'
        HandleSet.deal_cmd(command)
        click_pos_list.append((cx, cy))

        # 模拟真实点击、混淆点击热区
        if self.ex_click_probability > 0:  # 如果配置文件设置了额外随机点击
            ex_pos = self.get_ex_click_pos(self.ex_click_probability, width, height, (cx, cy), px, py)
            if ex_pos is not None:
                sleep(random.uniform(0.05, 0.15))  # 点击弹起改为随机
                command = abspath(dirname(__file__)) + rf'\adb.exe -s {device_id} shell input tap {ex_pos[0]} {ex_pos[1]}'
                HandleSet.deal_cmd(command)
                click_pos_list.append(ex_pos)

        return True, click_pos_list

    def windows_click_bk(self) -> Tuple[bool, List[Tuple[int, int]]]:
        """点击目标位置,只能前台点击（兼容所有窗体程序）"""
        click_pos_list = []
        pos = self.pos
        x1, y1, x2, y2 = GetWindowRect(self.handle_num)

        width = int(x2 - x1)
        height = int(y2 - y1)

        px, py = self.get_p_pos(self.click_mod, width, height, pos)

        cx = int(px + pos[0])
        cy = int(py + pos[1]) - 40  # 减去40是因为window这个框占用40单位的高度

        jx = cx + x1
        jy = cy + y1

        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        SetForegroundWindow(self.handle_num)
        sleep(0.2)  # 置顶后等0.2秒再点击
        moveTo(jx, jy)  # 鼠标移至目标
        click(jx, jy)

        click_pos_list.append((cx, cy))

        # 模拟真实点击、混淆点击热区
        if self.ex_click_probability > 0:  # 如果配置文件设置了额外随机点击
            ex_pos = self.get_ex_click_pos(self.ex_click_probability, width, height, (jx, jy), px, py)
            if ex_pos is not None:
                sleep(random.uniform(0.05, 0.15))  # 点击弹起改为随机
                click(ex_pos[0], ex_pos[1])
                click_pos_list.append(ex_pos)

        return True, click_pos_list

    @staticmethod
    def get_ex_click_pos(ex_click_probability: float, width: int, height: int, old_pos: Tuple[int, int], px: int, py: int) -> Optional[Tuple[int, int]]:
        """获取额外点击的偏移坐标"""
        roll_num = random.randint(0, 999)
        if roll_num < ex_click_probability * 0.1 * 1000:
            return old_pos
        elif ex_click_probability * 0.3 * 1000 < roll_num < ex_click_probability * 0.6 * 1000:
            return int(width * 0.618 + px), int(height * 0.618 + py)
        elif ex_click_probability * 0.6 * 1000 < roll_num < ex_click_probability * 0.9 * 1000:
            return random.randint(100, width), random.randint(100, height)
        return None

    @staticmethod
    def get_p_pos(click_mod: List[Tuple[int, int]], width: int, height: int, pos: Tuple[int, int]) -> Tuple[int, int]:
        """获取模型中的偏移坐标（九宫格）"""
        x1 = 0.382 * width
        x2 = 0.618 * width
        x3 = width
        y1 = 0.382 * height
        y2 = 0.618 * height
        y3 = height
        x = pos[0]
        y = pos[1]

        p_pos = ClickModSet.choice_mod_pos(click_mod)

        if x <= x1 and y <= y1:
            px, py = ClickModSet.pos_rotate(p_pos, 180)
        elif x <= x1 and y1 < y <= y2:
            px, py = ClickModSet.pos_rotate(p_pos, 135)
        elif x <= x1 and y2 < y <= y3:
            px, py = ClickModSet.pos_rotate(p_pos, 90)
        elif x1 < x <= x2 and y <= y1:
            px, py = ClickModSet.pos_rotate(p_pos, 225)
        elif x1 < x <= x2 and y1 < y <= y2:
            px, py = ClickModSet.pos_rotate(p_pos, 180)
        elif x1 < x <= x2 and y2 < y <= y3:
            px, py = ClickModSet.pos_rotate(p_pos, 45)
        elif x2 < x <= x3 and y <= y1:
            px, py = ClickModSet.pos_rotate(p_pos, 270)
        elif x2 < x <= x3 and y1 < y <= y2:
            px, py = ClickModSet.pos_rotate(p_pos, 315)
        else:
            px, py = p_pos

        py = int(py * 0.888)  # 让偏移结果再扁平一点

        return px, py
