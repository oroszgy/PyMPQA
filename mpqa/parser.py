import csv
import os
from typing import List

from mpqa.api import Position, AnnotationValue, Annotation, Document, Corpus


def _parse_position(text: str) -> Position:
    l, r = text.split(',')
    l, r = int(l), int(r)
    return l, r


def _split_annotations(text: str) -> List[str]:
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


def parse_annotation(text: str) -> Annotation:
    tokens = _split_annotations(text)
    kv_pairs = [t.split('=') for t in tokens if len(t) > 0]
    params = {k: _parse_annotation_value(v) for k, v in kv_pairs}
    return params


def is_annotation_in_sentence(ann: Annotation, sentence: Position) -> bool:
    return ann[Document.ANN_LEFT] >= sentence[0] \
           and ann[Document.ANN_RIGHT] <= sentence[1]


def _find_enclosing_sentences(ann: Annotation, sentences: List[Position]) -> Position:
    for sent in sentences:
        if is_annotation_in_sentence(ann, sent):
            return sent


def parse_annotations(filepath: str, sentences: List[Position]) -> List[Annotation]:
    annotations = []
    with open(filepath) as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            if row[0].strip()[0] == '#':
                continue
            l, r = _parse_position(row[1])
            ann = {Document.ANN_LEFT: l, Document.ANN_RIGHT: r, Document.TYPE: row[3]}
            if len(row) > 4:
                params = parse_annotation(row[4])
                ann.update(params)
                sentence_pos = _find_enclosing_sentences(ann, sentences) or (None, None)
                ann[Document.SENT_LEFT] = sentence_pos[0]
                ann[Document.SENT_RIGHT] = sentence_pos[1]
            annotations.append(ann)
    return annotations


def read_sentence_positions(sentence_ann_path: str) -> List[Position]:
    sentences = []
    with open(sentence_ann_path) as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            l, r = _parse_position(row[1])
            sentences.append((l, r))
    return sentences


def read_document(document_path: str) -> str:
    with open(document_path) as f:
        return f.read()


def parse_document(corpus_path: str, parent_dir: str, filename: str, version: str) -> Document:
    document_path = os.path.join(corpus_path, "docs", parent_dir, filename)
    sentence_ann_path = os.path.join(corpus_path, "man_anns", parent_dir, filename,
                                     "gatesentences.mpqa.{}".format(version))
    annotation_path = os.path.join(corpus_path, "man_anns", parent_dir, filename,
                                   "gateman.mpqa.lre.{}".format(version))

    text = read_document(document_path)
    sentences = read_sentence_positions(sentence_ann_path)
    annotations = parse_annotations(annotation_path, sentences)

    doc = Document(text, sentences, annotations)
    return doc


def get_corpus_version(data_home: str) -> str:
    return data_home[-3:]


def parse_corpus(corpus_path: str) -> Corpus:
    corpus_version = get_corpus_version(corpus_path)
    docs_path = os.path.join(corpus_path, "docs")

    docs = []
    for parent_dir in os.listdir(docs_path):
        for file_name in os.listdir(os.path.join(docs_path, parent_dir)):
            doc = parse_document(corpus_path, parent_dir, file_name, corpus_version)
            docs.append(doc)

    return Corpus(docs, corpus_version)
