import pymorphy2
from datetime import datetime

morph = pymorphy2.MorphAnalyzer()


def my_split(res, seps):
    for sep in seps:
        s, res = res, []
        for seq in s:
            res += seq.split(sep)
    return res


sentence_list = []

total_words = 0
total_twits = 0
count_words = {}
freq_in_twits = {}
twits_length = {}

separators = ['.', ',', '*', '"', "'", ':', ';', '!', '?', '@']
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


class SentenceNote:
    def __init__(self, line):
        line = line.split()
        day = list(map(int, line[0].split('-')))
        time = list(map(int, line[1].split(':')))
        self.time = datetime(day=day[2], month=day[1], year=day[0], hour=time[0], minute=time[1])
        raw_sentence = parse_sentence(line[2:])
        self.size = len(raw_sentence)
        self.used_words = {}
        for word in raw_sentence:
            if self.used_words.get(word, 0) == 0:
                self.used_words[word] = 0
            self.used_words[word] += 1

    def __str__(self):
        return "    ".join([str(self.time), str(self.used_words.items())])

    def __repr__(self):
        return self.__str__()


with open("data_utf8.txt", encoding='UTF8') as file:
    for line in file:
        line = line.strip()
        if len(line) == 0:
            continue
        sentence = SentenceNote(line)
        sentence_list.append(sentence)

total_twits = len(sentence_list)

for sentence in sentence_list:
    total_words += sentence.size
    if twits_length.get(sentence.size, 0) == 0:
        twits_length[sentence.size] = 0
    twits_length[sentence.size] += 1

    for word, count in sentence.used_words.items():
        if count_words.get(word, 0) == 0:
            count_words[word] = 0
        count_words[word] += count
        if freq_in_twits.get(word, 0) == 0:
            freq_in_twits[word] = 0
        freq_in_twits[word] += 1

file = open("frequency.txt", 'w', encoding='UTF8')
for word, cnt in sorted(freq_in_twits.items(), key= lambda x: x[1], reverse = True):
    print("%s - %d - %.3f%%" % (word, freq_in_twits[word], freq_in_twits[word]/total_twits*100), file=file)
file.close()

file = open("twits_length.txt", 'w', encoding='UTF8')
sum = 0
for length, cnt in sorted(twits_length.items(), key= lambda x: x[1], reverse = True):
    sum += cnt
    print("%d - %d - %.3f%%" % (length, cnt, cnt/total_twits*100), file= file)
file.close()
sum == total_twits

file = open("word_score.txt", 'w', encoding='UTF8')
for word, cnt in sorted(freq_in_twits.items(), key= lambda x: x[1], reverse = True):
    print(word, "" if freq_in_twits[word] > 1 else 0, file=file)
file.close()
