import copy
import math
from utils.names import *
from scipy.stats import percentileofscore

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

# Default parameters for scoring
# default_params = {
#     'good_deletion': 7, 
#     'good_insertion': 2, 
#     'good_syntax': 6, 
#     'good_paraphrase': 2, 
#     'good_trivial_insertion': 8, 
#     'content_error': -2, 
#     'syntax_error': -1, 
#     'lexical_error': -1.5, 
#     'grammar_error': -1, 
#     'size_calculation': 'log'
# }

# Linear regression on SimpEval, seperate dimensions of quality and error
# 3.69273355, 2.93977382, 4.81632663, -0.98446881, -5.30712595, -1.03163116
# default_params = {
#     'good_deletion': 3.69273355, 
#     'good_insertion': 3.69273355,
#     'good_syntax': 2.93977382, 
#     'good_paraphrase': 4.81632663, 
#     'good_trivial_insertion': 0,
#     'content_error': -0.98446881, 
#     'syntax_error': -5.30712595, 
#     'lexical_error': -1.03163116,
#     'grammar_error': -1.03163116,
#     'size_calculation': 'exp'
# }

# Linear regression on adjudicated data
# -0.27392014  4.13118383  4.85789139  1.51360182  5.55115929 -4.12159655
# default_params = {
#     'good_deletion': 0.1955782614057374, 
#     'good_insertion': 0.1955782614057374, 
#     'good_syntax': 5.4916773148765285, 
#     'good_paraphrase': 10.759154259512686, 
#     'good_trivial_insertion': 0, 
#     'content_error': 1.796703025226618, 
#     'syntax_error': 5.051975242720761, 
#     'lexical_error': 6.128637010080399, # -
#     'grammar_error': 6.128637010080399, # -
#     'size_calculation': 'exp'
# }

default_params = {
    'good_deletion': 5.1955782614057374, 
    'good_insertion': 5.1955782614057374, 
    'good_syntax': 5.4916773148765285, 
    'good_paraphrase': 10.759154259512686, 
    'good_trivial_insertion': 0, 
    'content_error': -5.796703025226618, 
    'syntax_error': -5.051975242720761, 
    'lexical_error': 6.128637010080399, # -
    'grammar_error': 6.128637010080399, # -
    'size_calculation': 'exp'
}


def calculate_annotation_score(annotation, parameters):
    edit_score = 0

    # This will only be null for 'no impact' same info and bad trivial insertions
    if annotation['rating'] != None and annotation['rating'] != '':
        edit_score = rating_mapping[annotation['rating']]
    
    # Add bonuses for good edits
    if annotation['type'] == Quality.QUALITY or annotation['type'] == Quality.TRIVIAL:
        impact = annotation['information_impact']
        if impact == Information.LESS:
            # good deletion
            edit_score *= parameters['good_deletion']
        elif impact == Information.MORE:
            if annotation['type'] == Quality.TRIVIAL:
                # good trivial insertion
                edit_score *= parameters['good_trivial_insertion']
            elif annotation['type'] == Quality.QUALITY:
                # good insertion
                edit_score *= parameters['good_insertion']
        elif impact == Information.SAME:
            if annotation['edit_type'] == 'substitution':
                # good paraphrase
                edit_score *= parameters['good_paraphrase']
            else:
                # good syntax change
                edit_score *= parameters['good_syntax']

    # Unnecessary insertions have no severity...
    if annotation['error_type'] == Error.UNNECESSARY_INSERTION:
        edit_score = 2

    if annotation['grammar_error'] == True:
        edit_score = abs(edit_score) * parameters['grammar_error']
    elif annotation['error_type'] in content_errors:
        edit_score = abs(edit_score) * parameters['content_error']
    elif annotation['error_type'] in syntax_errors:
        edit_score = abs(edit_score) * parameters['syntax_error']
    elif annotation['error_type'] in lexical_errors:
        edit_score = abs(edit_score) * parameters['lexical_error']

    # Calculate the annotation size
    annotation_size = annotation['size']
    # Less distinction between large edits
    if parameters['size_calculation'] == 'exp':
        annotation_size = math.exp(annotation_size) - 1
    elif parameters['size_calculation'] == 'log':
        annotation_size = 1 + math.log10(annotation_size + 0.1)
    elif parameters['size_calculation'] == 'square':
        annotation_size = annotation_size*annotation_size
    elif parameters['size_calculation'] == 'none':
        annotation_size = 1
    elif parameters['size_calculation'] == 'linear':
        annotation_size = annotation_size
    
    return edit_score * annotation_size

def calculate_sentence_score(sent, parameters):
    # Calculate the score of each annotation
    for annotation in sent['processed_annotations']:
        annotation['score'] = calculate_annotation_score(annotation, parameters)
    
    # Simply sum the scores for each annotation
    return sum(annotation['score'] for annotation in sent['processed_annotations'])

def calculate_sentence_scores(data, parameters=default_params):
    out = copy.deepcopy(data)
    for sent in out:
        try:
            sent['score'] = calculate_sentence_score(sent, parameters)
        except Exception as e:
            raise Exception(f'Could not process score on {sent}. Caught exception: {e}')
    return out

# Gets parameters for only a certain family of edits
def get_params(op):
    curr_params = default_params.copy()
    params_consider = []

    if ('quality' in op):
        if ('content' in op):
            # Quality content edits
            params_consider = [
                'good_deletion',
                'good_insertion',
                'content_error'
            ]
        elif ('syntax' in op):
            # Quality syntax edits
            params_consider = [
                'good_syntax'
            ]
        elif ('lexical' in op):
            # Qualtiy lexical edits
            params_consider = [
                'good_paraphrase',
                'good_trivial_insertion',
                'grammar_error'
            ]
        else:
            # All quality edits
            params_consider = [
                'good_insertion',
                'good_deletion',
                'good_paraphrase',
                'good_trivial_insertion', 
                'good_syntax'
            ]
    elif ('error' in op):
        if ('content' in op):
            # Content errors
            params_consider = [
                'content_error'
            ]
        elif ('syntax' in op):
            # Syntax errors
            params_consider = [
                'syntax_error'
            ]
        elif ('lexical' in op):
            # Lexcial errors
            params_consider = [
                'lexical_error'
            ]
        else:
            # All error edits
            params_consider = [
                'content_error',
                'syntax_error',
                'lexical_error'
            ]

    params_consider += ['size_calculation']

    for param in curr_params.keys():
        if param not in params_consider and op != 'all':
            curr_params[param] = 0
    
    return curr_params

def get_percentile(data, score):
    systems = set([x['system'] for x in data])
    scores = {}
    for dimension in ['lexical', 'syntax', 'content', 'quality', 'error', 'all']:
        dim_scores = {}
        for system in systems:
            dim_scores[system] = percentileofscore([sent['subscores'][dimension] for sent in data if system in sent['system']], score)
        scores[dimension] = dim_scores
    return scores