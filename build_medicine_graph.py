#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: juzipi
@file: build_medicine_graph.py
@time:2022/07/20
@description:
"""
from get_data.build_graph import MedicalGraph

if __name__ == '__main__':
    mg = MedicalGraph()
    mg.create_graph_nodes()
    mg.create_graph_relations()
    mg.export_data_dict()
