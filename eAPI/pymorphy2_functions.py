# coding=utf-8
import pymorphy2

morph = pymorphy2.MorphAnalyzer()


def get_nomn_parse(word):
    ps = morph.parse(word)
    for p in ps:
        if p.tag.case == 'nomn':
            return p


def word_to_accs(word):
    p = get_nomn_parse(word)
    if not p:
        return word
    return p.inflect({'accs'}).word.capitalize()


def word_to_datv(word):
    p = get_nomn_parse(word)
    if not p:
        return word
    return p.inflect({'datv'}).word.capitalize()


def to_accs(name):
    name = name.split(' ')
    name_accs = []
    for word in name:
        name_accs.append(word_to_accs(word))
    return ' '.join(name_accs)


def to_datv(name):
    name = name.split(' ')
    name_datv = []
    for word in name:
        name_datv.append(word_to_datv(word))
    return ' '.join(name_datv)