# coding=utf-8
import os
os.environ['PYPINYIN_NO_PHRASES'] = 'true'
import jieba
import jieba.analyse
import pypinyin 


def convert_to_pinyin(words):
    pinyin_words = pypinyin.pinyin(words)
    pinyin = ''
    for word in pinyin_words:
        pinyin = pinyin + word[0]

    return pinyin

def convert_to_lazy_pinyin(words):
    pinyin_words = pypinyin.lazy_pinyin(words)
    pinyin = ''
    for word in pinyin_words:
        pinyin = pinyin + word

    return pinyin

if __name__=='__main__':
    print(convert_to_lazy_pinyin('剑——罪渊'))
    print(convert_to_pinyin('廖雪峰的 python 教程,为学生量身定制python课程,零基础轻松入门.实战课程应有尽有7天快速入手,30天运用自如.简单易懂测试'))



