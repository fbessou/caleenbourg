from collections import defaultdict
import math
from pathlib import Path
import random
import re
import sys


def text_to_phon(dictionnary, text):
    text = text.replace("'", " ")
    phon = ""
    for word in text.split():
        if word not in dictionnary:
            raise Exception(f"Unknown word: {word}")
        else:
            w_phon = dictionnary.get(word)
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


def distance(phon_i, phon_j, distance_table):
    # D[i][j] = distance between phon_i[:i] and phon_j[:j]
    D = [[0] * (len(phon_j) + 1) for i in range(len(phon_i) + 1)]

    def substitute_cost(a, b):
        return (distance_table[a][b]
                if a in distance_table and b in distance_table[a] else 1.0)

    def same_type(a, b):
        return distance_table[a]["phon_type"] == distance_table[b]["phon_type"]

    for i in range(0, 1 + len(phon_i)):
        for j in range(0, 1 + len(phon_j)):
            if i == 0 and j == 0:
                continue
            p10 = phon_i[i - 1] if i > 0 else ""
            p20 = phon_i[i - 2] if i > 1 else ""
            p01 = phon_j[j - 1] if j > 0 else ""
            p02 = phon_j[j - 2] if j > 1 else ""
            cost11 = substitute_cost(p10, p01)
            cost12 = substitute_cost(p10, p02)
            cost21 = substitute_cost(p20, p01)
            cost22 = substitute_cost(p20, p02)
            cost10 = substitute_cost(p10, "")
            cost20 = substitute_cost(p20, "")
            cost01 = substitute_cost(p01, "")
            cost02 = substitute_cost(p02, "")
            fuseX0 = 1.2
            fuse0X = 1.2

            dist_cond = [
                # insert p10, delete p01
                (lambda: D[i-1][j] + cost10 + cost01,
                 lambda: i > 0),
                # insert p01, delete p10
                (lambda: D[i][j-1] + cost10 + cost01,
                 lambda: j > 0),
                # substitute p10/p01
                (lambda: D[i-1][j-1] + cost11,
                 lambda: p10 and p01),
                # insert p10+p20, delete p01
                (lambda: D[i-2][j] + fuseX0 * max(cost10, cost20) + cost01,
                 lambda: p10 and p20 and p01 and same_type(p10, p20)),
                # insert p01+p02, delete p10
                (lambda: D[i][j-2] + fuse0X * max(cost01, cost02) + cost10,
                 lambda: p01 and p02 and p10 and same_type(p01, p02)),
                # substitute p10+p20/p01
                (lambda: D[i-2][j-1] + fuseX0 * max(cost11, cost21),
                 lambda: p10 and p20 and p01 and same_type(p10, p20)),
                # substitute p10/p01+p02
                (lambda: D[i-1][j-2] + fuse0X * max(cost11, cost12),
                 lambda: p10 and p01 and p02 and same_type(p01, p02)),
                # substitute p10+p20/p01+p02
                (lambda: D[i-2][j-2] + fuse0X * fuseX0 *
                    max(cost11, cost12, cost21, cost22),
                 lambda: p10 and p20 and p01 and p02 and
                    same_type(p10, p20) and same_type(p01, p02)),
            ]

            D[i][j] = min(dist() for dist, cond in dist_cond if cond())

    return D[-1][-1] / max(D[0][-1], D[-1][0])


def load_distance_table(table, file_path, phon_type):
    factor = 0.7 if phon_type == "consonant" else 1.0
    with file_path.open() as f:
        phons = f.readline().replace("\n", "").split("\t")[1:]
        for line in f.readlines():
            line = line.replace("\n", "").split("\t")
            phon_i = line[0]
            for dist, phon_j in zip(line[1:], phons):
                if dist:
                    dist = float(dist) * factor
                    table[phon_i][phon_j] = dist
                    table[phon_j][phon_i] = dist
            table[phon_i][""] = factor * 1
            table[""][phon_i] = factor * 1
            table[phon_i]["phon_type"] = phon_type
    return table


def main():
    text = sys.argv[1].lower()
    phon_set = set()
    with (Path(__file__).parent / "data" / "dict.tsv").open() as f:
        dictionnary = dict()
        dictionnary_inv = defaultdict(list)
        for line in f.readlines()[1:]:
            ortho, phon = line.split("\t")[:2]
            dictionnary[ortho] = phon
            phon_set |= set(phon)
            if len(ortho) > 1 or ortho not in "zrtpqsdfghjklmwxcvbniuoe":
                dictionnary_inv[phon].append(ortho)

    # print(sorted(list(phon_set)))

    distance_table = defaultdict(dict)
    distance_table[""][""] = 0.0
    load_distance_table(
            distance_table,
            Path(__file__).parent / "tables" / "distance-fr-v.tsv", "vowel")
    load_distance_table(
            distance_table,
            Path(__file__).parent / "tables" / "distance-fr-c.tsv", "consonant")
    #for e in "29°":
    #    distance_table[e][""] = 0.3
    #    distance_table[""][e] = 0.3

    raw_corpus = []
    corpus_dir = Path(__file__).parent / "corpus"
    for text_file in corpus_dir.iterdir():
        with text_file.open() as f:
            raw_corpus += f.readlines()
    corpus = []
    for line in raw_corpus:
        line = re.sub(r'([?!….,;:"\s]|--)+', ' ', line)
        line = re.sub(r'^ | $', '', line)
        try:
            phon = text_to_phon(dictionnary, line.lower())
            corpus.append(phon or None)
        except Exception:
            corpus.append(None)

    phon = text_to_phon(dictionnary, text)
    print(phon)

    puns = []
    for p, raw in zip(corpus, raw_corpus):
        if p is not None:
            puns.append((
                distance(p, phon, distance_table), raw, p))

    puns.sort()
    print(len(puns))
    print("\n".join(map(str, puns[:10])))

    # while True:
    #     t = input().lower()
    #     p = text_to_phon(dictionnary, t)
    #     print(p)
    #     print(normalized_distance(
    #         p,
    #         phon,
    #         distance_table))
    # phon_to_text(dictionnary_inv, phon)


if __name__ == "__main__":
    main()
