#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author: juzipi
@file: chatbot.py
@time:2022/07/24
@description:
"""

from question_classify.rule_question_classify import RuleQuestionClassifier
from question_parser.rule_question_parser import RuleQuestionParser
from answer_search.raw_answer_search import RawAnswerSearcher


class ChatBot(object):

    def __init__(self):
        self.classifier = RuleQuestionClassifier()
        self.parser = RuleQuestionParser()
        self.answer_generate = RawAnswerSearcher()
        self.common_answer = "您好，我是科皮子菊的医药私人助手，希望可以为您解答。如果答案不满意，可以通过：https://github.com/Htring 联系我哦。祝您身体健康，远离我哦！"

    def answer(self, question):
        question_classify = self.classifier.classify(question)
        if not question_classify:
            return self.common_answer
        res_sql = self.parser.parser(question_classify)
        final_answers = self.answer_generate.search(res_sql)
        if not final_answers:
            return self.common_answer
        else:
            return "\n".join(final_answers)


if __name__ == '__main__':
    chat_bot = ChatBot()
    while True:
        question = input("用户：")
        answer = chat_bot.answer(question)
        print("科皮子菊：", answer)
