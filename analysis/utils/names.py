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
    REPETITION = 'Repetition'
    CONTRADICTION = 'Contradiction'
    HALLUCINATION = 'Hallucination'
    FACTUAL = 'Factual Error'
    IRRELEVANT = 'Irrelevant'
    COREFERENCE = 'Coreference'
    BAD_DELETION = 'Bad Deletion'
    BAD_REORDER = 'Bad Reorder'
    BAD_STRUCTURE = 'Bad Structure'
    BAD_SPLIT = 'Bad Split'
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

content_errors = [
    Error.HALLUCINATION,
    Error.CONTRADICTION,
    Error.REPETITION,
    Error.IRRELEVANT,
    Error.FACTUAL,
    Error.COREFERENCE,
    Error.BAD_DELETION
]

syntax_errors = [
    Error.BAD_REORDER,
    Error.BAD_STRUCTURE,
    Error.BAD_SPLIT
]

lexical_errors = [
    Error.COMPLEX_WORDING,
    Error.INFORMATION_REWRITE,
    Error.UNNECESSARY_INSERTION
]

rating_mapping = {
    0: 1,
    1: 2,
    2: 3,
    3: 4
}

default_params = {
    'good_deletion': 5.1955782614057374, 
    'good_insertion': 5.1955782614057374, 
    'good_syntax': 5.4916773148765285, 
    'good_paraphrase': 10.759154259512686, 
    'good_trivial_insertion': 0, 
    'content_error': -5.796703025226618, 
    'syntax_error': -5.051975242720761, 
    'lexical_error': 6.128637010080399,
    'grammar_error': 6.128637010080399,
    'size_calculation': 'exp'
}