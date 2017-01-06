#!/usr/bin/env python3
import csv
import sys
import logging
from typing import Iterable

logging.basicConfig(level=logging.DEBUG)

import click

from mpqa import parse_corpus


@click.group()
def mpqa_cli():
    pass


def write_tsv(rows: Iterable[Iterable], file):
    writer = csv.writer(file, delimiter='\t')
    for row in rows:
        writer.writerow(row)
        sys.stdout.flush()


@mpqa_cli.command()
@click.argument("corpus_path", type=click.Path(exists=True))
def sentence_subjectivity(corpus_path: str):
    corpus = parse_corpus(corpus_path)
    write_tsv(
        ((sent, label) for doc in corpus.documents for sent, label in doc.subj_obj_sents()),
        sys.stdout
    )


@mpqa_cli.command()
@click.argument("corpus_path", type=click.Path(exists=True))
def targeted_sentiment(corpus_path):
    corpus = parse_corpus(corpus_path)
    write_tsv(
        (data for doc in corpus.documents for data in doc.targets_w_attitudes()),
        sys.stdout
    )


if __name__ == "__main__":
    mpqa_cli()
