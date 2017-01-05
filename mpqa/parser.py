import csv
import os
from typing import Union, List, Tuple, Dict

Position = Tuple[int, int]
AnnotationValue = Union[str, List[str]]
Annotation = Dict[str, AnnotationValue]


def read_annotations(data_home: str, parent_dir: str, filename: str, version: str) -> List[Annotation]:
    annotations = []
    filepath = os.path.join(data_home, "man_anns", parent_dir, filename, "gateman.mpqa.lre.{}".format(version))
    with open(filepath) as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if row[0].strip()[0] == '#':
                continue
            l, r = parse_position(row[1])
            ann = dict(left=l, right=r, type=row[3])
            if len(row) > 4:
                params = parse_annotation(row[4])
                ann.update(params)
            annotations.append(ann)
    return annotations


def parse_annotation(text: str) -> Annotation:
    tokens = _tokenize_annotations(text)
    kv_pairs = [t.split('=') for t in tokens if len(t) > 0]
    params = {k: _parse_annotation_value(v) for k, v in kv_pairs}
    return params


def _tokenize_annotations(text: str) -> List[str]:
    delimiter = " "
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


def _parse_annotation_value(value: str) -> AnnotationValue:
    delimiter = ","
    value = value.replace("\"", "")
    if delimiter in value:
        return [v.strip() for v in value.split(delimiter)]
    else:
        return value


def read_document(data_home: str, parent_dir: str, filename: str) -> str:
    filepath = os.path.join(data_home, "docs", parent_dir, filename)
    with open(filepath) as f:
        return f.read()


def read_sentences(data_home: str, parent_dir: str, filename: str, version: str) -> List[Position]:
    sentences = []
    filepath = os.path.join(data_home, "man_anns", parent_dir, filename, "gatesentences.mpqa.{}".format(version))
    with open(filepath) as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            l, r = parse_position(row[1])
            sentences.append((l, r))
    return sentences


def parse_position(text: str) -> Position:
    l, r = text.split(',')
    l, r = int(l), int(r)
    return l, r


def get_ver(data_home: str) -> str:
    return data_home[-3:]
