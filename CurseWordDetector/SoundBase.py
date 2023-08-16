from CurseWordDetector.functions import *
import json, re

class detector:
    def __init__(self, CursePath=".\\CurseWordDetector\\curse.json") -> None:
        self.curses = json.load(open(CursePath, 'r', encoding='utf8'))

    def detect(self, sentence, RemoveSpecials=True, IgnoreJungSung=True) -> str:
        sentence = ConvertText(sentence)

        specials = set(re.findall(r'[^A-Za-z가-ퟻㄱ-ㅣ]', sentence))
        specialsmap = []
        for s in specials:
            specialsmap += [(i, s) for i in FindAll(sentence, s)]
        if (IgnoreJungSung):
            for jung in JUNGSUNG_LIST:
                specialsmap += [(i, jung) for i in FindAll(sentence, jung)]
        
        specialsmap = sorted(specialsmap, key=lambda t: t[0])
        sentence = re.sub(r'[^A-Za-z가-ퟻㄱ-ㅣ]', '', sentence)
        if (IgnoreJungSung):
            for jung in JUNGSUNG_LIST:
                sentence = sentence.replace(jung, '')
            
        pos = []

        for curse in self.curses['curse']:
            size = len(curse)
            CurseSound = kr2sound(curse, IgnoreRepeating=False, ReturnList=True)

            for i, chr in enumerate(sentence):
                target = sentence[i:i+size]
                TargetSound = kr2sound(target, IgnoreRepeating=False, ReturnList=True)
                vec1, vec2 = GenerateVector(CurseSound, TargetSound, FillEmpty=False)
                Similarity = similar(vec1,vec2)

                pos.append(Similarity)


        return max(pos)