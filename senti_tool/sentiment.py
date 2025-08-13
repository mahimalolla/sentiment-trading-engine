import re
from collections import Counter
from typing import Dict, List, Tuple

_SUFFIXES = r"(?:s|es|ed|ing|er|ers|ment|ments)?"
_WORD_BOUND = r"(?<![A-Za-z0-9_]){kw}(?![A-Za-z0-9_])"

def _compile_patterns(words: List[str]) -> List[re.Pattern]:
    pats = []
    single_words = []
    phrases = []
    for w in set(x.lower().strip() for x in words if x.strip()):
        if " " in w:
            phrases.append(re.escape(w))
        else:
            single_words.append(re.escape(w) + _SUFFIXES)
    # whole phrases as-is (simple contains)
    phrase_pats = [re.compile(w, flags=re.IGNORECASE) for w in phrases]
    # single words with boundaries + suffix handling
    word_pats = [re.compile(_WORD_BOUND.format(kw=w), flags=re.IGNORECASE) for w in single_words]
    return phrase_pats + word_pats

def normalize_title(title: str) -> str:
    t = title.lower()
    t = re.sub(r"[^a-z0-9 ]+","", t)
    t = re.sub(r"\s+"," ", t).strip()
    return t

class KeywordSentiment:
    def __init__(self, positives: List[str], negatives: List[str], negations: List[str] = None, phrase_window: int = 3, source_weights: Dict[str,float]=None):
        self.pos_pats = _compile_patterns(positives)
        self.neg_pats = _compile_patterns(negatives)
        self.negations = [n.lower() for n in (negations or [])]
        self.window = int(phrase_window or 3)
        self.source_weights = source_weights or {}

    def _apply_negation(self, text: str, pos: int, neg: int) -> Tuple[int,int]:
        if not self.negations:
            return pos, neg
        # very lightweight negation: if any negation cue exists near a positive hit, flip 1; and vice versa
        # this avoids dependences; it's a heuristic.
        lower = text.lower()
        for cue in self.negations:
            if cue in lower:
                # flip one unit of whichever side is larger to the other side
                if pos > neg and pos > 0:
                    pos -= 1; neg += 1
                elif neg > pos and neg > 0:
                    neg -= 1; pos += 1
                break
        return pos, neg

    def score_item(self, item: Dict) -> Tuple[int,int,Dict[str,int]]:
        text = " ".join([item.get("title",""), item.get("description",""), item.get("content","")])
        pos_hits: Counter = Counter()
        neg_hits: Counter = Counter()
        for pat in self.pos_pats:
            for _ in pat.finditer(text):
                pos_hits[pat.pattern] += 1
        for pat in self.neg_pats:
            for _ in pat.finditer(text):
                neg_hits[pat.pattern] += 1
        pos = sum(pos_hits.values()); neg = sum(neg_hits.values())
        pos, neg = self._apply_negation(text, pos, neg)

        # source weight
        w = self.source_weights.get(item.get("source") or "Unknown", 1.0)
        pos_w = round(pos * w); neg_w = round(neg * w)

        hits = {}
        hits.update({f"+:{k}": v for k,v in pos_hits.items()})
        hits.update({f"-:{k}": v for k,v in neg_hits.items()})
        return pos_w, neg_w, hits
