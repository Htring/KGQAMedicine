#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: juzipi
@file: rule_question_classify.py
@time:2022/07/23
@description:
"""
import os
import ahocorasick
import tqdm
from utils.config import SysConfig


class RuleQuestionClassifier(object):
    disease_feature_words = []
    department_feature_words = []
    check_feature_words = []
    drug_feature_words = []
    food_feature_words = []
    producer_feature_words = []
    symptom_feature_words = []
    region_feature_words = set()
    deny_feature_words = []

    # 问句疑问词
    symptom_qwds = ['症状', '表征', '现象', '症候', '表现']
    cause_qwds = ['原因', '成因', '为什么', '怎么会', '怎样才', '咋样才', '怎样会', '如何会', '为啥', '为何', '如何才会', '怎么才会', '会导致', '会造成']
    acompany_qwds = ['并发症', '并发', '一起发生', '一并发生', '一起出现', '一并出现', '一同发生', '一同出现', '伴随发生', '伴随', '共现']
    food_qwds = ['饮食', '饮用', '吃', '食', '伙食', '膳食', '喝', '菜', '忌口', '补品', '保健品', '食谱', '菜谱', '食用', '食物', '补品']
    drug_qwds = ['药', '药品', '用药', '胶囊', '口服液', '炎片']
    prevent_qwds = ['预防', '防范', '抵制', '抵御', '防止', '躲避', '逃避', '避开', '免得', '逃开', '避开', '避掉', '躲开', '躲掉', '绕开',
                    '怎样才能不', '怎么才能不', '咋样才能不', '咋才能不', '如何才能不', '怎样才不', '怎么才不', '咋样才不', '咋才不',
                    '如何才不', '怎样才可以不', '怎么才可以不', '咋样才可以不', '咋才可以不', '如何可以不', '怎样才可不', '怎么才可不',
                    '咋样才可不', '咋才可不', '如何可不']
    lasttime_qwds = ['周期', '多久', '多长时间', '多少时间', '几天', '几年', '多少天', '多少小时', '几个小时', '多少年']
    cureway_qwds = ['怎么治疗', '如何医治', '怎么医治', '怎么治', '怎么医', '如何治', '医治方式', '疗法', '咋治', '怎么办', '咋办', '咋治']
    cureprob_qwds = ['多大概率能治好', '多大几率能治好', '治好希望大么', '几率', '几成', '比例', '可能性', '能治', '可治', '可以治', '可以医']
    easyget_qwds = ['易感人群', '容易感染', '易发人群', '什么人', '哪些人', '感染', '染上', '得上']
    check_qwds = ['检查', '检查项目', '查出', '检查', '测出', '试出']
    belong_qwds = ['属于什么科', '属于', '什么科', '科室']
    cure_qwds = ['治疗什么', '治啥', '治疗啥', '医治啥', '治愈啥', '主治啥', '主治什么', '有什么用', '有何用', '用处', '用途',
                 '有什么好处', '有什么益处', '有何益处', '用来', '用来做啥', '用来作甚', '需要', '要']

    def __init__(self):
        self.region_actree = None
        self.word_kind_dict = None
        self._init()

    @staticmethod
    def _load_line_file(file_path):
        print(f"load file {file_path}")
        data_list = []
        with open(file_path, 'r', encoding='utf8') as reader:
            for line in reader:
                if not line.strip():
                    continue
                data_list.append(line.strip())
        return data_list

    def _init(self):
        # load data
        file_list = ["disease", "department", "check", "drug", "food", "producer", "symptom", "deny"]
        for index, file_path in enumerate(file_list):
            data_list = self._load_line_file(os.path.join(SysConfig.DATA_DICT_DIR, file_path + ".txt"))
            setattr(self, file_path + "_feature_words", data_list)
            self.region_feature_words.update(data_list)
        # build actree
        self.region_actree = self._get_actree(list(self.region_feature_words))
        # build word kind dict
        self._build_word_kind_dict()
        print("object init over")

    def _build_word_kind_dict(self):
        word_kind_dict = {}
        for word in tqdm.tqdm(self.region_feature_words, desc='building word kind dict'):
            word_kind_dict.setdefault(word, [])
            if word in self.disease_feature_words:
                word_kind_dict[word].append("disease")
            if word in self.department_feature_words:
                word_kind_dict[word].append("department")
            if word in self.check_feature_words:
                word_kind_dict[word].append("check")
            if word in self.drug_feature_words:
                word_kind_dict[word].append("drug")
            if word in self.food_feature_words:
                word_kind_dict[word].append("food")
            if word in self.symptom_feature_words:
                word_kind_dict[word].append("symptom")
            if word in self.producer_feature_words:
                word_kind_dict[word].append("producer")
        self.word_kind_dict = word_kind_dict

    @staticmethod
    def _get_actree(key_list):
        actree = ahocorasick.Automaton()
        for index, word in enumerate(key_list):
            actree.add_word(word, (index, word))
        actree.make_automaton()
        return actree

    def classify(self, question):
        classify_res = {}
        medical_dict = self.check_query(question)
        if not medical_dict:
            return {}
        classify_res['args'] = medical_dict
        region_word_kinds = []
        for kinds in medical_dict.values():
            region_word_kinds.extend(kinds)
        question_kinds = []
        # disease symptom
        self.sub_classify(self.symptom_qwds, question, 'disease', region_word_kinds, question_kinds, "disease_symptom")
        # symptom disease
        self.sub_classify(self.symptom_qwds, question, 'symptom', region_word_kinds, question_kinds, "symptom_disease")
        # disease cause
        self.sub_classify(self.cause_qwds, question, 'disease', region_word_kinds, question_kinds, "disease_cause")
        # disease accompany
        self.sub_classify(self.acompany_qwds, question, 'disease', region_word_kinds, question_kinds,
                          "disease_accompany")
        # disease food
        if self.check_words(self.food_qwds, question) and 'disease' in region_word_kinds:
            deny_status = self.check_words(self.deny_feature_words, question)
            if deny_status:
                question_kind = "disease_not_food"
            else:
                question_kind = "disease_do_food"
            question_kinds.append(question_kind)
        # food disease
        if self.check_words(self.food_qwds + self.cure_qwds, question) and 'food' in region_word_kinds:
            deny_status = self.check_words(self.deny_feature_words, question)
            if deny_status:
                question_kind = 'food_not_disease'
            else:
                question_kind = 'food_do_disease'
            question_kinds.append(question_kind)
        # disease_drug
        self.sub_classify(self.drug_qwds, question, 'disease', region_word_kinds, question_kinds, "disease_drug")
        # drug disease
        self.sub_classify(self.cure_qwds, question, 'drug', region_word_kinds, question_kinds, "drug_disease")
        # disease check
        self.sub_classify(self.check_qwds, question, 'disease', region_word_kinds, question_kinds, "disease_check")
        # check disease
        self.sub_classify(self.check_qwds + self.cure_qwds, question, 'check', region_word_kinds, question_kinds,
                          "check_disease")
        # disease prevent
        self.sub_classify(self.prevent_qwds, question, 'disease', region_word_kinds, question_kinds, "disease_prevent")
        # disease last time
        self.sub_classify(self.lasttime_qwds, question, 'disease', region_word_kinds, question_kinds,
                          "disease_lasttime")
        # disease cure way
        self.sub_classify(self.cureway_qwds, question, 'disease', region_word_kinds, question_kinds, "disease_cureway")
        # disease cure prob
        self.sub_classify(self.cureprob_qwds, question, 'disease', region_word_kinds, question_kinds,
                          "disease_cureprob")
        # disease easy get
        self.sub_classify(self.easyget_qwds, question, 'disease', region_word_kinds, question_kinds, "disease_easyget")
        # others deal
        if question_kinds == [] and 'disease' in region_word_kinds:
            question_kinds.append('disease_desc')
        if question_kinds == [] and 'symptom' in region_word_kinds:
            question_kinds.append('symptom_disease')

        classify_res['question_kinds'] = question_kinds
        return classify_res

    def sub_classify(self, kind_qkwds, question, key, region_word_kinds, question_kinds, kind_type):
        # print(f"question {question}, key {key} kind_type {kind_type}")
        # print(self.check_words(kind_qkwds, question))
        # print(key in region_word_kinds)
        if self.check_words(kind_qkwds, question) and (key in region_word_kinds):
            question_kinds.append(kind_type)

    @staticmethod
    def check_words(kws, question):
        for kw in kws:
            if kw in question:
                return True
        return False

    def check_query(self, question):
        region_feature_words = []
        for i in self.region_actree.iter(question):
            feature_word = i[1][1]
            region_feature_words.append(feature_word)
        inner_words = []
        for i in range(len(region_feature_words)):
            wi = region_feature_words[i]
            for j in range(i + 1, len(region_feature_words)):
                wj = region_feature_words[j]
                if wi in wj and wi != wj:
                    inner_words.append(wi)
        final_dict = {word: self.word_kind_dict.get(word) for word in filter(lambda x: x not in inner_words, region_feature_words)}
        return final_dict

