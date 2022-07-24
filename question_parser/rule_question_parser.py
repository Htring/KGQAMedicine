#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: juzipi
@file: rule_question_parser.py
@time:2022/07/24
@description:
"""


class RuleQuestionParser(object):

    @staticmethod
    def _get_entity_dict(args: dict):
        entity_dict = {}
        for arg, kinds in args.items():
            for kind in kinds:
                entity_dict.setdefault(kind, [])
                entity_dict[kind].append(arg)
        return entity_dict

    def parser(self, classify_res: dict):
        args = classify_res['args']
        entity_dict = self._get_entity_dict(args)
        question_kinds = classify_res['question_kinds']
        sql_list = []
        for question_kind in question_kinds:
            sql_dict = {"question_kind": question_kind}
            if question_kind == "disease_symptom":
                sql = self.sql_transfer(question_kind, entity_dict.get('disease'))
            elif question_kind == "symptom_disease":
                sql = self.sql_transfer(question_kind, entity_dict.get('symptom'))
            elif question_kind == "disease_cause":
                sql = self.sql_transfer(question_kind, entity_dict.get('disease'))
            elif question_kind == "disease_acompany":
                sql = self.sql_transfer(question_kind, entity_dict.get('disease'))
            elif question_kind == "disease_not_food":
                sql = self.sql_transfer(question_kind, entity_dict.get('disease'))
            elif question_kind == "disease_not_food":
                sql = self.sql_transfer(question_kind, entity_dict.get('disease'))
            elif question_kind == "disease_do_food":
                sql = self.sql_transfer(question_kind, entity_dict.get('disease'))
            elif question_kind == "food_not_disease":
                sql = self.sql_transfer(question_kind, entity_dict.get('food'))
            elif question_kind == "food_do_disease":
                sql = self.sql_transfer(question_kind, entity_dict.get('food'))
            elif question_kind == "disease_drug":
                sql = self.sql_transfer(question_kind, entity_dict.get('disease'))
            elif question_kind == "drug_disease":
                sql = self.sql_transfer(question_kind, entity_dict.get('drug'))
            elif question_kind == "disease_check":
                sql = self.sql_transfer(question_kind, entity_dict.get('disease'))
            elif question_kind == "check_disease":
                sql = self.sql_transfer(question_kind, entity_dict.get('check'))
            elif question_kind == "disease_prevent":
                sql = self.sql_transfer(question_kind, entity_dict.get('disease'))
            elif question_kind == "disease_lasttime":
                sql = self.sql_transfer(question_kind, entity_dict.get('disease'))
            elif question_kind == "disease_cureway":
                sql = self.sql_transfer(question_kind, entity_dict.get('disease'))
            elif question_kind == "disease_cureprob":
                sql = self.sql_transfer(question_kind, entity_dict.get('disease'))
            elif question_kind == "disease_easyget":
                sql = self.sql_transfer(question_kind, entity_dict.get('disease'))
            elif question_kind == "disease_desc":
                sql = self.sql_transfer(question_kind, entity_dict.get('disease'))
            else:
                sql = []
            if sql:
                sql_dict['sql'] = sql
                sql_list.append(sql_dict)
        return sql_list

    def sql_transfer(self, question_kind, entities):
        if not entities:
            return []
        # query disease cause
        if question_kind == 'disease_cause':
            sql = ["MATCH (m: Disease) where m.name = '{}' return m.name, m.cause".format(i) for i in entities]
        elif question_kind == "disease_prevent":
            sql = ["MATCH (m: Disease) where m.name = '{}' return m.name, m.prevent".format(i) for i in entities]
        elif question_kind == "disease_lasttime":
            sql = ["MATCH (m: Disease) where m.name = '{}' return m.name, m.cure_lasttime".format(i) for i in entities]
        elif question_kind == "disease_cureprob":
            sql = ["MATCH (m: Disease) where m.name = '{}' return m.name, m.cured_prob".format(i) for i in entities]
        elif question_kind == "disease_cureway":
            sql = ["MATCH (m: Disease) where m.name = '{}' return m.name, m.cure_way".format(i) for i in entities]
        elif question_kind == "disease_easyget":
            sql = ["MATCH (m: Disease) where m.name = '{}' return m.name, m.easy_get".format(i) for i in entities]
        elif question_kind == "disease_desc":
            sql = ["MATCH (m: Disease) where m.name = '{}' return m.name, m.desc".format(i) for i in entities]
        elif question_kind == "disease_symptom":
            sql = [
                "MATCH (m: Disease)-[r: has_symptom]-> (n:Symptom) where m.name='{}' return m.name, r.name, n.name".format(
                    i) for i in entities]
        elif question_kind == "symptom_disease":
            sql = [
                "MATCH (m: Disease)-[r: has_symptom]-> (n:Symptom) where n.name='{}' return m.name, r.name, n.name".format(
                    i) for i in entities]
        elif question_kind == "disease_acompany":
            sql1 = [
                "MATCH (m: Disease)-[r: acompany_with]-> (n: Disease) where m.name='{}' return m.name, r.name, n.mame".format(
                    i) for i in entities]
            sql2 = [
                "MATCH (m: Disease)-[r: acompany_with]-> (n: Disease) where n.name='{}' return m.name, r.name, n.mame".format(
                    i) for i in entities]
            sql = sql1 + sql2
        elif question_kind == 'disease_not_food':
            sql = ["MATCH (m:Disease)-[r:no_eat]->(n:Food) where m.name = '{0}' return m.name, r.name, n.name".format(i)
                   for i in entities]
        elif question_kind == 'disease_do_food':
            sql1 = [
                "MATCH (m:Disease)-[r:do_eat]->(n:Food) where m.name = '{0}' return m.name, r.name, n.name".format(i)
                for i in entities]
            sql2 = [
                "MATCH (m:Disease)-[r:recommand_eat]->(n:Food) where m.name = '{0}' return m.name, r.name, n.name".format(
                    i) for i in entities]
            sql = sql1 + sql2
        elif question_kind == 'food_not_disease':
            sql = ["MATCH (m:Disease)-[r:no_eat]->(n:Food) where n.name = '{0}' return m.name, r.name, n.name".format(i)
                   for i in entities]
        elif question_kind == 'food_do_disease':
            sql1 = [
                "MATCH (m:Disease)-[r:do_eat]->(n:Food) where n.name = '{0}' return m.name, r.name, n.name".format(i)
                for i in entities]
            sql2 = [
                "MATCH (m:Disease)-[r:recommand_eat]->(n:Food) where n.name = '{0}' return m.name, r.name, n.name".format(
                    i) for i in entities]
            sql = sql1 + sql2
        elif question_kind == 'disease_drug':
            sql1 = [
                "MATCH (m:Disease)-[r:common_drug]->(n:Drug) where m.name = '{0}' return m.name, r.name, n.name".format(
                    i) for i in entities]
            sql2 = [
                "MATCH (m:Disease)-[r:recommand_drug]->(n:Drug) where m.name = '{0}' return m.name, r.name, n.name".format(
                    i) for i in entities]
            sql = sql1 + sql2
        elif question_kind == 'drug_disease':
            sql1 = [
                "MATCH (m:Disease)-[r:common_drug]->(n:Drug) where n.name = '{0}' return m.name, r.name, n.name".format(
                    i) for i in entities]
            sql2 = [
                "MATCH (m:Disease)-[r:recommand_drug]->(n:Drug) where n.name = '{0}' return m.name, r.name, n.name".format(
                    i) for i in entities]
            sql = sql1 + sql2
        elif question_kind == 'disease_check':
            sql = [
                "MATCH (m:Disease)-[r:need_check]->(n:Check) where m.name = '{0}' return m.name, r.name, n.name".format(
                    i) for i in entities]
        elif question_kind == 'check_disease':
            sql = [
                "MATCH (m:Disease)-[r:need_check]->(n:Check) where n.name = '{0}' return m.name, r.name, n.name".format(
                    i) for i in entities]
        else:
            sql = []
        return sql
