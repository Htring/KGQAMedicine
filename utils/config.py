#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: juzipi
@file: config.py
@time:2022/07/20
@description:
"""
from configparser import ConfigParser


class SysConfig(object):
    __doc__ = """ system config """

    # 单例，全局唯一
    def __new__(cls, *args, **kwargs):
        if not hasattr(SysConfig, '_instance'):
            SysConfig._instance = object.__new__(cls)
        return SysConfig._instance

    config_parser = ConfigParser()
    config_parser.read("./data/config.ini")
    # neo4j
    NEO4J_HOST = config_parser.get("neo4j", 'host')
    NEO4J_PORT = int(config_parser.get("neo4j", 'port'))
    NEO4J_USER = config_parser.get("neo4j", 'user')
    NEO4J_PASSWORD = config_parser.get('neo4j', 'password')
    # mongodb
    MONGODB_HOST = config_parser.get("mongodb", 'host')
    MONGODB_PORT = int(config_parser.get("mongodb", 'port'))
    MONGODB_USER = config_parser.get("mongodb", 'user')
    MONGODB_PASSWORD = config_parser.get('mongodb', 'password')
    # sys
    DATA_ORIGIN_PATH = config_parser.get("sys", 'origin_data_path')
    DATA_DICT_DIR = config_parser.get("sys", 'data_dict_dir')

