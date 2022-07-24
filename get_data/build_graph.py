#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: juzipi
@file: build_graph.py
@time:2022/07/23
@description:
"""
import json
import os
import tqdm
from py2neo import Graph, Node
from utils.config import SysConfig


class MedicalGraph(object):

    def __init__(self):
        self.data_path = SysConfig.DATA_ORIGIN_PATH
        self.graph = Graph(SysConfig.NEO4J_HOST + ":" + str(SysConfig.NEO4J_PORT), auth=(SysConfig.NEO4J_USER,
                                                                                         SysConfig.NEO4J_PASSWORD))
        self.raw_graph_data = None

    def _read_nodes(self):
        # 共７类节点
        drugs = []  # 药品
        foods = []  # 食物
        checks = []  # 检查
        departments = []  # 科室
        producers = []  # 药品大类
        diseases = []  # 疾病
        symptoms = []  # 症状
        disease_infos = []  # 疾病信息
        # 构建节点实体关系
        relation_department_department = []  # 科室－科室关系
        relation_diseases_noteat = []  # 疾病－忌吃食物关系
        relation_diseases_doeat = []  # 疾病－宜吃食物关系
        relation_diseases_recommandeat = []  # 疾病－推荐吃食物关系
        relation_diseases_commonddrug = []  # 疾病－通用药品关系
        rels_recommanddrug = []  # 疾病－热门药品关系
        rels_check = []  # 疾病－检查关系
        relation_drug_producer = []  # 厂商－药物关系

        rels_symptom = []  # 疾病症状关系
        rels_acompany = []  # 疾病并发关系
        rels_category = []  # 疾病与科室之间的关系

        with open(self.data_path, 'r', encoding='utf8') as reader:
            for data in tqdm.tqdm(reader, desc=f"reading {self.data_path} fle"):
                disease_dict = {}
                data_json = json.loads(data)
                disease = data_json['name']
                disease_dict['name'] = disease
                diseases.append(disease)
                disease_dict['desc'] = ''
                disease_dict['prevent'] = ''
                disease_dict['cause'] = ''
                disease_dict['easy_get'] = ''
                disease_dict['cure_department'] = ''
                disease_dict['cure_way'] = ''
                disease_dict['cure_lasttime'] = ''
                disease_dict['symptom'] = ''
                disease_dict['cured_prob'] = ''

                if 'symptom' in data_json:
                    symptoms += data_json['symptom']
                    for symptom in data_json['symptom']:
                        rels_symptom.append([disease, symptom])

                if 'acompany' in data_json:
                    for acompany in data_json['acompany']:
                        rels_acompany.append([disease, acompany])

                if 'desc' in data_json:
                    disease_dict['desc'] = data_json['desc']

                if 'prevent' in data_json:
                    disease_dict['prevent'] = data_json['prevent']

                if 'cause' in data_json:
                    disease_dict['cause'] = data_json['cause']

                if 'get_prob' in data_json:
                    disease_dict['get_prob'] = data_json['get_prob']

                if 'easy_get' in data_json:
                    disease_dict['easy_get'] = data_json['easy_get']

                if 'cure_department' in data_json:
                    cure_department = data_json['cure_department']
                    if len(cure_department) == 1:
                        rels_category.append([disease, cure_department[0]])
                    if len(cure_department) == 2:
                        big = cure_department[0]
                        small = cure_department[1]
                        relation_department_department.append([small, big])
                        rels_category.append([disease, small])

                    disease_dict['cure_department'] = cure_department
                    departments += cure_department

                if 'cure_way' in data_json:
                    disease_dict['cure_way'] = data_json['cure_way']

                if 'cure_lasttime' in data_json:
                    disease_dict['cure_lasttime'] = data_json['cure_lasttime']

                if 'cured_prob' in data_json:
                    disease_dict['cured_prob'] = data_json['cured_prob']

                if 'common_drug' in data_json:
                    common_drug = data_json['common_drug']
                    for drug in common_drug:
                        relation_diseases_commonddrug.append([disease, drug])
                    drugs += common_drug

                if 'recommand_drug' in data_json:
                    recommand_drug = data_json['recommand_drug']
                    drugs += recommand_drug
                    for drug in recommand_drug:
                        rels_recommanddrug.append([disease, drug])

                if 'not_eat' in data_json:
                    not_eat = data_json['not_eat']
                    for _not in not_eat:
                        relation_diseases_noteat.append([disease, _not])

                    foods += not_eat
                    do_eat = data_json['do_eat']
                    for _do in do_eat:
                        relation_diseases_doeat.append([disease, _do])

                    foods += do_eat
                    recommand_eat = data_json['recommand_eat']

                    for _recommand in recommand_eat:
                        relation_diseases_recommandeat.append([disease, _recommand])
                    foods += recommand_eat

                if 'check' in data_json:
                    check = data_json['check']
                    for _check in check:
                        rels_check.append([disease, _check])
                    checks += check
                if 'drug_detail' in data_json:
                    drug_detail = data_json['drug_detail']
                    producer = [i.split('(')[0] for i in drug_detail]
                    relation_drug_producer += [[i.split('(')[0], i.split('(')[-1].replace(')', '')] for i in drug_detail]
                    producers += producer
                disease_infos.append(disease_dict)
        return set(drugs), set(foods), set(checks), set(departments), set(producers), set(symptoms), set(diseases), disease_infos, \
               rels_check, relation_diseases_recommandeat, relation_diseases_noteat, relation_diseases_doeat, relation_department_department, relation_diseases_commonddrug, relation_drug_producer, rels_recommanddrug, \
               rels_symptom, rels_acompany, rels_category

    def create_graph_nodes(self):
        if self.raw_graph_data is None:
            self.raw_graph_data = self._read_nodes()
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases, disease_infos = self.raw_graph_data[: 8]
        self.create_diseases_nodes(disease_infos)
        self.create_node('Drug', Drugs)
        self.create_node('Food', Foods)
        self.create_node('Check', Checks)
        self.create_node('Department', Departments)
        self.create_node('Producer', Producers)
        self.create_node('Symptom', Symptoms)

    def create_node(self, label, nodes):
        for node_name in tqdm.tqdm(nodes, desc=f"creating {label} nodes"):
            node = Node(label, name=node_name)
            self.graph.create(node)

    def create_diseases_nodes(self, disease_infos):
        """
        创建知识图谱中心疾病的节点
        :param disease_infos:
        :return:
        """
        for disease_dict in tqdm.tqdm(disease_infos, desc="creating diseases nodes"):
            node = Node("Disease", name=disease_dict['name'], desc=disease_dict['desc'],
                        prevent=disease_dict['prevent'], cause=disease_dict['cause'],
                        easy_get=disease_dict['easy_get'], cure_lasttime=disease_dict['cure_lasttime'],
                        cure_department=disease_dict['cure_department']
                        , cure_way=disease_dict['cure_way'], cured_prob=disease_dict['cured_prob'])
            self.graph.create(node)

    def create_graph_relations(self):
        if self.raw_graph_data is None:
            self.raw_graph_data = self._read_nodes()
        rels_check, rels_recommandeat, rels_noteat, rels_doeat, rels_department, rels_commonddrug, rels_drug_producer, rels_recommanddrug, rels_symptom, rels_acompany, rels_category = self.raw_graph_data[
                                                                                                                                                                                        8:]
        self.create_relationship('Disease', 'Food', rels_recommandeat, 'recommand_eat', '推荐食谱')
        self.create_relationship('Disease', 'Food', rels_noteat, 'no_eat', '忌吃')
        self.create_relationship('Disease', 'Food', rels_doeat, 'do_eat', '宜吃')
        self.create_relationship('Department', 'Department', rels_department, 'belongs_to', '属于')
        self.create_relationship('Disease', 'Drug', rels_commonddrug, 'common_drug', '常用药品')
        self.create_relationship('Producer', 'Drug', rels_drug_producer, 'drugs_of', '生产药品')
        self.create_relationship('Disease', 'Drug', rels_recommanddrug, 'recommand_drug', '好评药品')
        self.create_relationship('Disease', 'Check', rels_check, 'need_check', '诊断检查')
        self.create_relationship('Disease', 'Symptom', rels_symptom, 'has_symptom', '症状')
        self.create_relationship('Disease', 'Disease', rels_acompany, 'acompany_with', '并发症')
        self.create_relationship('Disease', 'Department', rels_category, 'belongs_to', '所属科室')

    def create_relationship(self, start_node, end_node, edges, rel_type, rel_name):
        """
        创建关系
        :param start_node:
        :param end_node:
        :param edges:
        :param rel_type:
        :param rel_name:
        :return:
        """
        # 去重处理
        set_edges = []
        for edge in edges:
            set_edges.append('###'.join(edge))
        for edge in tqdm.tqdm(set(set_edges), desc=f"building edge {start_node} - {end_node} rel type {rel_type} rel name {rel_name}"):
            edge = edge.split('###')
            p = edge[0]
            q = edge[1]
            query = "match(p:%s),(q:%s) where p.name='%s'and q.name='%s' create (p)-[rel:%s{name:'%s'}]->(q)" % (
                start_node, end_node, p, q, rel_type, rel_name)
            try:
                self.graph.run(query)
            except Exception as e:
                print(e)

    @staticmethod
    def _write(file_path, data_list):
        with open(file_path, 'w', encoding='utf8') as writer:
            writer.write("\n".join(data_list))

    def export_data_dict(self):
        if self.raw_graph_data is None:
            self.raw_graph_data = self._read_nodes()
        Drugs, Foods, Checks, Departments, Producers, Symptoms, Diseases = self.raw_graph_data[: 7]
        self._write(os.path.join(SysConfig.DATA_DICT_DIR, "drug.txt"), list(Drugs))
        self._write(os.path.join(SysConfig.DATA_DICT_DIR, "food.txt"), list(Foods))
        self._write(os.path.join(SysConfig.DATA_DICT_DIR, "check.txt"), list(Checks))
        self._write(os.path.join(SysConfig.DATA_DICT_DIR, "department.txt"), list(Departments))
        self._write(os.path.join(SysConfig.DATA_DICT_DIR, "producer.txt"), list(Producers))
        self._write(os.path.join(SysConfig.DATA_DICT_DIR, "symptom.txt"), list(Symptoms))
        self._write(os.path.join(SysConfig.DATA_DICT_DIR, "disease.txt"), list(Diseases))
