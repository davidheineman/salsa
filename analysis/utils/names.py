from enum import Enum

class Edit(Enum):
    DELETION = 'Deletion'
    INSERTION = 'Insertion'
    SUBSTITUTION = 'Substitution'
    REORDER = 'Reorder'
    STRUCTURE = 'Structure'
    SPLIT = 'Split'

class Information(Enum):
    LESS = 'Generalization'
    SAME = 'Same Information'
    MORE = 'Elaboration'
    DIFFERENT = 'Different Information'

class Error(Enum):
    # Content Insertion Errors
    REPETITION = 'Repetition'
    CONTRADICTION = 'Contradiction'
    HALLUCINATION = 'Hallucination'
    FACTUAL = 'Factual Error'
    IRRELEVANT = 'Irrelevant'
    # Content Deletion Errors
    COREFERENCE = 'Coreference'
    BAD_DELETION = 'Bad Deletion'
    # Structure Errors
    BAD_REORDER = 'Bad Reorder'
    BAD_STRUCTURE = 'Bad Structure'
    BAD_SPLIT = 'Bad Split'
    # Lexical Errors
    UNNECESSARY_INSERTION = 'Unnecessary Insertion'
    UNNECESSARY_DELETION = 'Unnecessary Deletion'
    INFORMATION_REWRITE = 'Information Rewrite'
    COMPLEX_WORDING = 'Complex Wording'

class Structure(Enum):
    VOICE = "Voice"
    POS = "Part of Speech"
    TENSE = "Tense"
    GRAMMAR_NUMBER = "Grammatical Number"
    CLAUSAL = "Clausal Structure"
    TRANSITION = "Transition"

class Family(Enum):
    CONTENT = 'Conceptual'
    SYNTAX = 'Syntax'
    LEXICAL = 'Lexical'

class Quality(Enum):
    QUALITY = 'No Error'
    TRIVIAL = 'Trivial'
    ERROR = 'Error'

class ReorderLevel(Enum):
    WORD = 'Word-level'
    COMPONENT = 'Component-level'