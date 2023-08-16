from CurseWordDetector.similars import *
from CurseWordDetector.char2vec import *
from numpy import dot
from numpy.linalg import norm
from difflib import SequenceMatcher
import itertools

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def CosineSimilarity(vec1, vec2):
    return dot(vec1, vec2)/((norm(vec1)*norm(vec2))+1e-30)

CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
JONGSUNG_LIST = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

def split(word):
    return [char for char in word] 

def ksplit(korean_word, ReturnString=False, IgnoreNoSound=True, FillEmpty=False, IgnoreRepeating=True) -> list|str:
    r_lst = []
    for w in split(korean_word):
        if '가'<=w<='힣':
            ch1 = (ord(w) - ord('가'))//588
            ch2 = ((ord(w) - ord('가')) - (588*ch1)) // 28
            ch3 = (ord(w) - ord('가')) - (588*ch1) - 28*ch2
            if JONGSUNG_LIST[ch3] != ' ':
                new_ = [CHOSUNG_LIST[ch1], JUNGSUNG_LIST[ch2], JONGSUNG_LIST[ch3]]
            else:
                if (FillEmpty): new_ = [CHOSUNG_LIST[ch1], JUNGSUNG_LIST[ch2], ' ']
                else: new_ = [CHOSUNG_LIST[ch1], JUNGSUNG_LIST[ch2]]

            if new_[0] == "ㅇ" and IgnoreNoSound: new_ = new_[1:]
            r_lst += new_
        else:
            if (FillEmpty):
                if (w in JUNGSUNG_LIST): r_lst += [' ', w, ' ']
                else:
                    r_lst += [w, ' ', ' ']
            else:
                r_lst.append(w)

    if (IgnoreRepeating): r_lst = [ConvertText(k) for k, g in itertools.groupby(r_lst)]
    if (ReturnString): r_lst = ''.join(r_lst)
    
    return r_lst

def ConvertText(chr):
    if (len(chr) == 1):
        chr = seems.get(chr, chr)
        chr = en2kr.get(chr, chr)
        return chr
    else:
        text :str = ''.join([ConvertText(c) for c in chr])
        for doub in double:
            text = text.replace(doub, double[doub])

        return text
    
def word2vec(text:str, FillEmpty=True, IgnoreRepeating= True, IgnoreNoSound=False) -> list:
    splited = ksplit(text, IgnoreNoSound=False, FillEmpty=True, IgnoreRepeating=True)
    vector = []

    for c in splited:
        vector += CHAR2VEC.get(c, [0, 0, 0, 0, 0, 0, 0, 0,])

    return vector

def GenerateVector(word1, word2, FillEmpty=True, IgnoreRepeating= True, IgnoreNoSound=False):
    maxlen = max(len(ksplit(word1, IgnoreNoSound=IgnoreNoSound, FillEmpty=FillEmpty, IgnoreRepeating=IgnoreRepeating)), len(ksplit(word2, IgnoreNoSound=IgnoreNoSound, FillEmpty=FillEmpty, IgnoreRepeating=IgnoreRepeating))) * 8
    vec1, vec2 = word2vec(word1, FillEmpty, IgnoreRepeating, IgnoreNoSound), word2vec(word2, FillEmpty, IgnoreRepeating, IgnoreNoSound)
    if (FillEmpty):
        vec1 = vec1 + [0] * (maxlen - len(vec1))
        vec2 = vec2 + [0] * (maxlen - len(vec2))

    return vec1, vec2


def similarity(word1, word2):
    vec1, vec2 = GenerateVector(word1, word2)
    return CosineSimilarity(vec1, vec2)

def FindAll(text, item):
    indices = []
    for idx, value in enumerate(text):
        if value == item:
            indices.append(idx)
    return indices

kr2s = {' ': ' ', 'ㄱ': 'g', 'ㄲ': 'gg', 'ㄳ': 'gs', 'ㄴ': 'n', 'ㄵ': 'nj', 
        'ㄶ': 'n', 'ㄷ': 'd', 'ㄸ': 'dd', 'ㄹ': 'l', 'ㄺ': 'lg', 'ㄻ': 'lm', 
        'ㄼ': 'lb', 'ㄽ': 'ls', 'ㄾ': 'lt', 'ㄿ': 'lp', 'ㅀ': 'lh', 'ㅁ': 'm', 
        'ㅂ': 'b', 'ㅃ': 'bb', 'ㅄ': 'bs', 'ㅅ': 's', 'ㅆ': 'ss', 'ㅇ': 'o', 
        'ㅈ': 'j', 'ㅉ': 'jj', 'ㅊ': 'ch', 'ㅋ': 'k', 'ㅌ': 't', 'ㅍ': 'p', 
        'ㅎ': 'h', 'ㅏ': 'a', 'ㅐ': 'e', 'ㅑ': 'ya', 'ㅒ': 'ye', 'ㅓ': 'eo', 
        'ㅔ': 'e', 'ㅕ': 'yeo', 'ㅖ': 'ye', 'ㅗ': 'o', 'ㅘ': 'wa', 'ㅙ': 'wae', 
        'ㅚ': 'oe', 'ㅛ': 'yo', 'ㅜ': 'wo', 'ㅝ': 'weo', 'ㅞ': 'we', 'ㅟ': 'wui', 
        'ㅠ': 'u', 'ㅡ': 'eu', 'ㅢ': 'ui', 'ㅣ': 'i'}



def kr2sound(korean:str, IgnoreRepeating=True, ReturnList = False) -> str|list:
    splited = ksplit(korean, ReturnString=True, IgnoreNoSound=True, FillEmpty=False, IgnoreRepeating=IgnoreRepeating)
    converted = [kr2s.get(c, c) for c in splited]
    converted = "".join(converted)
    if (IgnoreRepeating): converted = [k for k, g in itertools.groupby(converted)]
    if (ReturnList): converted = [c for c in converted]

    return converted