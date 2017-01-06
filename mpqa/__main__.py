#!/usr/bin/env python3
import csv
import logging
import sys
from typing import Iterable

import click

from mpqa import parse_corpus

logging.basicConfig(level=logging.INFO)


def write_tsv(rows: Iterable[Iterable], file):
    writer = csv.writer(file, delimiter="\t")
    for row in rows:
        writer.writerow(row)
        sys.stdout.flush()


@click.group()
def mpqa_cli():
    pass


@mpqa_cli.command()
@click.argument("corpus_path", type=click.Path(exists=True))
def sentence_subjectivity(corpus_path: str):
    corpus = parse_corpus(corpus_path)
    write_tsv(
        (data for doc in corpus.documents for data in doc.subj_obj_sents()),
        sys.stdout
    )


@mpqa_cli.command()
@click.argument("corpus_path", type=click.Path(exists=True))
def targeted_sentiment(corpus_path):
    corpus = parse_corpus(corpus_path)
    write_tsv(
        (data for doc in corpus.documents for data in doc.stargets_w_attitudes()),
        sys.stdout
    )


@mpqa_cli.command()
@click.argument("corpus_path", type=click.Path(exists=True))
def entity_sentiment(corpus_path):
    corpus = parse_corpus(corpus_path)
    write_tsv(
        (data for doc in corpus.documents for data in doc.entity_sentiment()),
        sys.stdout
    )


if __name__ == "__main__":
    mpqa_cli()
