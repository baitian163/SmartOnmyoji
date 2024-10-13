# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE

from os import path, walk
from re import search, compile
from typing import Tuple, List, Dict, Optional
import cv2
import numpy as np
import logging

from modules.ModuleImgProcess import ImgProcess
from modules.ModuleGetConfig import ReadConfigFile

class GetTargetPicInfo:
    def __init__(self, target_modname: str, custom_target_path: str, compress_val: float = 1):
        self.modname = target_modname
        self.custom_target_path = custom_target_path
        self.compress_val = compress_val
        self.rc = ReadConfigFile()

    def get_target_folder_path(self) -> Optional[str]:
        file_name = self.rc.read_config_target_path_files_name()
        parent_path = path.abspath(path.dirname(path.dirname(__file__)))

        for name, folder in file_name:
            if self.modname == name:
                return path.join(parent_path, "img", folder)

        if self.modname == "自定义":
            return self.custom_target_path

        return None

    @property
    def get_target_info(self) -> Optional[Tuple[Dict, Dict, List, List, Dict]]:
        folder_path = self.get_target_folder_path()
        if not folder_path:
            logging.error("未找到目标文件夹或图片地址！")
            return None

        return self._process_target_images(folder_path)

    def _process_target_images(self, folder_path: str) -> Tuple[Dict, Dict, List, List, Dict]:
        target_img_sift = {}
        img_hw = {}
        img_name = []
        img_file_path = []
        cv2_img = {}

        for cur_dir, _, included_file in walk(folder_path):
            for file in included_file:
                if search(r'\.(jpg|png)$', file):  # 兼容jpg和png格式
                    img_file_path.append(path.join(cur_dir, file))

        if not img_file_path:
            logging.error("未找到目标文件夹或图片地址！")
            return None

        for img_path in img_file_path:
            img = cv2.imdecode(np.fromfile(img_path, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            img_hw[len(img_name)] = img.shape[:2]  # 获取目标图片宽高
            img_name.append(self.trans_path_to_name(img_path))  # 获取目标图片名称
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            target_img_sift[len(img_name)] = ImgProcess.get_sift(img)  # 获取目标图片特征点信息
            cv2_img[len(img_name)] = img  # 将图片信息读取到内存

        return target_img_sift, img_hw, img_name, img_file_path, cv2_img

    @staticmethod
    def trans_path_to_name(path_string: str) -> str:
        """获取指定文件路径的文件名称"""
        return path_string.split("\\")[-1].split(".")[0]  # 直接从路径中提取文件名

    # 其他方法保持不变...
