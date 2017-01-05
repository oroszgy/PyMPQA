#!/usr/bin/env python3
import csv
import sys

import click

from mpqa import parse_corpus


@click.group()
def mpqa_cli():
    pass


@mpqa_cli.command()
@click.argument("corpus_path", type=click.Path(exists=True))
def extract_sentences(corpus_path: str):
    corpus = parse_corpus(corpus_path)
    writer = csv.writer(sys.stdout, delimiter='\t')
    for doc in corpus.documents:
        for sent, label in doc.subj_obj_sents():
            writer.writerow([sent, label])
            sys.stdout.flush()


if __name__ == "__main__":
    mpqa_cli()
