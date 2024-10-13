# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE

import time
from os.path import abspath, dirname
from subprocess import Popen, PIPE
from typing import Optional

import numpy as np
import win32com.client
from numpy import frombuffer, uint8, array
from win32con import SRCCOPY
from win32gui import DeleteObject, SetForegroundWindow, GetWindowRect, GetWindowDC
from win32ui import CreateDCFromHandle, CreateBitmap
import cv2
from PIL import ImageGrab

from modules.ModuleGetConfig import ReadConfigFile


class GetScreenCapture:
    def __init__(self, handle_num: int = 0, handle_width: int = 0, handle_height: int = 0):
        self.hwd_num = handle_num
        self.screen_width = handle_width
        self.screen_height = handle_height
        self.screen_scale_rate = get_screen_scale_rate()

    def window_screen(self) -> np.ndarray:
        """Windows API 窗体截图方法，可后台截图，可被遮挡，不兼容部分窗口"""
        hwnd = self.hwd_num
        screen_width_source = int(self.screen_width / self.screen_scale_rate)
        screen_height_source = int(self.screen_height / self.screen_scale_rate)

        hwnd_dc = GetWindowDC(hwnd)
        mfc_dc = CreateDCFromHandle(hwnd_dc)
        save_dc = mfc_dc.CreateCompatibleDC()
        save_bit_map = CreateBitmap()
        save_bit_map.CreateCompatibleBitmap(mfc_dc, screen_width_source, screen_height_source)
        save_dc.SelectObject(save_bit_map)
        save_dc.BitBlt((0, 0), (screen_width_source, screen_height_source), mfc_dc, (0, 0), SRCCOPY)

        signed_ints_array = save_bit_map.GetBitmapBits(True)
        im_opencv = frombuffer(signed_ints_array, dtype='uint8')
        im_opencv.shape = (screen_height_source, screen_width_source, 4)
        im_opencv = cv2.cvtColor(im_opencv, cv2.COLOR_BGRA2GRAY)
        im_opencv = cv2.resize(im_opencv, (self.screen_width, self.screen_height))

        DeleteObject(save_bit_map.GetHandle())
        save_dc.DeleteDC()
        mfc_dc.DeleteDC()
        return im_opencv

    def window_screen_bk(self) -> np.ndarray:
        """PIL截图方法，不能被遮挡"""
        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('%')
        SetForegroundWindow(self.hwd_num)
        time.sleep(0.2)
        x1, y1, x2, y2 = GetWindowRect(self.hwd_num)
        grab_image = ImageGrab.grab((x1, y1, x2, y2))
        im_cv2 = array(grab_image)
        im_opencv = cv2.cvtColor(im_cv2, cv2.COLOR_BGRA2GRAY)
        return im_opencv

    @staticmethod
    def adb_screen(device_id: str) -> np.ndarray:
        """安卓手机adb截图"""
        command = abspath(dirname(__file__)) + f'\\adb.exe -s {device_id} shell screencap -p'
        commend = Popen(command, stdin=PIPE, stdout=PIPE, shell=True)
        img_bytes = commend.stdout.read().replace(b'\r\n', b'\n')
        scr_img = cv2.imdecode(frombuffer(img_bytes, uint8), cv2.IMREAD_COLOR)
        scr_img = cv2.cvtColor(scr_img, cv2.COLOR_BGRA2GRAY)
        return scr_img


def get_screen_scale_rate() -> float:
    """获取缩放比例"""
    set_config = ReadConfigFile()
    other_setting = set_config.read_config_other_setting()
    return float(other_setting[11])
