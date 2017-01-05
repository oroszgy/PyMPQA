"""
Details of the annotation scheme is described here: https://github.com/jyuhuan/mpqa/wiki/Types-of-Annotations
"""
from typing import List, Tuple, Generator


class Sentence(tuple):
    def text(self, doc_text: str) -> str:
        return doc_text[self[0]: self[1]]


class Annotation(dict):
    LEFT = 'left'
    RIGHT = 'right'
    SENTENCE = 'sentence'
    TYPE = 'type'
    ATTITUDE_TYPE = "GATE_attitude"
    TARGET_TYPE = "GATE_target"
    EXPRESSIVE_SUBJ_TYPE = 'GATE_expressive-subjectivity'
    DIRECT_SUBJ_TYPE = 'GATE_direct-subjective'
    INTENSITY = 'intensity'
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
            if Annotation.ID in ann.keys() and ann[Annotation.ID] == self[Annotation.TARGET_LINK]:
                return ann

    def text(self, doc_text: str) -> str:
        return doc_text[self[Annotation.LEFT]: self[Annotation.RIGHT]]

    def get_enclosing_sentence(self):
        return self[Annotation.SENTENCE]

    @property
    def is_intensive_direct_subjectivity(self) -> bool:
        return self[Annotation.TYPE] == Annotation.DIRECT_SUBJ_TYPE \
               and Annotation.INTENSITY in self \
               and self[Annotation.INTENSITY] not in Annotation.LOW_NEUTRAL_INTENSITY_VALUES \
               and Annotation.INSUBSTANTIAL not in self

    @property
    def is_intensive_expressive_subjectivity(self) -> bool:
        return self[Annotation.TYPE] == Annotation.EXPRESSIVE_SUBJ_TYPE \
               and Annotation.INTENSITY in self \
               and self[Annotation.INTENSITY] not in Annotation.LOW_INTENSITY_VALUES

    @property
    def is_attitude(self) -> bool:
        return self[Annotation.TYPE] == Annotation.ATTITUDE_TYPE


class Document(object):
    OBJ = "objective"
    SUBJ = "subjective"

    def __init__(self, text: str, sentences: List[Sentence], annotations: List[Annotation]) -> None:
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

    def targets_w_attitudes(self):
        for ann in self.annotations:
            if ann.is_attitude:
                ann_text = ann.text(self.text)
                enclosing_sentence_text = ann.get_enclosing_sentence().text(self.text)
                target_ann = ann.find_target_annotation(self.annotations)
                target_text = target_ann.text(self.text)
                yield (ann_text, target_text, enclosing_sentence_text)


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
