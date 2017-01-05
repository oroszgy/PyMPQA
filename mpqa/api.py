from typing import List, Tuple, Union, Dict, Generator

Position = Tuple[int, int]
AnnotationValue = Union[str, List[str]]
Annotation = Dict[str, AnnotationValue]


class Document(object):
    LEFT = 'left'
    RIGHT = 'right'
    TYPE = 'type'
    EXPRESSIVE_SUBJ = 'GATE_expressive-subjectivity'
    DIRECT_SUBJ = 'GATE_direct-subjective'
    INTENSITY = 'intensity'
    LOW_INTENSITIES = ('low')
    LOW_NEUTRAL_INTENSITIES = ('low', 'neutral')
    OBJ = "objective"
    SUBJ = "subjective"
    INSUBSTANTIAL = "insubstantial"

    def __init__(self, text: str, sentences: List[str], annotations: List[Annotation]) -> None:
        self.text = text
        self.sentences = sentences
        self.annotations = annotations

    def subj_obj_sents(self) -> Generator[Tuple[str, str], None, None]:
        for start_offset, end_offset in self.sentences:
            sentence_intensity_counter = 0
            for ann in self.annotations:
                if self.is_annotation_in_sentence(ann, end_offset, start_offset):
                    if self.is_intensive_direct_subjectivity(ann):
                        sentence_intensity_counter += 1

                    if self.is_intensive_expressive_subjectivity(ann):
                        sentence_intensity_counter += 1

            sentence_text = self.text[start_offset:end_offset]
            yield (sentence_text, self.SUBJ) if sentence_intensity_counter > 0 \
                else (sentence_text, self.OBJ)

    def is_annotation_in_sentence(self, ann, end_offset: int, start_offset: int) -> bool:
        return ann[self.LEFT] >= start_offset \
               and ann[self.RIGHT] <= end_offset

    def is_intensive_direct_subjectivity(self, ann) -> bool:
        return ann[self.TYPE] == self.DIRECT_SUBJ \
               and self.INTENSITY in ann \
               and ann[self.INTENSITY] not in self.LOW_NEUTRAL_INTENSITIES \
               and self.INSUBSTANTIAL not in ann

    def is_intensive_expressive_subjectivity(self, ann) -> bool:
        return ann[self.TYPE] == self.EXPRESSIVE_SUBJ \
               and self.INTENSITY in ann \
               and ann[self.INTENSITY] not in self.LOW_INTENSITIES


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
