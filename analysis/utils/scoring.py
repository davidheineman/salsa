import copy
import math
from utils.names import *

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

def get_params(op):
    """
    Get parameters for only a certain family of edits
    """
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
