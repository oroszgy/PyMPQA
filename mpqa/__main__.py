#!/usr/bin/env python3
import csv
import os
import sys

import click

from mpqa import Document
from mpqa.parser import get_ver


@click.group()
def mpqa():
    pass


@mpqa.command()
@click.argument("corpus_path", type=click.Path(exists=True))
def extract_sentences(corpus_path: str):
    ver = get_ver(corpus_path)
    docs = []

    docs_path = os.path.join(corpus_path, "docs")
    for parent in os.listdir(docs_path):
        for leaf in os.listdir(os.path.join(docs_path, parent)):
            doc = Document(corpus_path, parent, leaf, ver)
            docs.append(doc)
    writer = csv.writer(sys.stdout, delimiter='\t')
    for doc in docs:
        for sent, label in doc.subj_obj_sents():
            writer.writerow([sent, label])
            sys.stdout.flush()


if __name__ == "__main__":
    mpqa()
