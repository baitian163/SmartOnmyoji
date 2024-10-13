# -*- coding: utf-8 -*-
# @Link    : https://github.com/aicezam/SmartOnmyoji
# @Version : Python3.7.6
# @MIT License Copyright (c) 2022 ACE

from configparser import ConfigParser
from os.path import abspath, dirname, exists
from typing import List, Any


class ReadConfigFile:
    def __init__(self):
        self.file_path = abspath(dirname(dirname(__file__))) + r'/modules/config.ini'

    def read_config_ui_info(self) -> List[Any]:
        config_ini = ConfigParser()

        if not exists(self.file_path):
            raise FileNotFoundError("配置文件不存在！")

        config_ini.read(self.file_path, encoding="utf-8-sig")

        return [
            config_ini.get('ui_info', 'connect_mod'),
            config_ini.get('ui_info', 'target_path_mode'),
            config_ini.get('ui_info', 'handle_title'),
            int(config_ini.get('ui_info', 'click_deviation')),
            float(config_ini.get('ui_info', 'interval_seconds')),
            float(config_ini.get('ui_info', 'loop_min')),
            float(config_ini.get('ui_info', 'img_compress_val')),
            config_ini.get('ui_info', 'match_method'),
            config_ini.get('ui_info', 'run_mode'),
            config_ini.get('ui_info', 'custom_target_path'),
            config_ini.get('ui_info', 'process_num'),
            config_ini.get('ui_info', 'handle_num'),
            config_ini.get('ui_info', 'if_end'),
            self.str_to_bool(config_ini.get('ui_info', 'debug_status')),
            self.str_to_bool(config_ini.get('ui_info', 'set_priority_status')),
            float(config_ini.get('ui_info', 'interval_seconds_max')),
            config_ini.get('other_setting', 'screen_scale_rate'),
            config_ini.get('ui_info', 'times_mode')
        ]

    def read_config_target_path_files_name(self) -> List[List[str]]:
        config_ini = ConfigParser()

        if not exists(self.file_path):
            raise FileNotFoundError("配置文件不存在！")

        config_ini.read(self.file_path, encoding="utf-8-sig")

        return [config_ini.get('target_path_files_name', f'file_name_{i}').split(",") for i in range(7)]

    def read_config_other_setting(self) -> List[Any]:
        config_ini = ConfigParser()

        if not exists(self.file_path):
            raise FileNotFoundError("配置文件不存在！")

        config_ini.read(self.file_path, encoding="utf-8-sig")

        return [
            self.str_to_bool(config_ini.get('other_setting', 'save_ui_info_in_config')),
            self.str_to_bool(config_ini.get('other_setting', 'playtime_warming_status')),
            self.str_to_bool(config_ini.get('other_setting', 'success_times_warming_status')),
            config_ini.get('other_setting', 'success_times_warming_times'),
            config_ini.get('other_setting', 'success_times_warming_waiting_seconds').split(","),
            self.str_to_bool(config_ini.get('other_setting', 'debug_status_show_pics')),
            config_ini.get('other_setting', 'set_priority_num'),
            self.str_to_bool(config_ini.get('other_setting', 'play_sound_status')),
            self.str_to_bool(config_ini.get('other_setting', 'adb_wifi_status')),
            config_ini.get('other_setting', 'adb_wifi_ip'),
            config_ini.get('other_setting', 'ex_click'),
            config_ini.get('other_setting', 'screen_scale_rate'),
            self.str_to_bool(config_ini.get('other_setting', 'if_match_then_stop')),
            config_ini.get('other_setting', 'stop_target_img_name').split(","),
            self.str_to_bool(config_ini.get('other_setting', 'if_match_5times_stop')),
            self.str_to_bool(config_ini.get('other_setting', 'save_click_log')),
            int(config_ini.get('other_setting', 'target_deviation')),
            config_ini.get('other_setting', 'success_match_then_wait').split(",")
        ]

    def writ_config_ui_info(self, info: List[str]) -> None:
        config_ini = ConfigParser(comment_prefixes='/', allow_no_value=True)

        if not exists(self.file_path):
            raise FileNotFoundError("配置文件不存在！")

        for i in range(len(info)):
            info[i] = str(info[i])

        config_ini.read(self.file_path, encoding="utf-8-sig")

        config_ini.set("ui_info", "connect_mod", info[0])
        config_ini.set("ui_info", "target_path_mode", info[1])
        config_ini.set("ui_info", "handle_title", info[2])
        config_ini.set("ui_info", "click_deviation", info[3])
        config_ini.set("ui_info", "interval_seconds", info[4])
        config_ini.set("ui_info", "loop_min", info[5])
        config_ini.set("ui_info", "img_compress_val", info[6])
        config_ini.set("ui_info", "match_method", info[7])
        config_ini.set("ui_info", "run_mode", info[8])
        config_ini.set("ui_info", "custom_target_path", info[9])
        config_ini.set("ui_info", "process_num", info[10])
        config_ini.set("ui_info", "handle_num", info[11])
        config_ini.set("ui_info", "if_end", info[12])
        config_ini.set("ui_info", "debug_status", info[13])
        config_ini.set("ui_info", "set_priority_status", info[14])
        config_ini.set("ui_info", "interval_seconds_max", info[15])
        config_ini.set("other_setting", "screen_scale_rate", info[16])
        config_ini.set("ui_info", "times_mode", info[17])

        with open(self.file_path, 'w', encoding="utf-8") as configfile:
            config_ini.write(configfile)

    @staticmethod
    def str_to_bool(str_val: str) -> bool:
        return str_val.lower() == 'true'
