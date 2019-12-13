import pymorphy2
import datetime


def my_split(res, seps):
    #res = [s]
    for sep in seps:
        s, res = res, []
        for seq in s:
            res += seq.split(sep)
    return res


morph = pymorphy2.MorphAnalyzer()

#name = 'кто-то'
#word = morph.tag(name)
#print(morph.normal_forms(name)[0])
#print(morph.tag(name)[0].POS)

date_day = []
date_time = []
sentence_list = []
token = {}
separators = ['.', ',', '*', '"', "'", ':', ';', '!', '?']
ignore_word_type = ['PREP', 'CONJ', 'PRCL', 'INTJ', None]

def parse_sentence(line):
    sentence = []
    ignore_flag = False
    for word in line:
        if ignore_flag:
            ignore_flag = False
            continue
        if word == '#':
            ignore_flag = True
            continue
        if r".com/" not in word:
            word = my_split([word], separators)
            sentence += word
        # print(word, morph.normal_forms(word)[0], morph.tag(word)[0].POS)
    sentence = [morph.normal_forms(word)[0] for word in sentence
                if word != '' and morph.tag(word)[0].POS not in ignore_word_type]
    return sentence


with open("data_utf8.txt", encoding='UTF8') as file:
    for line in file:
        line = line.strip().split()
        if len(line) == 0:
            continue
        date_day = line[0]
        date_time = line[1]
        sentence = parse_sentence(line[2:])
        #sentence_list.append(sentence)
        print(sentence)
#for sentence in sentence_list:
#    print(sentence)
