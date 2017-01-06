"""
Details of the annotation scheme is described here: https://github.com/jyuhuan/mpqa/wiki/Types-of-Annotations
"""
import logging
from typing import List, Tuple, Generator


class Sentence(tuple):
    def text(self, doc_text: str) -> str:
        if self[0] is not None and self[1] is not None:
            return doc_text[self[0]: self[1]]
        else:
            return None


class Annotation(dict):
    NUM = "num"
    LEFT = 'left'
    RIGHT = 'right'
    SENTENCE = 'sentence'
    ANN_TYPE = 'ann_type'
    TYPE = "type"
    ATTITUDE_TYPE = "GATE_attitude"
    ATTITUDE_T = "attitude-type"
    ENTITY = "entity"
    E_TARGET = "eTarget"
    TARGET_TYPE = "GATE_target"
    EXPRESSIVE_SUBJ_TYPE = 'GATE_expressive-subjectivity'
    DIRECT_SUBJ_TYPE = 'GATE_direct-subjective'
    EXPRESISON_INTENSITY = 'expression-intensity'
    INTENSITY = 'intensity'
    POLARITY = 'polarity'
    ANNOTATION_UNCERTAIN = 'annotation-uncertain'
    SUBJECTIVE_UNCERTAIN = 'subjective-uncertain'
    LOW_INTENSITY_VALUES = ('low',)
    LOW_NEUTRAL_INTENSITY_VALUES = ('low', 'neutral')
    INSUBSTANTIAL = "insubstantial"
    TARGET_LINK = "target-link"
    ID = "id"

    def in_sentence(self, sentence: Sentence) -> bool:
        return self[Annotation.LEFT] >= sentence[0] \
               and self[Annotation.RIGHT] <= sentence[1]

    def find_target_annotation(self, annotations):
        for ann in annotations:
            if Annotation.TARGET_LINK in self.keys() and Annotation.ID in ann.keys() \
                    and ann[Annotation.ID] == self[Annotation.TARGET_LINK]:
                return ann

    def text(self, doc_text: str) -> str:
        return doc_text[self[Annotation.LEFT]: self[Annotation.RIGHT]]

    def get_enclosing_sentence(self):
        return self[Annotation.SENTENCE]

    @property
    def is_intensive_direct_subjectivity(self) -> bool:
        return self[Annotation.ANN_TYPE] == Annotation.DIRECT_SUBJ_TYPE \
               and Annotation.INTENSITY in self \
               and self[Annotation.INTENSITY] not in Annotation.LOW_NEUTRAL_INTENSITY_VALUES \
               and Annotation.INSUBSTANTIAL not in self

    @property
    def is_intensive_expressive_subjectivity(self) -> bool:
        return self[Annotation.ANN_TYPE] == Annotation.EXPRESSIVE_SUBJ_TYPE \
               and Annotation.INTENSITY in self \
               and self[Annotation.INTENSITY] not in Annotation.LOW_INTENSITY_VALUES

    @property
    def is_attitude(self) -> bool:
        return self[Annotation.ANN_TYPE] == Annotation.ATTITUDE_TYPE

    @property
    def is_entity_target(self) -> bool:
        return self[Annotation.ANN_TYPE] == Annotation.E_TARGET and self.get(Annotation.TYPE) == Annotation.ENTITY


class Document(object):
    OBJ = "objective"
    SUBJ = "subjective"
    SUBJ_OBJ_SENTS_SCHEMA = \
        ("sentence_text", "subjectivity")
    STARGET_ATTITUDE_SCHEMA = \
        ("annotation_start", "annotation_end", "annotation_text",
         "attitude", "intensity",
         "target_start", "target_end", "target_text", "sentence_text")
    ENTITY_SENTIMENT_SCHEMA = ("entity_start", "entity_end", "entity_text")

    def __init__(self, text: str, sentences: List[Sentence], annotations: List[Annotation], filename: str) -> None:
        self.filename = filename
        self.text = text
        self.sentences = sentences
        self.annotations = annotations

    def subj_obj_sents(self) -> Generator[Tuple[str, str], None, None]:
        for sent in self.sentences:
            sentence_intensity_counter = 0
            for ann in self.annotations:
                if ann.in_sentence(sent):
                    if ann.is_intensive_direct_subjectivity:
                        sentence_intensity_counter += 1
                    if ann.is_intensive_expressive_subjectivity:
                        sentence_intensity_counter += 1

            sentence_text = sent.text(self.text)
            yield (sentence_text, self.SUBJ) if sentence_intensity_counter > 0 \
                else (sentence_text, self.OBJ)

    def stargets_w_attitudes(self) -> Generator[Tuple, None, None]:
        for ann in self.annotations:
            if ann.is_attitude:
                ann_text = ann.text(self.text)
                sentence = ann.get_enclosing_sentence()
                enclosing_sentence_text = sentence.text(self.text)
                target_ann = ann.find_target_annotation(self.annotations)
                if target_ann and enclosing_sentence_text:
                    target_text = target_ann.text(self.text)
                    yield (ann[Annotation.LEFT] - sentence[0], ann[Annotation.RIGHT] - sentence[0], ann_text,
                           ann.get(Annotation.ATTITUDE_T, "-"), ann.get(Annotation.INTENSITY, "-"),
                           target_ann[Annotation.LEFT] - sentence[0], target_ann[Annotation.RIGHT] - sentence[0],
                           target_text,
                           enclosing_sentence_text)
                else:
                    logging.debug("No target found for annotation #{} in {}".format(ann[ann.NUM], self.filename))

    def entity_sentiment(self) -> Generator[Tuple, None, None]:
        for e_ann in self._entities():
            enclosing_sent = e_ann.get_enclosing_sentence()
            if enclosing_sent[0] is not None:
                enclosing_sent_text = enclosing_sent.text(self.text)
                ent_text = e_ann.text(self.text)
                yield (
                e_ann[Annotation.LEFT] - enclosing_sent[0], e_ann[Annotation.RIGHT] - enclosing_sent[0], ent_text)

    def _entities(self):
        for ann in self.annotations:
            if ann.is_entity_target:
                yield ann


class Corpus(object):
    def __init__(self, documents: List[Document], version: str) -> None:
        self._version = version
        self._documents = documents

    @property
    def documents(self) -> List[Document]:
        return self._documents

    @property
    def version(self) -> str:
        return self._version
