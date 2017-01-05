from mpqa.parser import read_document, read_sentences, read_annotations


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

    def __init__(self, data_home: str, parent_dir: str, filename: str, ver: str):
        self.ver = ver
        self.text = read_document(data_home, parent_dir, filename)
        self.sentences = read_sentences(data_home, parent_dir, filename, self.ver)
        self.annotations = read_annotations(data_home, parent_dir, filename, self.ver)

    def subj_obj_sents(self):
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

    def is_annotation_in_sentence(self, ann, end_offset, start_offset):
        return ann[self.LEFT] >= start_offset \
               and ann[self.RIGHT] <= end_offset

    def is_intensive_direct_subjectivity(self, ann):
        return ann[self.TYPE] == self.DIRECT_SUBJ \
               and self.INTENSITY in ann \
               and ann[self.INTENSITY] not in self.LOW_NEUTRAL_INTENSITIES \
               and self.INSUBSTANTIAL not in ann

    def is_intensive_expressive_subjectivity(self, ann):
        return ann[self.TYPE] == self.EXPRESSIVE_SUBJ \
               and self.INTENSITY in ann \
               and ann[self.INTENSITY] not in self.LOW_INTENSITIES
