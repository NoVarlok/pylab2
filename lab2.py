import pymorphy2
from datetime import datetime
import matplotlib.pyplot as mpt

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
word_estimations = {}

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


class SentenceNote:
    def __init__(self, line):
        self.estimation = 0
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

# file = open("word_score_no.txt", 'w', encoding='UTF8')
# for word, cnt in sorted(freq_in_twits.items(), key= lambda x: x[1], reverse = True):
#     print(word, "" if freq_in_twits[word] > 1 else 0, file=file)
# file.close()

with open("estimations.txt", encoding='UTF8') as file:
    for line in file:
        line = line.strip().split()
        if(len(line) == 1) : print(line)
        word, score = line[0], int(line[1])
        word_estimations[word] = score

with open('classifications.txt.', 'w', encoding='UTF8') as file:
    pass

for sentence in sentence_list:
    for word, number in sentence.used_words.items():
        sentence.estimation += word_estimations.get(word, 0) * number

rule_1 = {'bad_sentences':0, 'neutral_sentences':0,'good_sentences':0}
for sentence in sentence_list:
    if sentence.estimation < -1:
        rule_1['bad_sentences'] += 1
    elif sentence.estimation <= 1:
        rule_1['neutral_sentences'] += 1
    else :
        rule_1['good_sentences'] += 1
print(rule_1)

with open('classifications.txt.', 'a+', encoding='UTF8') as file:
    print('Rule 1:', file= file)
    for classification, number in rule_1.items():
        print('%s - %d - %.3f%%' % (classification, number, 100*number/total_twits), file= file)
    print(file=file)

mpt.bar(x=[-1,0,1], height = rule_1.values(), align ='center', color=['red', 'yellow', 'green'],
        tick_label = ['bad', 'neutral', 'good'])

rule_2 = {'bad_sentences':0, 'neutral_sentences':0,'good_sentences':0}
for sentence in sentence_list:
    if sentence.estimation < 0:
        rule_2['bad_sentences'] += 1
    elif sentence.estimation == 0:
        rule_2['neutral_sentences'] += 1
    else :
        rule_2['good_sentences'] += 1
print(rule_2)

with open('classifications.txt.', 'a+', encoding='UTF8') as file:
    print('Rule 2:', file= file)
    for classification, number in rule_2.items():
        print('%s - %d - %.3f%%' % (classification, number, 100*number/total_twits), file= file)
    print(file=file)
mpt.bar(x=[-1,0,1], height = rule_2.values(), align ='center', color=['red', 'yellow', 'green'],
        tick_label = ['bad', 'neutral', 'good'])

possitive_list = []
negative_list = []
with open('estimations.txt', encoding='UTF8') as file:
    for line in file:
        line = line.strip().split()
        word = line[0]
        word_estimation = int(line[1])
        if morph.tag(word)[0].POS == 'ADJF':
            if word_estimation == 1 and len(possitive_list) < 5:
                possitive_list.append(word)
            if word_estimation == -1 and len(negative_list) < 5:
                negative_list.append(word)
with open('adjectives.txt.', 'w', encoding='UTF8') as file:
    print('Top-5 Positive:', file=file)
    for word in possitive_list:
        print('%s - %d - %.3f%%' % (word, freq_in_twits[word], 100 * freq_in_twits[word] / total_twits), file=file)
    print(file=file)

    print('Top-5 Negative:', file=file)
    for word in negative_list:
        print('%s - %d - %.3f%%' % (word, freq_in_twits[word], 100 * freq_in_twits[word] / total_twits), file=file)
    print(file=file)

# outset = set(sentence_list)
# for obj in sorted(outset, key= lambda x: x.time):
#     print(obj.time)

empirical_estimation = {}
accuracy = 0

for word in freq_in_twits:
    empirical_estimation[word] = 0

for sentence in sentence_list:
    for word in sentence.used_words:
        empirical_estimation[word] += sentence.estimation

for word in freq_in_twits:
    empirical_estimation[word] /= count_words[word]

deviation = {}

for word in freq_in_twits:
    deviation[word] = abs(word_estimations[word] - empirical_estimation[word])
    if deviation[word] <= 1 or (word_estimations[word] > 0 and empirical_estimation[word] > 0) or (
            word_estimations[word] < 0 and empirical_estimation[word] < 0):
        accuracy += 1

# deviation_list = sorted(deviation.items(), key= lambda x: x[1], reverse=False)
deviation_list = sorted(deviation, key=lambda x: deviation[x], reverse=False)

with open('estimation_check.txt', 'w', encoding='UTF8') as file:
    print("Top-5 Closest:", file=file)
    for word in deviation_list[:5]:
        print("%s   %.2f   %.2f" % (word, word_estimations[word], empirical_estimation[word]), file=file)
    print(file=file)

    print("Top-5 Furthest:", file=file)
    for word in deviation_list[-1:-6:-1]:
        print("%s   %.2f   %.2f" % (word, word_estimations[word], empirical_estimation[word]), file=file)
    print(file=file)

    print("Estimation accuracy: %.3f%%" % (100 * accuracy / len(freq_in_twits)), file=file)

with open('estimation_check.txt', encoding='UTF8') as file:
    for line in file:
        print(line)

empirical_estimation_list = sorted(empirical_estimation.items(), key=lambda x: x[1])

with open('best_worst.txt', 'w', encoding='UTF8') as file:
    print("Top-5 Most Positive:", file=file)
    for word, estimation in empirical_estimation_list[:5]:
        print(word, estimation, file=file)
    print(file=file)

    print("Top-5 Most Negative:", file=file)
    for word, estimation in empirical_estimation_list[-1:-6:-1]:
        print(word, estimation, file=file)

with open('best_worst.txt', encoding='UTF8') as file:
    for line in file:
        print(line)
