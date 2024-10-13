# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE

from typing import Tuple, List, Optional

import cv2
import numpy as np
from numpy import int32, float32

from modules.ModuleGetConfig import ReadConfigFile
from modules.ModuleImgProcess import ImgProcess

rc = ReadConfigFile()
other_setting = rc.read_config_other_setting()


class GetPosByTemplateMatch:
    @staticmethod
    def get_pos_by_template(screen_capture: np.ndarray, target_pic: List[np.ndarray], debug_status: bool) -> Tuple[Optional[List[int]], int]:
        screen_width = screen_capture.shape[1]
        screen_high = screen_capture.shape[0]

        pos = None
        val = 0.80
        for i, target in enumerate(target_pic):
            pos = GetPosByTemplateMatch.template_matching(screen_capture, target, screen_width, screen_high, val, debug_status, i)
            if pos is not None:
                if debug_status and other_setting[5]:
                    draw_img = ImgProcess.draw_pos_in_img(screen_capture, pos, [screen_high / 10, screen_width / 10])
                    ImgProcess.show_img(draw_img)
                return pos, i
        return pos, len(target_pic) - 1

    @staticmethod
    def template_matching(img_src: np.ndarray, template: np.ndarray, screen_width: int, screen_height: int, val: float, debug_status: bool, i: int) -> Optional[List[int]]:
        if img_src is None or template is None:
            return None

        img_tmp_height, img_tmp_width = template.shape[:2]
        img_src_height, img_src_width = img_src.shape[:2]
        res = cv2.matchTemplate(img_src, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        if debug_status:
            print(f"<br>第 [ {i+1} ] 张图片，匹配分数：[ {round(max_val,2)} ]")

        if max_val >= val:
            position = [
                int(screen_width / img_src_width * (max_loc[0] + img_tmp_width / 2)),
                int(screen_height / img_src_height * (max_loc[1] + img_tmp_height / 2))
            ]
            return position
        return None


class GetPosBySiftMatch:
    @staticmethod
    def get_pos_by_sift(target_sift: List, screen_sift: List, target_hw: List, target_img: List[np.ndarray], screen_img: np.ndarray, debug_status: bool) -> Tuple[Optional[Tuple[int, int]], int]:
        for i, (t_sift, t_hw, t_img) in enumerate(zip(target_sift, target_hw, target_img)):
            pos = GetPosBySiftMatch.sift_matching(t_sift, screen_sift, t_hw, t_img, screen_img, debug_status, i)
            if pos is not None:
                return pos, i
        return None, len(target_img) - 1

    @staticmethod
    def sift_matching(target_sift: Tuple, screen_sift: Tuple, target_hw: Tuple[int, int], target_img: np.ndarray, screen_img: np.ndarray, debug_status: bool, i: int) -> Optional[Tuple[int, int]]:
        kp1, des1 = target_sift
        kp2, des2 = screen_sift
        min_match_count = 9

        flann_index_kdtree = 0
        index_params = dict(algorithm=flann_index_kdtree, trees=4)
        search_params = dict(checks=50)

        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(des1, des2, k=2)

        good = [m for m, n in matches if m.distance < 0.6 * n.distance]

        if debug_status:
            print(f"<br>第 [ {i+1} ] 张图片，匹配角点数量：[ {len(good)} ] ,目标数量：[ {min_match_count} ]")

        if len(good) > min_match_count:
            src_pts = float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
            m, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)

            if debug_status and other_setting[5]:
                matches_mask = mask.ravel().tolist()
                draw_params = dict(matchColor=(0, 255, 0), singlePointColor=None, matchesMask=matches_mask, flags=2)
                img3 = cv2.drawMatches(target_img, kp1, screen_img, kp2, good, None, **draw_params)
                img3 = cv2.cvtColor(img3, cv2.COLOR_BGR2RGB)
                ImgProcess.show_img(img3)

            if m is not None:
                h, w = target_hw
                pts = float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, m)
                arr = int32(dst)
                pos_arr = arr[0] + (arr[2] - arr[0]) // 2
                return int(pos_arr[0][0]), int(pos_arr[0][1])

        return None
