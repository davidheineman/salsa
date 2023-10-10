import copy, os, json, csv, logging as log

from utils.util import *
from utils.names import *
from utils.scoring import *

# Setup logger
log.basicConfig(format='%(levelname)s:%(message)s', level=log.ERROR)

# File paths
simp_eval_main_path = '../data/simp_eval/simpeval_22_rate_and_rank.csv'
simp_eval_da_path = '../data/simp_eval/simpeval_22_DA.csv'
simp_eval_likert_path = '../data/simp_eval/simpeval_22_likert.csv'

# Specify metadata for an empty span
empty_span = {
    'span': None,
    'span_length': None
}

# Maps raw annotation outputs to enums or numbers
mapping = {
    'deletion': 0,
    'substitution': 1,
    'insertion': 3,
    'split': 2,
    'reorder': 4,
    'structure': 5
}
reverse_mapping = {v: k for k, v in mapping.items()}
    
quality_mapping = {
    'very bad': 0,
    'bad': 1,
    'good': 2,
    'perfect': 3,
}

simplification_quality_mapping = {
    'minor': 0,
    'somewhat': 1,
    'a lot': 2
}

severity_mapping = {
    'not at all': 0,
    'minor': 1,
    'somewhat': 2,
    'a lot': 3,
}

different_meaning_severity_mapping = {
    'minor': 0,
    'somewhat': 1,
    'very': 2,
}

error_mapping = {
    'yes': True,
    'no': False
}

impact_mapping = {
    'negative': Quality.ERROR,
    'no': Quality.TRIVIAL,
    'positive': Quality.QUALITY
}

information_mapping = {
    'less': Information.LESS,
    'same': Information.SAME,
    'more': Information.MORE,
    'different': Information.DIFFERENT
}

error_type_mapping = {
    'repetition': Error.REPETITION,
    'contradiction': Error.CONTRADICTION,
    'hallucination': Error.HALLUCINATION,
}

reorder_mapping = {
    'word': ReorderLevel.WORD,
    'component': ReorderLevel.COMPONENT
}

# Creates basic metadata about each span

# Structure also has a span[4] and span[5] entry, indicating
# the composite type and the id of the span within the structure change

def get_span_metadata(spans):
    out = []
    for type_ in mapping:
        spans_of_type = get_spans_by_type(spans, type_)
        for span in spans_of_type:
            entry = {
                'id': span[3],
                'type': type_,
                'span': (span[1], span[2]),
                'span_length': span[2] - span[1]
            }
            if type_ == 'structure' or type_ == 'split':
                entry['composite_type'] = reverse_mapping[span[4]] if len(span) > 4 else None
                entry['composite_id'] = span[5] if len(span) > 4 else None
            out += [entry]
    return out

# Creates 'edit' list for a sentence
def associate_spans(sent):
    edits = []

    # Extract metadata about each span
    orig_spans = get_span_metadata(sent['original_spans'])
    simp_spans = get_span_metadata(sent['simplified_spans'])

    # Get counts of each span type
    counts = count_edits(sent)
    for type_ in counts.keys():
        annotations = sent['annotations'][type_]
        if counts[type_] != 0 and counts[type_] + 1 > len(annotations):
            log.warning(f'{get_sent_info(sent)} has {counts[type_]} {type_} edits but {len(annotations) - 1} annotations. Likely a missing annotation. Skipping edit type...')
            edits += []
            continue
        for i in range(1, counts[type_]+1):
            # Get all spans corresponding to the ID
            orig_span = [x for x in orig_spans if x['id'] == i and x['type'] == type_]
            simp_span = [x for x in simp_spans if x['id'] == i and x['type'] == type_]

            # If the original or simplified span is missing (i.e. addition or deletion), fill in with dummy span
            orig_span = orig_span if len(orig_span) > 0 else empty_span
            simp_span = simp_span if len(simp_span) > 0 else empty_span

            # If the ID has no spans, skip
            if orig_span is empty_span and simp_span is empty_span:
                continue
                
            # Convert list of dicts to list of spans, retaining None value if necessary
            orig_span_amt = [x['span'] for x in orig_span] if orig_span is not empty_span else None
            simp_span_amt = [x['span'] for x in simp_span] if simp_span is not empty_span else None
            
            entry = {
                'type': type_,
                'id': i-1,
                'original_span': orig_span_amt,
                'simplified_span': simp_span_amt,
                'annotation': annotations[i]
            }

            # For structure edits, add composite edits
            if type_ == 'structure' or type_ == 'split':
                entry['composite_edits'] = []
                composite_count = count_composite_edits(sent, i, type_)
                for c_type_ in composite_count.keys():
                    for k in range(1, composite_count[c_type_]+1):
                        orig_composite_span = [x for x in orig_span if x['composite_id'] == k and x['composite_type'] == c_type_] if orig_span is not empty_span else []
                        simp_composite_span = [x for x in simp_span if x['composite_id'] == k and x['composite_type'] == c_type_] if simp_span is not empty_span else []

                        orig_composite_span = orig_composite_span if len(orig_composite_span) > 0 else empty_span
                        simp_composite_span = simp_composite_span if len(simp_composite_span) > 0 else empty_span

                        if orig_composite_span is empty_span and simp_composite_span is empty_span:
                            continue

                        orig_composite_span_amt = [x['span'] for x in orig_composite_span] if orig_composite_span is not empty_span else None
                        simp_composite_span_amt = [x['span'] for x in simp_composite_span] if simp_composite_span is not empty_span else None

                        entry['composite_edits'] += [{
                            'type': c_type_,
                            'id': k-1,
                            'original_span': orig_composite_span_amt,
                            'simplified_span': simp_composite_span_amt,
                        }]
            # Compile spans into edit
            edits += [entry]
    return edits

# Creates 'edit' list for all sentences
def consolidate_edits(data):
    out = copy.deepcopy(data)
    for sent in out:
        sent['edits'] = associate_spans(sent)
    return out

def process_del_info(raw_annotation):
    # ex. ['perfect', 'no', 'no']
    rating, error_type = None, None
    rating, coreference, grammar_error = raw_annotation

    # Deal with annotators sometimes not filling out all fields
    if grammar_error == '':
        log.debug(f"Couldn't process grammar for deletion: {raw_annotation}. Assuming 'no'...")
        grammar_error = 'no'
    if coreference == '':
        log.debug(f"Couldn't process coreference error for deletion: {raw_annotation}. Assuming 'no'...")
        coreference = 'no'

    rating, grammar_error, coreference = quality_mapping[rating], error_mapping[coreference], error_mapping[grammar_error]
    
    edit_quality = Quality.QUALITY
    if coreference:
        error_type = Error.COREFERENCE
        edit_quality = Quality.ERROR

    # I've manually checked this for correctness. 0 = very bad, 1 = bad
    if rating == 0 or rating == 1:
        error_type = Error.BAD_DELETION
        edit_quality = Quality.ERROR
    
    return edit_quality, rating, error_type, grammar_error

def process_add_info(raw_annotation):
    # ex. ['trivial', 'no', '', ''], ['elaboration', 'minor', 'no'], ['repetition', 'somewhat', 'no']
    rating, error_type = None, None
    
    annotation_type = raw_annotation[0]
    if (annotation_type == 'elaboration'):
        edit_quality = Quality.QUALITY
        rating, grammar_error = raw_annotation[1:]
        rating = simplification_quality_mapping[rating]
    elif (annotation_type == 'trivial'):
        helpful, rating, grammar_error = raw_annotation[1:]
        if helpful == 'yes':
            edit_quality = Quality.QUALITY
            rating = simplification_quality_mapping[rating]
        else:
            edit_quality = Quality.TRIVIAL
            # error_type = Error.UNNECESSARY_INSERTION

            # If an annotator sets a rating, then says 'no', the rating is still there
            # therefore, we should ignore this rating
            rating = None
    else:
        edit_quality = Quality.ERROR
        if (annotation_type == 'hallucination'):
            error_type, irrelevancy, rating, grammar_error = raw_annotation
            if error_mapping[irrelevancy] == True:
                error_type = Error.IRRELEVANT
        else:
            error_type, rating, grammar_error = raw_annotation
            error_type = error_type_mapping[error_type]
        rating = severity_mapping[rating]
    
    grammar_error = error_mapping[grammar_error] if grammar_error != '' else False
    return edit_quality, rating, error_type, grammar_error


def process_same_info(raw_annotation, edit_type):
    # ex. (substitution) ['positive', 'a lot', 'minor', 'no']
    # ex. (reorder) ['negative', 'a lot', '', 'no', 'word']
    # ex. (structure) ['positive', '', 'a lot', 'no'], ['positive', '', 'somewhat', 'yes']
    edit_quality, pos_rating, neg_rating, grammar_error = raw_annotation

    # Deal with annotators sometimes not filling out all fields
    if grammar_error == '':
        log.debug(f"Couldn't process grammar for substitution: {raw_annotation}. Assuming 'no'...")
        grammar_error = 'no'
        if pos_rating == '':
            log.debug(f"Couldn't process positive rating for substitution: {raw_annotation}. Assuming 'somewhat'...")
            pos_rating = 'somewhat'
  
    edit_quality, grammar_error = impact_mapping[edit_quality], error_mapping[grammar_error]

    error_type = None
    if edit_quality == Quality.QUALITY:
        rating = simplification_quality_mapping[pos_rating]
    elif edit_quality == Quality.ERROR:
        rating = severity_mapping[neg_rating]
        if edit_type == 'substitution':
            error_type = Error.COMPLEX_WORDING
        elif edit_type == 'reorder':
            error_type = Error.BAD_REORDER
        elif edit_type == 'structure':
            error_type = Error.BAD_STRUCTURE
        elif edit_type == 'split':
            error_type = Error.BAD_SPLIT
    elif edit_quality == Quality.TRIVIAL:
        rating = None

    return edit_quality, rating, error_type, grammar_error

def process_diff_info(raw_annotation):
    # ['very', 'no']
    rating, grammar_error = different_meaning_severity_mapping[raw_annotation[0]], error_mapping[raw_annotation[1]]
    return Quality.ERROR, rating, Error.INFORMATION_REWRITE, grammar_error

# So when coding the interface, substitutions follow the format:
# [quality, pos_rating, neg_rating, grammar_error]
# but syntax errors follow this format:
# [quality, neg_rating, pos_rating, grammar_error]
# this swaps the neg and pos for syntax errors
def swap_same_sub_fix(annotation):
    annotation[1], annotation[2] = annotation[2], annotation[1]

def calculate_edit_length(original_span, simplified_span):
    orig_len, simp_len = 0, 0
    if original_span is not None:
        for span in original_span:
            orig_len = span[1] - span[0]
    if simplified_span is not None:
        for span in simplified_span:
            simp_len = span[1] - span[0]
    return abs(simp_len - orig_len)

def process_annotation(edit):
    edit_type = edit['type']
    raw_annotation = edit['annotation']

    if raw_annotation == '' or raw_annotation is None:
        raise Exception(f'Could not process edit: {edit}')

    information_impact = Information.SAME
    reorder_level = None
    
    # Classify edit types into their information change
    if (edit_type == 'deletion'):
        information_impact = information_mapping['less']
    elif (edit_type == 'insertion'):
        information_impact = information_mapping['more']
    elif (edit_type == 'substitution'):
        information_impact = information_mapping[raw_annotation[0]]
        raw_annotation = raw_annotation[1:]
    elif (edit_type == 'reorder'):
        reorder_level = reorder_mapping[raw_annotation[-1]] if raw_annotation[-1] != '' else None
        raw_annotation = raw_annotation[:-1]
        swap_same_sub_fix(raw_annotation)
    elif (edit_type == 'structure' or edit_type == 'split'):
        swap_same_sub_fix(raw_annotation)
        pass

    # Process annotation based on information change
    if (information_impact == Information.LESS):
        edit_quality, rating, error_type, grammar_error = process_del_info(raw_annotation)
    elif (information_impact == Information.MORE):
        edit_quality, rating, error_type, grammar_error = process_add_info(raw_annotation)
    elif (information_impact == Information.DIFFERENT):
        edit_quality, rating, error_type, grammar_error = process_diff_info(raw_annotation)
    else:
        edit_quality, rating, error_type, grammar_error = process_same_info(raw_annotation, edit_type)

    # For berevity, we simply set the error type to ERROR if any error exists
    if error_type is not None:
        edit_quality = Quality.ERROR

    # Determine the family of edit based on edit type and information change
    edit_family = None
    if information_impact != Information.SAME:
        edit_family = Family.CONTENT
    elif edit_type == 'substitution':
        edit_family = Family.LEXICAL
    else:
        edit_family = Family.SYNTAX


    # Get the length of the edit
    size = calculate_edit_length(edit['original_span'], edit['simplified_span'])

    return {
        'edit_type': edit_type,
        'id': edit['id'],
        'information_impact': information_impact,
        'type': edit_quality,
        'family': edit_family,
        'grammar_error': grammar_error,
        'error_type': error_type,
        'rating': rating,
        'size': size,
        'token_size': edit['token_length'],
        'reorder_level': reorder_level,
        'original_span': edit['original_span'],
        'simplified_span': edit['simplified_span']
    }

# def process_annotations(annotations):
#     return [process_annotation(edit) for edit in annotations]

def consolidate_annotations(data):
    out = copy.deepcopy(data)
    idx = 0
    while idx < len(out):
        sent = out[idx]
        processed = []
        successful = True
        for edit in sent['edits']:
            # Add token length to edit
            token_length = 0
            if edit['original_span'] is not None:
                for span in edit['original_span']:
                    token_length += len(sent['original'][span[0]:span[1]].split(' '))
            if edit['simplified_span'] is not None:   
                for span in edit['simplified_span']:
                    token_length += len(sent['simplified'][span[0]:span[1]].split(' '))
            edit['token_length'] = token_length

            try: 
                processed.append(process_annotation(edit))
            except Exception as e:
                log.error(f'When processing sentence: {get_sent_info(sent)}. Caught error on: {e}. Skipping...')
                successful = False
        
        # Delete the sentence if we could not process the annotations for it
        if not successful:
            del out[idx]
            continue
        
        sent['processed_annotations'] = processed

        # Create a new entry for the 'length-normalized' size of the edit
        for i in range(len(sent['processed_annotations'])):
            sent['processed_annotations'][i]['size'] /= len(sent['original'])
        
        out[idx] = sent
        idx += 1
    return out

def add_simpeval_scores_json(data):
    # Add SimpEval scores to data ('simpeval_scores' field)
    out = copy.deepcopy(data)
    simpeval = []
    files = [i for j in [[f'../simpeval/{x}/{y}' for y in os.listdir('../simpeval/'+x)] for x in os.listdir('../simpeval/')] for i in j]
    for filename in files:
        with open(filename) as f:
            individual_annotation = json.load(f)
            simpeval += individual_annotation
    for i in range(len(out)):
        sent = out[i]
        system = sent['system']
        simpeval_sents = [entry for entry in simpeval if entry['Original'] == sent['original']]
        final = []
        for entry in simpeval_sents:
            for sentence_type in ['Deletions', 'Paraphrases', 'Splittings']:
                for entry_sent in entry[sentence_type]:
                    if entry_sent[2] == system:
                        final.append({'sentence_type': sentence_type.lower(), 'score': entry_sent[0], 'spans': entry_sent[3:]})
        scores = [x['score'] for x in final]
        out[i]['simpeval_scores'] = scores
    return out
    
def add_simpeval_scores(data, json=False):
    # JSON will get the scores from the original simpeval files
    if (json):
        return add_simpeval_scores_json(data)

    simp_eval = []
    for path in [simp_eval_main_path, simp_eval_da_path, simp_eval_likert_path]:
        with open(path, encoding='utf-8') as f:
            reader = csv.reader(f)
            keys = next(reader)
            contents = [row for row in reader]
            loaded = []
            for sent in contents:
                loaded += [{k: v for k, v in zip(keys, sent)}]
        simp_eval += [loaded]
    main, da, likert = simp_eval

    out = copy.deepcopy(data)

    # Copy the simpeval z-score, likert and DA
    for i in range(len(out)):
        sent = out[i]
        main_scores = [s for s in main if s['original'] == sent['original'] and s['system'] in sent['system']]
        da_scores = [s for s in da if s['Input.original'] == sent['original'] and s['Input.system'] in sent['system']]
        likert_scores = [s for s in likert if s['Input.original'] == sent['original'] and s['Input.system'] in sent['system']]
        
        out[i]['simpeval_scores'] = None
        if len(main_scores) != 0:
            main_scores = main_scores[0]
            out[i]['simpeval_scores'] = [float(x) for x in [main_scores['rating_1_zscore'], main_scores['rating_2_zscore'], main_scores['rating_3_zscore']]]

        out[i]['da_scores'] = None
        if len(da_scores) != 0:
            da_scores = [{
                'adequacy': float(da_score['Answer.adequacy']), 
                'fluency': float(da_score['Answer.fluency']),
                'simplicity': float(da_score['Answer.simplicity'])
            } for da_score in da_scores]
            out[i]['da_scores'] = da_scores

        out[i]['likert_scores'] = None
        if len(likert_scores) != 0:
            likert_scores = [{
                'adequacy': int(lk_score['Answer.adequacy']), 
                'fluency': int(lk_score['Answer.fluency']),
                'simplicity': int(lk_score['Answer.simplicity'])
            } for lk_score in likert_scores]
            out[i]['likert_scores'] = likert_scores
    return out

def calculate_subscores(data):
    for sent in data:
        subscores = {}
        for dim in ['content', 'syntax', 'lexical']:
            subscores[f'quality_{dim}'] = calculate_sentence_score(sent, get_params(f'quality_{dim}'))
            subscores[f'error_{dim}'] = calculate_sentence_score(sent, get_params(f'error_{dim}'))
            subscores[dim] = subscores[f'quality_{dim}'] + subscores[f'error_{dim}']
        subscores['quality'] = calculate_sentence_score(sent, get_params('quality'))
        subscores['error'] = calculate_sentence_score(sent, get_params('error'))
        subscores['all'] = subscores['quality'] + subscores['error']
        sent['subscores'] = subscores
    return data

def collapse_systems(data):
    data = copy.deepcopy(data)
    for sent in data:
        if 'new-wiki-2' or 'new-wiki-3' in sent['system']:
            sent['system'] = sent['system'].replace('new-wiki-2', 'new-wiki-1').replace('new-wiki-3', 'new-wiki-1')
    return data

def load_data(path, batch_num=None, preprocess=False, realign_ids=True, adjudicated=False):
    data = []

    if not 'annotated' in path:
        raise Exception('Currently only supports format of \"annotated\" files.')
    files = sorted([f'{path}/{x}' for x in os.listdir(path)])

    # Only include files of a specified batches
    if (batch_num is not None):
        selected_files = []
        for num in batch_num:
            selected_files.extend([x for x in files if ('batch_' + str(num)) + '_' in x])
        files = selected_files

    # Exclude corrupted file
    if 'analysis' in path:
        files = [x for x in files if 'batch_2_rachel' not in x]

    log.info(f'Loading files: {files}\n')

    # Add file and append user's name
    id_counter = 0
    batches = set([int(x.split('.')[-2].split('_')[-2]) for x in files])
    for batch_num in batches:
        for filename in [x for x in files if ('batch_' + str(batch_num)) in x]:
            with open(filename, encoding='utf-8') as f:
                pasted_annotation = []
                for entry in json.load(f):
                    pasted_annotation += [{
                        'id': -1,
                        'annotation_id': id_counter,
                        'sentence_id': -1,
                        'batch': batch_num,
                        'hit_id': entry['id'],
                        'user': filename.split('.')[-2].split('_')[-1],
                        'system': entry['system'],
                        'original': entry['original'],
                        'simplified': entry['simplified'],
                        'original_spans': entry['original_spans'],
                        'simplified_spans': entry['simplified_spans'],
                        'annotations': entry['annotations'],
                    }]
                    id_counter += 1

                # We have an issue where we need to exclude GPT outputs from
                # batches 5 and 6 because we re-do them using text-davinci-003
                if not adjudicated and (batch_num == 5 or batch_num == 6):
                    pasted_annotation = [sent for sent in pasted_annotation if 'GPT' not in sent['system']]
                
                data += pasted_annotation

    # ID is used to identify unique sentences, this WAS okay in the past because
    # each batch was the same ordering, but now that batches are randomized, this
    # needs to be re-done once sentences are loaded
    if realign_ids:
        unique_sents = [(sent['simplified'], sent['system']) for sent in data]
        unique_sents = [i for n, i in enumerate(unique_sents) if i not in unique_sents[:n]] # remove duplicates while retaining ordering
        print(f'Found {len(unique_sents)} unique sentences to create IDs from')
        new_data = []
        full_counter = 0
        for i in range(len(unique_sents)):
            sents = sorted([sent for sent in data if sent['simplified'] == unique_sents[i][0] and sent['system'] == unique_sents[i][1]], key=lambda x: x['user'])
            for sent in sents:
                # sent['sentence_id'] = i
                # sent['id'] = full_counter
                
                # Temporary fix for agreement calculations
                sent['sentence_id'] = full_counter
                sent['id'] = i
                full_counter += 1
            new_data.extend(sents)
        data = new_data

    log.info(f'Found users: {set([sent["user"] for sent in data])}\n')

    # Preprocess will violate data integrity. If you use preprocess, there's no guarentee
    # that this data will work with the interface.
    if preprocess:
        if adjudicated:
            # Have split edits start counting at 1 rather than 0
            for sent in [s for s in data if len(sent['annotations']['split'].keys()) != 0]:
                for key in sorted([int(k) for k in sent['annotations']['split'].keys()], reverse=True):
                    sent['annotations']['split'][str(key + 1)] = sent['annotations']['split'][str(key)]
                    del sent['annotations']['split'][str(key)]
        else:
            # At the very primitive level, weirdly split edits do NOT add an ambiguous None field
            for sent in data:
                sent['annotations']['split'] = [None] + sent['annotations']['split']

            data = consolidate_edits(data)                  # Adds 'edits' field
            data = consolidate_annotations(data)            # Adds 'processed_annotations' field
            
            data = add_simpeval_scores(data)                    # Adds 'simpeval_scores' field. Can optionally not take the z-score normalized scores with "json=True"
            data = calculate_sentence_scores(data)              # Adds 'score' field
            data = calculate_subscores(data)                    # Adds 'subscores' field
            data = collapse_systems(data)                       # Fix 'system' field to not distinguish between datasets
    
    return data
