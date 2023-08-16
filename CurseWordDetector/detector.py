import json, math, itertools, re, hangul_utils
from numpy import dot
from numpy.linalg import norm
from CurseWordDetector.similars import *
from CurseWordDetector.char2vec import *
from CurseWordDetector.SoundBase import detector as SoundBase

def CosineSimilarity(vec1, vec2):
    return dot(vec1, vec2)/((norm(vec1)*norm(vec2))+1e-30)

CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
JONGSUNG_LIST = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
sound = SoundBase()

def split(word):
    return [char for char in word] 

def ksplit(korean_word, convert=True):
    r_lst = []
    for w in split(korean_word):
        if '가'<=w<='힣':
            ch1 = (ord(w) - ord('가'))//588
            ch2 = ((ord(w) - ord('가')) - (588*ch1)) // 28
            ch3 = (ord(w) - ord('가')) - (588*ch1) - 28*ch2
            if JONGSUNG_LIST[ch3] != ' ':
                new_ = [CHOSUNG_LIST[ch1], JUNGSUNG_LIST[ch2], JONGSUNG_LIST[ch3]]
            else:
                new_ = [CHOSUNG_LIST[ch1], JUNGSUNG_LIST[ch2], ' ']

            if new_[0] == "ㅇ": new_[0] = ' '
            r_lst += new_
        else:
            r_lst.append(w)

    if convert:
        return [ConvertText(k) for k, g in itertools.groupby(r_lst)]
    else:
        return [k for k, g in itertools.groupby(r_lst)]
    
def ksplit2(korean_word, convert=True):
    r_lst = []
    for w in split(korean_word):
        if '가'<=w<='힣':
            ch1 = (ord(w) - ord('가'))//588
            ch2 = ((ord(w) - ord('가')) - (588*ch1)) // 28
            ch3 = (ord(w) - ord('가')) - (588*ch1) - 28*ch2
            if JONGSUNG_LIST[ch3] != ' ':
                new_ = [CHOSUNG_LIST[ch1], JUNGSUNG_LIST[ch2], JONGSUNG_LIST[ch3]]
            else:
                new_ = [CHOSUNG_LIST[ch1], JUNGSUNG_LIST[ch2]]

            if new_[0] == "ㅇ": new_ = new_[1:]
            r_lst += new_
        else:
            r_lst.append(w)

    if convert:
        return [ConvertText(k) for k, g in itertools.groupby(r_lst)]
    else:
        return [k for k, g in itertools.groupby(r_lst)]

def ConvertText(chr):
    chr = seems.get(chr, chr)
    # chr = en2kr.get(chr, chr)
    return chr


def word2vec(text:str, convert=True, method=ksplit) -> list:
    splited = method(text, convert)
    vector = []

    for c in splited:
        vector += CHAR2VEC.get(c, [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,])

    return vector

def GenerateVector(word1, word2, convert=True, method=ksplit):
    maxlen = max(len(method(word1, convert)), len(method(word2, convert))) * 8
    vec1, vec2 = word2vec(word1, convert, method), word2vec(word2, convert, method)
    vec1 = vec1 + [0] * (maxlen - len(vec1))
    vec2 = vec2 + [0] * (maxlen - len(vec2))

    return vec1, vec2


def similarity(word1, word2, convert=True, method=ksplit):
    vec1, vec2 = GenerateVector(word1, word2, convert, method)
    return CosineSimilarity(vec1, vec2)

def FindAll(text, item):
    indices = []
    for idx, value in enumerate(text):
        if value == item:
            indices.append(idx)
    return indices

en = 'abcdefghijklmnopqrstuvwxyz'
def filtering(string):
    print(hangul_utils.jamo_type('a'))



class detector:
    def __init__(self, CursePath=".\\CurseWordDetector\\curse.json") -> None:
        self.path = CursePath
        self.curses = json.load(open(CursePath, 'r', encoding='utf8'))

    def detect(self, sentence, RemoveSpecials=True):
        try:
            threshold = 0.7
            detected = False

            text = sentence
            result = text.split(" ")
            org = text.split(" ")
            for i, token in enumerate(result):
                specials = set(re.findall(r'[^A-Za-z가-ퟻㄱ-ㅣ]', token))
                specialsmap = []
                for s in specials:
                    specialsmap += [(i, s) for i in FindAll(token, s)]
                specialsmap = sorted(specialsmap, key=lambda t: t[0])
                for curse in self.curses['curse']:
                    changed = False
                    sim = similarity(token, curse)
                    sim_unconvert = similarity(token, curse, False)
                    sim_ksplit2 = similarity(token, curse, method=ksplit2)

                    sim_ksplit2 = -1

                    # print(sim, sim_unconvert, sim_ksplit2)
                    processed = token
                    if (sim >= threshold or sim_unconvert >= threshold or sim_ksplit2 >= threshold):
                        if (curse in self.curses['force'] or sim_unconvert >= threshold + .1 or sim_ksplit2 >= threshold + .1):
                            processed = "*"*len(token)
                            changed = True
                            print(f'[token] {curse}, {token}\n', sim, sim_unconvert, sim_ksplit2)
                        else:
                            soundpos = sound.detect(token)
                            if (soundpos > 0.8):
                                changed = True
                                processed = "*"*len(token)
                                print(f'[token+sound] {curse}, {token}\n', sim, sim_unconvert, sim_ksplit2, '\n', soundpos)
                    for index, special in specialsmap:
                        processed = processed[:index] + special + processed[index:]
                    if changed: result[i] = processed; detected = True
            text = ' '.join(result)
            sentence = text

            if RemoveSpecials:
                specials = set(re.findall(r'[^A-Za-z가-ퟻㄱ-ㅣ]', sentence))
                specialsmap = []
                for s in specials:
                    specialsmap += [(i, s) for i in FindAll(sentence, s)]


                specialsmap = sorted(specialsmap, key=lambda t: t[0])
                sentence = re.sub(r'[^ A-Za-z가-ퟻㄱ-ㅣ+]', "(REMOVE)", sentence)
            sentence = sentence.replace("(REMOVE)", "")
            text = sentence.replace(" ", "")
            for curse in self.curses['curse']:
                size = len(curse)
                for i in range(len(text) - size + 1):
                    check = text[i:i+size]
                    sim = similarity(check, curse)
                    sim_unconvert = similarity(check, curse, False)
                    sim_ksplit2 = similarity(check, curse, method=ksplit2)

                    sim_ksplit2 = -1
                    if (sim >= threshold or sim_unconvert >=threshold or sim_ksplit2 >= threshold):
                        cleaned = hangul_utils.join_jamos(''.join(ksplit2(check)))
                        if (curse in self.curses['force'] or sim >= threshold +.1 or sim_unconvert >=threshold+.1 or sim_ksplit2 >= threshold+.1):
                            text = text.replace(check, "*"*len(check))
                            print(f'[token] {curse}, {check}\n', sim, sim_unconvert, sim_ksplit2)
                            detected = True
                            continue
                        soundpos = sound.detect(check)
                        print(soundpos)
                        if (soundpos >= 0.8):
                            text = text.replace(check, "*"*len(check))
                            
                            print(f'[token] {curse}, {check}\n', sim, sim_unconvert, sim_ksplit2, '\n', soundpos)
                            detected = True
            
            #restore spacing
            for index, special in specialsmap:
                text = text[:index] + special + text[index:]
                                            
            #

            return text, detected
        except Exception as e:
            print(f"[Detector Error] {e}\n\nSentence: {sentence}")
            return sentence
    
    def reload(self):
        self.curses = json.load(open(self.path, 'r', encoding='utf8'))