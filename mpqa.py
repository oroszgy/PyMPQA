#! /usr/bin/env python3

import csv
import os
import sys
from typing import Tuple, List


def tokenize(text: str):
    delimiter = " "
    op = "="
    quoted = False
    start = 0
    text = text.strip() + delimiter
    tokens = []
    for i, ch in enumerate(text):
        if ch == "\"":
            quoted = not quoted
        if ch == delimiter and not quoted:
            tokens.append(text[start:i])
            start = i + 1
    return tokens


def read_document(data_home: str, parent_dir: str, filename: str) -> str:
    filepath = os.path.join(data_home, "docs", parent_dir, filename)
    with open(filepath) as f:
        return f.read()


def read_sentences(data_home: str, parent_dir: str, filename: str, version: str) -> List[Tuple[int, int]]:
    sentences = []
    filepath = os.path.join(data_home, "man_anns", parent_dir, filename, "gatesentences.mpqa.{}".format(version))
    with open(filepath) as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            l, r = get_offset(row[1])
            sentences.append((l, r))
    return sentences


def get_offset(text):
    l, r = text.split(',')
    l, r = int(l), int(r)
    return l, r


def read_annotations(data_home, parent_dir, filename, ver):
    annotations = []
    filepath = os.path.join(data_home, "man_anns", parent_dir, filename, "gateman.mpqa.lre.%s" % ver)
    with open(filepath) as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if row[0].strip()[0] == '#':
                continue
            l, r = get_offset(row[1])
            ann = dict(left=l, right=r, type=row[3])
            if len(row) > 4:
                kv = tokenize(row[4])
                meta = dict([t.split('=') for t in kv if len(t) > 0])
                ann.update(meta)
            annotations.append(ann)
    return annotations


class Doc(object):
    def __init__(self, data_home: str, parent_dir: str, filename: str, ver: str):
        self.ver = ver

        self.text = read_document(data_home, parent_dir, filename)

        self.sentences = read_sentences(data_home, parent_dir, filename, self.ver)

        self.annotations = read_annotations(data_home, parent_dir, filename, self.ver)

    def sub_obj_sents(self):
        for l, r in self.sentences:
            c = 0
            for ann in self.annotations:
                if ann['left'] >= l and ann['right'] <= r:
                    if ann['type'] == 'GATE_direct-subjective' and \
                                    'intensity' in ann and \
                                    ann['intensity'] not in ('low', 'neutral') and \
                                    "insubstantial" not in ann:
                        c += 1
                    if ann['type'] == 'GATE_expressive-subjectivity' and \
                                    'intensity' in ann and \
                                    ann['intensity'] not in ('low'):
                        c += 1
            if c > 0:
                yield self.text[l:r], "subjective"
            else:
                yield self.text[l:r], "objective"


def get_ver(data_home):
    ''' return version of data '''
    return data_home[-3:]


def extract_sentences(data_home):
    ver = get_ver(data_home)
    docs_path = os.path.join(data_home, "docs")
    man_anns_path = os.path.join(data_home, "man_anns")
    docs = []
    for parent in os.listdir(docs_path):
        for leaf in os.listdir(os.path.join(docs_path, parent)):
            docs.append(Doc(data_home, parent, leaf, ver))
    writer = csv.writer(sys.stdout, delimiter='\t')
    for doc in docs:
        for sent, label in doc.sub_obj_sents():
            writer.writerow([sent, label])


if __name__ == "__main__":
    sys.exit(extract_sentences(sys.argv[1]))
