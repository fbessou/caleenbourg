from collections import defaultdict
from pathlib import Path
import random
import sys


def text_to_phon(dictionnary, text):
    text = text.replace("'", " ")
    phon = ""
    for word in text.split():
        w_phon = dictionnary.get(word, word)
        phon += w_phon
    return phon


def phon_to_text(dictionnary_inv, phon, text=""):
    if not phon:
        print(f"*{text}")
        return

    shuffled_keys = list(dictionnary_inv.keys())
    random.shuffle(shuffled_keys)
    for word_phon in shuffled_keys:
        orths = dictionnary_inv[word_phon]
        if phon.startswith(word_phon):
            random.shuffle(orths)
            orth = orths[0]
            phon_to_text(dictionnary_inv, phon[len(word_phon):], text + " " + orth)
    else:
        pass  # print(text)


def main():
    text = sys.argv[1].lower()
    with (Path(__file__).parent / "data" / "dict.tsv").open() as f:
        dictionnary = dict()
        dictionnary_inv = defaultdict(list)
        for ortho, phon in [line.split("\t")[0:2] for line in f.readlines()]:
            dictionnary[ortho] = phon
            if len(ortho) > 1 or ortho not in "zrtpqsdfghjklmwxcvbniuoe":
                dictionnary_inv[phon].append(ortho)

    phon = text_to_phon(dictionnary, text)
    print(phon)
    phon_to_text(dictionnary_inv, phon)


if __name__ == "__main__":
    main()
