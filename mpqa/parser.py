import csv
import logging
import os
from typing import List, Union, Tuple, Optional

from mpqa.api import Annotation, Document, Corpus, Sentence

AnnotationValue = Union[int, str, List[str], Sentence]
Position = Tuple[int, int]


def _parse_position(text: str) -> Position:
    t_parts = text.split(',')
    l, r = int(t_parts[0].strip()), int(t_parts[1].strip())
    return l, r


def _split_annotations_properties(text: str) -> List[str]:
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


def _parse_property_value(value: str) -> AnnotationValue:
    delimiter = ","
    value = value.replace("\"", "")
    if delimiter in value:
        return [v.strip() for v in value.split(delimiter)]
    else:
        return value


def parse_annotation_properties(text: str) -> Annotation:
    tokens = _split_annotations_properties(text)
    kv_pairs = [t.split('=') for t in tokens if len(t) > 0]
    params = Annotation({k: _parse_property_value(v) for k, v in kv_pairs})
    return params


def _find_enclosing_sentences(ann: Annotation, sentences: List[Sentence]) -> Sentence:
    for sent in sentences:
        if ann.in_sentence(sent):
            return sent
    logging.debug("No enclosing sentence found for annotation #{}".format(ann[ann.NUM]))


def parse_annotation(row: List[str], sentences: List[Sentence], version: str) -> Optional[Annotation]:
    if row[0].strip()[0] == '#':
        return None
    l, r = _parse_position(row[1])

    type_pos = 2 if version == "3.0" else 3
    properties_pos = 3 if version == "3.0" else 4

    ann = Annotation(
        {Annotation.NUM: int(row[0]), Annotation.LEFT: l, Annotation.RIGHT: r, Annotation.ANN_TYPE: row[type_pos]})
    if len(row) > properties_pos:
        params = parse_annotation_properties(row[properties_pos])
        ann.update(params)
        sentence = _find_enclosing_sentences(ann, sentences) or Sentence((None, None))
        ann[Annotation.SENTENCE] = sentence
    return ann


def parse_annotations(filepath: str, sentences: List[Sentence], version: str) -> List[Annotation]:
    logging.debug("Parsing annotations for {}".format(filepath))
    annotations = []
    with open(filepath) as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            ann = parse_annotation(row, sentences, version)
            if ann:
                annotations.append(ann)
    return annotations


def read_sentence_positions(sentence_ann_path: str) -> List[Sentence]:
    sentences = []
    with open(sentence_ann_path) as f:
        reader = csv.reader(f, delimiter="\t")
        for row in reader:
            sent = Sentence(_parse_position(row[1]))
            sentences.append(sent)
    return sentences


def read_document(document_path: str) -> str:
    with open(document_path) as f:
        return f.read()


def parse_document(corpus_path: str, parent_dir: str, filename: str, version: str) -> Optional[Document]:
    sent_ann_ver = "2.0" if version == "3.0" else version
    ann_ver = version
    document_path = os.path.join(corpus_path, "docs", parent_dir, filename)
    sentence_ann_path = os.path.join(corpus_path, "man_anns", parent_dir, filename,
                                     "gatesentences.mpqa.{}".format(sent_ann_ver))
    annotation_path = os.path.join(corpus_path, "man_anns", parent_dir, filename,
                                   "gateman.mpqa.lre.{}".format(ann_ver))

    if os.path.exists(sentence_ann_path) and os.path.exists(annotation_path):
        text = read_document(document_path)
        sentences = read_sentence_positions(sentence_ann_path)
        annotations = parse_annotations(annotation_path, sentences, version)

        doc = Document(text, sentences, annotations, annotation_path)
        return doc
    else:
        logging.debug("Annotation files do not exist for {}".format(document_path))
        return None


def get_corpus_version(data_home: str) -> str:
    return data_home[-3:]


def parse_corpus(corpus_path: str) -> Corpus:
    corpus_version = get_corpus_version(corpus_path)
    docs_path = os.path.join(corpus_path, "docs")

    docs = []
    for parent_dir in os.listdir(docs_path):
        for file_name in os.listdir(os.path.join(docs_path, parent_dir)):
            doc = parse_document(corpus_path, parent_dir, file_name, corpus_version)
            if doc is not None:
                docs.append(doc)

    return Corpus(docs, corpus_version)
