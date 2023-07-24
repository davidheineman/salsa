import copy
from sty import fg, bg, ef, rs
from utils.names import *

# try not to use this
mapping = {
    'deletion': 0,
    'substitution': 1,
    'insertion': 3,
    'split': 2,
    'reorder': 4,
    'structure': 5
}

# Utility class for creating edit type trees
class Node:
    def __init__(self, amount, label, id):
        self.children = []
        self.amount = amount
        self.label = label
        self.id = id

    def add_child(self, child):
        self.children.append(child)

    def get_children(self):
        return self.children

    def __str__(self):
        return str([self.label, self.amount, [str(x) for x in self.children]])

# Counts some slice of annotations
def count_data(data, edit_type=None, information_impact=None, quality_type=None, error_type=None, rating=None, length_normalized=False):
    annotations = [i for j in [x['processed_annotations'] for x in data] for i in j]
    if edit_type != None:
        annotations = [x for x in annotations if x['edit_type'] == edit_type]
    if information_impact != None:
        annotations = [x for x in annotations if x['information_impact'] == information_impact]
    if quality_type != None:
        annotations = [x for x in annotations if x['type'] == quality_type]
    if error_type != None:
        annotations = [x for x in annotations if x['error_type'] == error_type]
    if rating != None:
        annotations = [x for x in annotations if x['rating'] == rating]

    if length_normalized:
        return sum([x['size'] for x in annotations])

    return len(annotations)

# Given a set of spans, returns all spans of a given type
def get_spans_by_type(spans, type_):
    val = [x for x in spans if x[0] == mapping[type_]]
    # This is extremely broken, but split edits exclusively index starting at 0
    if type_ == 'split' and any([x[3] == 0 for x in val]):
        for v in val: 
            v[3] += 1
    return val

# Given a sentence, returns number of edits for each type
def count_edits(sent):
    out = {}
    for type_ in mapping.keys():
        count = len(set(
            [x[3] for x in get_spans_by_type(sent['original_spans'], type_)] + 
            [x[3] for x in get_spans_by_type(sent['simplified_spans'], type_)]
        ))
        out[type_] = count

    for count in out:
        if count == None:
            raise Exception(sent)
    
    return out

# Given a sentence, returns ids for each type
def get_edit_ids(sent):
    out = {}
    for type_ in mapping.keys():
        out[type_] = set(
            [x[3] for x in get_spans_by_type(sent['original_spans'], type_)] + 
            [x[3] for x in get_spans_by_type(sent['simplified_spans'], type_)]
        )
    return out

# Counts structure changes
def count_composite_edits(sent, parent_id, edit_type):
    out = {}
    for type_ in mapping.keys():
        orig = get_spans_by_type(sent['original_spans'], edit_type)
        simp = get_spans_by_type(sent['simplified_spans'], edit_type)

        orig = [x for x in orig if len(x) > 4]
        simp = [x for x in simp if len(x) > 4]

        count = len(set(
            [x[5] for x in orig if x[3] == parent_id and x[4] == mapping[type_]] + 
            [x[5] for x in simp if x[3] == parent_id and x[4] == mapping[type_]]
        ))
        out[type_] = count
    return out

def count_info_change(sent):
    out = {}
    for type_ in Information:
        out[type_] = sum([1 for ann in sent['processed_annotations'] if ann['information_impact'] == type_])
    return out

# Gets sum of all edits, optionally filtered by system
def sum_edits(data, system=None, normalized=False):
    if system is not None:
        data = get_sentences_for_system(data, system)
    
    # Initialize mapping array
    out = {}
    for type_ in mapping.keys():
        out[type_] = 0

    for sent in data:
        num_edits = count_edits(sent)
        for type_ in num_edits.keys():
            out[type_] += num_edits[type_]
        
    if normalized:
        for type_ in out.keys():
            if len(data) != 0:
               out[type_] /= len(data)
    return out

# Get sum of all information change types
def sum_info_change(data, system=None):
    if system is not None:
        data = get_sentences_for_system(data, system)

    out = {}
    for type_ in Information:
        out[type_] = 0
    for sent in data:
        num_edits = count_info_change(sent)
        for type_ in num_edits.keys():
            out[type_] += num_edits[type_]
    return out

# Gets sum of errors
def sum_errors(data, system=None):
    if system is not None:
        data = get_sentences_for_system(data, system)

    ann = [i for j in [sent['processed_annotations'] for sent in data] for i in j]
    errors = [a for a in ann if a['type'] == Quality.ERROR]
    
    # Initialize mapping array
    out = {}
    for type_ in Error:
        errors_by_type = [e for e in errors if e['error_type'] == type_]
        out[type_] = len(errors_by_type)
    return out

# Returns sentences for system
def get_sentences_for_system(data, system):
    return [x for x in data if x['system'] == system]

# Return the comments within the data
def get_comments(data):
    for entry in data:
        if 'comment' in entry.keys():
            print(f"{entry['user'].upper()} - HIT {str(entry['id']+1)}: {entry['comment']}\n")

# Returns the average of a list
def avg(lst, prec=2):
    if len(lst) == 0:
        return 0
    return round(sum(lst) / len(lst), prec)

def best_performing(data):
    # Print highest scoring sentences
    print("Highest Scoring:")
    sents = sorted(data, key=lambda x: x['score'], reverse=True)[:5]
    for sent in sents:
        print(f"{sent['user']} - Batch {sent['batch']}, HIT {sent['hit_id']+1} (ID {sent['id']}) - {str(sent['score'])}")
    highest = sents

    # Print lowest scoring sentences
    print("\nLowest scoring:")
    sents = sorted(data, key=lambda x: x['score'])[:5]
    for sent in sents:
        print(f"{sent['user']} - Batch {sent['batch']}, HIT {sent['hit_id']+1} (ID {sent['id']}) - {str(sent['score'])}")
    lowest = sents
    return highest, lowest

# A lot of the '0's are sentences with a single, trivial substitution
def is_single_substitution(sent):
    return len(sent['processed_annotations']) == 1 and sent['processed_annotations'][0]['edit_type'] == 'substitution' and sent['processed_annotations'][0]['type'] == Quality.TRIVIAL

# Get sentences which scored a 0
def zero_scoring_sents(data):
    sents = [sent for sent in data if sent['score'] == 0 and len(sent['edits']) != 0 and not is_single_substitution(sent)][:5]
    for sent in sents:
        print(get_sent_info(sent))
    return sents

# Print information about a sentence's annotator, batch, HIT
def get_sent_info(sent):
    return f"{sent['user']} - Batch {sent['batch']}, HIT {sent['hit_id']+1} (ID {sent['id']})"

# Converts the sentence to a dictionary of (start, end) -> {}
def generate_token_dict(sent):
    counter = 0
    tokens = {}
    for word in sent.split(' '):
        tokens[(counter, counter + len(word))] = {}
        counter = counter + len(word) + 1
    return tokens

# Converts sentence to dictionary of (start, end) -> {edit_type: #}
def get_annotations_per_token(sents, sent_type, remove_none=True, collapse_composite=False, \
    tagging=False, remove_reorder=False, get_alignment=False):
    edit_dict_value = sent_type + '_span'
    tokens = generate_token_dict(sents[0][sent_type])
    
    # Iterate through all annotators' edits
    for sent in sents:
        edits = sent['edits']

        # Optionally collapse composite edits
        if collapse_composite:
            edits = copy.deepcopy(edits)

            # Seperate structure edits into a separate list
            edits_with_composite_edits = [x for x in edits if x['type'] == 'structure' or x['type'] == 'split']
            edits = [x for x in edits if x['type'] != 'structure' and x['type'] != 'split']

            # Add their components to the new list
            for edit in edits_with_composite_edits:
                for composite_edit in edit['composite_edits']:
                    edits += [{
                        'type': composite_edit['type'],
                        'original_span': composite_edit['original_span'],
                        'simplified_span': composite_edit['simplified_span'],
                    }]
            
            # Optionally replaces reorder edits with substitutions
            if remove_reorder:
                new_edits = []

                for e in edits:
                    # Retains component-level reorder
                    if e['type'] == 'reorder':
                        e['type'] = 'substitution'
                    new_edits += [e]

                    # Removes component-level reorder edits
                    # if e['type'] == 'reorder':
                    #     if 'annotation' in e.keys() and e['annotation'][4] == 'word':
                    #         e['type'] = 'substitution'
                    # if e['type'] != 'reorder':
                    #     new_edits += [e]         
                edits = new_edits
        
        for edit in edits:
            if edit[edit_dict_value] is None:
                continue

            for elongated_span in edit[edit_dict_value]:
                composite_spans = [(entry[0] + elongated_span[0], entry[1] + elongated_span[0]) for entry in list(generate_token_dict(sents[0][sent_type][elongated_span[0]:elongated_span[1]]).keys())]

                for c_span in composite_spans:
                    if c_span in tokens.keys():
                        if edit['type'] not in tokens[c_span].keys():
                            tokens[c_span][edit['type']] = 0 if not tagging and not get_alignment else []
                        if tagging:
                            ann = [ann for ann in sent['processed_annotations'] if ann['id'] == edit['id'] and edit['type'] == ann['edit_type']][0]
                            rating = ann['rating'] + 1 if ann['rating'] is not None else 0
                            if ann['type'] == Quality.ERROR:
                                rating = -rating
                            elif ann['type'] == Quality.TRIVIAL:
                                rating = 0

                            tokens[c_span][edit['type']] += [{
                                'family': ann['family'],
                                'word_qe': 'good' if ann['type'] == Quality.QUALITY else 'bad',
                                'word_rating': rating,
                                'edit_qe': True,
                                'error_type': ann['error_type']
                            }]
                        else:
                            if get_alignment:
                                other_sent_type = 'original' if sent_type == 'simplified' else 'simplified'
                                other_edit = edit[f'{other_sent_type}_span']
                                other_edit = other_edit if other_edit is not None else []
                                tokens[c_span][edit['type']] += other_edit
                            else:
                                tokens[c_span][edit['type']] += 1
                    elif c_span is None:
                        pass
                    else:
                        print(edit)
                        print("there's a problem boss")
    
    # Remove spans with no annotations from any annotator
    if remove_none:
        keys = list(tokens.keys())
        for entry in keys:
            if len(tokens[entry].keys()) == 0:
                del tokens[entry]
    return tokens
    
def st(text):
    return bg(int('FF', 16), int('9F', 16), int('15', 16)) + fg(0) + text + fg.rs + bg.rs 

# Highlights a type of sentence change. TODO: coloring doesn't work
def print_changes(sents, type_='structure'):
    for sent in sents:
        edits = [x for x in sent['edits'] if x['type'] == type_]
        if len(edits) == 0:
            continue

        orig = sent['original']
        simp = sent['simplified']
        print(f'{get_sent_info(sent)}\n')
        for edit in edits:
            # A bit obnoxious, but if there are no spans in the edit, we have to convert it to an empty array
            orig_spans = edit['original_span'] if edit['original_span'] is not None else []
            simp_spans = edit['simplified_span'] if edit['simplified_span'] is not None else []

            c = 0
            for span in orig_spans:
                orig = orig[:span[0]+c] + st(orig[span[0]+c:span[1]+c]) + orig[span[1]+c:]
                c += len(st(''))
            c = 0
            for span in simp_spans:
                simp = simp[:span[0]+c] + st(simp[span[0]+c:span[1]+c]) + simp[span[1]+c:]
                c += len(st(''))
            print(orig)
            print(simp, end='\n\n')

# Calculates Levenshtein Distances using DP
def edit_dist(s1, s2):
    if len(s1) > len(s2):
        s1, s2 = s2, s1

    distances = range(len(s1) + 1)
    for i2, c2 in enumerate(s2):
        distances_ = [i2+1]
        for i1, c1 in enumerate(s1):
            if c1 == c2:
                distances_.append(distances[i1])
            else:
                distances_.append(1 + min((distances[i1], distances[i1 + 1], distances_[-1])))
        distances = distances_
    return distances[-1]

def get_edits_by_family(data, family, combine_humans=True, errors_by_sent=False):
    out = {}
    systems = set([sent['system'] for sent in data])
    if combine_humans:
        systems = set([sent['system'] for sent in data if 'Human' not in sent['system']] + ['aggregated/human'])
    for system in systems:
        if combine_humans and system == 'aggregated/human':
            sents = [sent for sent in data if 'Human' in sent['system']]
        else:
            sents = [sent for sent in data if sent['system'] == system]
        anns = [ann for sent in sents for ann in sent['processed_annotations']]
        selected = [ann for ann in anns if ann['family'] == family]

        quality_edits = [ann for ann in selected if ann['type'] == Quality.QUALITY]
        quality_annotations = {}
        if family == Family.CONTENT:
            for impact in Information:
                quality_annotations[impact] = len([ann for ann in quality_edits if ann['information_impact'] == impact])
        elif family == Family.SYNTAX:
            for reorder_level in ReorderLevel:
                quality_annotations[reorder_level] = len([ann for ann in quality_edits if ann['reorder_level'] == reorder_level])
            quality_annotations[Edit.STRUCTURE] = len([ann for ann in quality_edits if ann['edit_type'] == Edit.STRUCTURE.value.lower()])
            quality_annotations[Edit.SPLIT] = len([ann for ann in quality_edits if ann['edit_type'] == Edit.SPLIT.value.lower()])
        elif family == Family.LEXICAL:
            quality_annotations[Information.SAME] = len(quality_edits)

        error_annotations = {}
        # Whether to count errors by occuring once in a sentence, or each time they occur
        if errors_by_sent:
            if family == Family.CONTENT:
                for error_type in Error:
                    error_annotations[error_type] = len([sent for sent in sents if any([ann['error_type'] == error_type and ann['type'] == Quality.ERROR and ann['family'] == Family.CONTENT for ann in sent['processed_annotations']])])
            elif family == Family.SYNTAX:
                for reorder_level in ReorderLevel:
                    error_annotations[reorder_level] = len([sent for sent in sents if any([ann['reorder_level'] == reorder_level and ann['type'] == Quality.ERROR for ann in sent['processed_annotations']])])  # len([ann for ann in error_edits if ann['reorder_level'] == reorder_level])
                error_annotations[Edit.STRUCTURE] = len([sent for sent in sents if any([ann['edit_type'] == Edit.STRUCTURE.value.lower() and ann['type'] == Quality.ERROR for ann in sent['processed_annotations']])]) # len([ann for ann in error_edits if ann['edit_type'] == Edit.STRUCTURE.value.lower()])
                error_annotations[Edit.SPLIT] = len([sent for sent in sents if any([ann['edit_type'] == Edit.SPLIT.value.lower() and ann['type'] == Quality.ERROR for ann in sent['processed_annotations']])])
            elif family == Family.LEXICAL:
                # TODO: This should be grammar error, not Quality.ERROR
                # In general, counting the grammar edits is really weird
                error_annotations[Quality.ERROR] = len([sent for sent in sents if any([ann['grammar_error'] and ann['type'] == Quality.ERROR for ann in sent['processed_annotations']])]) # len([ann for ann in anns if ann['grammar_error']])
                error_annotations[Error.COMPLEX_WORDING] = len([sent for sent in sents if any([ann['error_type'] == Error.COMPLEX_WORDING and ann['type'] == Quality.ERROR for ann in sent['processed_annotations']])]) # len([ann for ann in error_edits if ann['error_type'] == Error.COMPLEX_WORDING])
                error_annotations[Error.UNNECESSARY_INSERTION] = len([sent for sent in sents if any([ann['error_type'] == Error.UNNECESSARY_INSERTION and ann['type'] == Quality.ERROR for ann in sent['processed_annotations']])]) # len([ann for ann in error_edits if ann['error_type'] == Error.UNNECESSARY_INSERTION])
        else:
            error_edits = [ann for ann in selected if ann['type'] == Quality.ERROR]
            if family == Family.CONTENT:
                for error_type in Error:
                    error_annotations[error_type] = len([ann for ann in error_edits if ann['error_type'] == error_type])
            elif family == Family.SYNTAX:
                for reorder_level in ReorderLevel:
                    error_annotations[reorder_level] = len([ann for ann in error_edits if ann['reorder_level'] == reorder_level])
                error_annotations[Edit.STRUCTURE] = len([ann for ann in error_edits if ann['edit_type'] == Edit.STRUCTURE.value.lower()])
                error_annotations[Edit.SPLIT] = len([ann for ann in error_edits if ann['edit_type'] == Edit.SPLIT.value.lower()])
            elif family == Family.LEXICAL:
                # TODO: This should be grammar error, not Quality.ERROR
                # In general, counting the grammar edits is really weird
                error_annotations[Quality.ERROR] = len([ann for ann in anns if ann['grammar_error']])
                error_annotations[Error.COMPLEX_WORDING] = len([ann for ann in error_edits if ann['error_type'] == Error.COMPLEX_WORDING])
                error_annotations[Error.INFORMATION_REWRITE] = len([ann for ann in error_edits if ann['error_type'] == Error.INFORMATION_REWRITE])

        out[system] = {'quality': quality_annotations, 'error': error_annotations}

    # Since we're combining 2 sets of human annotations, we have to divide by 2
    # if combine_humans:
    #     for vala in out.keys():
    #         if vala == 'aggregated/human':
    #             for valb in out[vala].keys():
    #                 for valc in out[vala][valb].keys():
    #                     out[vala][valb][valc] /= 2

    # Instead, divide by all sentences
    for vala in out.keys():
        if combine_humans and vala == 'aggregated/human':
            total =  len([sent for sent in data if 'Human' in sent['system']])
        else:
            total = len([sent for sent in data if sent['system'] == vala])
        for valb in out[vala].keys():
            for valc in out[vala][valb].keys():
                out[vala][valb][valc] /= total
            
    return out

def get_ratings_by_edit_type(data, edit_type, combine_humans=False, size_weighted=False):
    information_change = None
    if edit_type == 'paraphrase':
        family = Family.LEXICAL
        edit_type = 'substitution'
    elif edit_type == 'split' or edit_type == 'structure' or edit_type == 'reorder':
        family = Family.SYNTAX
    elif edit_type == 'elaboration' or edit_type == 'generalization':
        family = Family.CONTENT
        if edit_type == 'elaboration':
            information_change = Information.MORE
        elif edit_type == 'generalization':
            information_change = Information.LESS
    else:
        raise ValueError(f'Edit type not supported for this operation: {edit_type}')

    out = {}
    systems = set([sent['system'] for sent in data])
    if combine_humans:
        systems = set([sent['system'] for sent in data if 'Human' not in sent['system']] + ['aggregated/human'])
    for system in systems:
        score_range = 3

        if combine_humans and system == 'aggregated/human':
            sents = [sent for sent in data if 'Human' in sent['system']]
        else:
            sents = [sent for sent in data if sent['system'] == system]
        anns = [ann for sent in sents for ann in sent['processed_annotations']]
        selected = [ann for ann in anns if ann['family'] == family]
        selected = [ann for ann in anns if ann['edit_type'] == edit_type]

        # Selecting content edits
        if edit_type == 'elaboration' or edit_type == 'generalization':
            selected = [ann for ann in anns if ann['information_impact'] == information_change]

        quality_edits = [ann for ann in selected if ann['type'] == Quality.QUALITY]
        quality_annotations = {}
        for rating in range(score_range):
            edits = [ann for ann in quality_edits if ann['rating'] == rating]
            if size_weighted:
                quality_annotations[rating] = len(edits)*avg([e['token_size'] for e in edits], prec=10) / len(selected)
            else:
                quality_annotations[rating] = len(edits) / len(selected)
        
        error_edits = [ann for ann in selected if ann['type'] == Quality.ERROR]
        error_annotations = {}
        for rating in range(score_range):
            edits = [ann for ann in error_edits if ann['rating'] == rating]
            if size_weighted:
                error_annotations[rating] = len(edits)*avg([e['token_size'] for e in edits], prec=10) / len(selected)
            else:
                error_annotations[rating] = len(edits) / len(selected)

        edits = [ann for ann in selected if ann['type'] == Quality.TRIVIAL]
        if size_weighted:
            trivial_amt = len(edits)*avg([e['size'] for e in edits], prec=10) / len(selected)
        else:
            trivial_amt = len(edits) / len(selected)

        out[system] = {
            'quality': quality_annotations, 
            'trivial': trivial_amt,
            'error': error_annotations
        }

    # if combine_humans:
    #     for vala in out.keys():
    #         if vala == 'aggregated/human':
    #             for valb in out[vala].keys():
    #                 if type(out[vala][valb]) == dict:
    #                     for valc in out[vala][valb].keys():
    #                         out[vala][valb][valc] /= 2
    #                 else:
    #                     out[vala][valb] /= 2
    return out
    
def get_edits_by_type(data, quality_error):
    out = {}
    systems = set([sent['system'] for sent in data])
    for system in systems:
        sents = [sent for sent in data if sent['system'] == system]
        anns = [ann for sent in sents for ann in sent['processed_annotations']]
        avg_score = {}

        quality_edits = [ann for ann in anns if ann['type'] == Quality.QUALITY]
        quality_annotations = {}
        for impact in [i for i in Information if i != Information.DIFFERENT]:
            quality_annotations[impact] = [ann['rating'] for ann in quality_edits if ann['information_impact'] == impact]
        for reorder_level in ReorderLevel:
            quality_annotations[reorder_level] = [ann['rating'] for ann in quality_edits if ann['reorder_level'] == reorder_level]
        quality_annotations[Edit.STRUCTURE] = [ann['rating'] for ann in quality_edits if ann['edit_type'] == Edit.STRUCTURE.value.lower()]
        quality_annotations[Information.SAME] = [ann['rating'] for ann in quality_edits if ann['edit_type'] == Edit.SUBSTITUTION.value.lower() and ann['information_impact'] == Information.SAME]

        
        error_edits = [ann for ann in anns if ann['type'] == Quality.ERROR]
        error_annotations = {}
        for impact in [i for i in Information if i != Information.DIFFERENT]:
            error_annotations[impact] = [ann['rating'] for ann in error_edits if ann['information_impact'] == impact]
        for reorder_level in ReorderLevel:
            error_annotations[reorder_level] = [ann['rating'] for ann in error_edits if ann['reorder_level'] == reorder_level]
        error_annotations[Edit.STRUCTURE] = [ann['rating'] for ann in error_edits if ann['edit_type'] == Edit.STRUCTURE.value.lower()]
        error_annotations[Information.SAME] = [ann['rating'] for ann in error_edits if ann['edit_type'] == Edit.SUBSTITUTION.value.lower() and ann['information_impact'] == Information.SAME]
        
        
        for k in quality_annotations.keys():
            avg_score[k] = avg(quality_annotations[k] + [i for i in error_annotations[k] if i is not None])
            if k != Information.LESS:
                avg_score[k] += 1

        out[system] = avg_score
    return out

def error_rate(data):
    # What % of sentences contain at least 1 error?
    error, noterror = 0, 0
    for sent in data:
        for ann in sent['processed_annotations']:
            if ann['type'] == Quality.ERROR:
                error += 1
                break
    aloe = error/len(data)

    error, noterror = 0, 0
    for sent in data:
        for ann in sent['processed_annotations']:
            if ann['type'] == Quality.ERROR and ann['error_type'] != Error.BAD_DELETION:
                error += 1
                break
    aloe_no_del = error/len(data)

    # What % of edits were errors?
    error, noterror = 0, 0
    for sent in data:
        for ann in sent['processed_annotations']:
            if ann['type'] == Quality.ERROR:
                error += 1
            else:
                noterror += 1
    perc_error = error/(noterror+error)

    return aloe, aloe_no_del, perc_error

def edit_ratings_by_family(data, size_weighted=False, combine_humans=True):
    families = [
        'elaboration',
        'generalization',
        'split',
        'structure',
        'reorder',
        'paraphrase'
    ]
    systems = set([x['system'] for x in data])
    if combine_humans:
        systems = set([sent['system'] for sent in data if 'Human' not in sent['system']] + ['aggregated/human'])
    fam = {}
    for family in families:
        ratings = get_ratings_by_edit_type(data, family, combine_humans=True, size_weighted=size_weighted)
        total = max([sum([x if type(x) is not dict else sum(x.values()) for x in list(ratings[s].values())]) for s in systems])
        al = {}
        for system in systems:
            # Use this line to calulate the percentage at within each system
            # total = sum([x if type(x) is not dict else sum(x.values()) for x in list(ratings[system].values())])
            nl = []
            for i in range(3):
                nl += [ratings[system]["error"][i] / total]
            nl += [ratings[system]["trivial"] / total]
            for i in range(3):
                nl += [ratings[system]["quality"][i] / total]
            al[system] = nl
        fam[family] = al
    
    # TODO: Refactor this
    tmp = {}
    for family in families:
        ratings = get_ratings_by_edit_type(data, family, combine_humans=True, size_weighted=size_weighted)
        al = {}
        for system in systems:
            nl = []
            for i in range(3):
                nl += [ratings[system]["error"][i]]
            nl += [ratings[system]["trivial"]]
            for i in range(3):
                nl += [ratings[system]["quality"][i]]
            al[system] = nl
        tmp[family] = al
    all_total = max([sum([sum([tmp[f][system][i] for f in families]) for i in range(7)]) for i in range(7) for system in systems])
    # fam['all'] = {
    #     system: [
    #         sum([tmp[f][system][i] for f in families])/sum([sum([tmp[f][system][i] for f in families]) for i in range(7)]) for i in range(7)
    #     ]
    #     for system in systems
    # }

    # sum([sum([tmp[f][system][i] for f in families]) for i in range(7)])

    fam['all'] = {
        system: [
            sum([tmp[f][system][i] for f in families])/all_total for i in range(7)
        ]
        for system in systems
    }

    return fam

def count_dataset_composite_edits(data, parent_type):
    composite_edits = []
    edit_types = [val.value.lower() for val in Edit]
    for sent in data:
        edits = [x['composite_edits'] for x in sent['edits'] if x['type'] == parent_type]
        edits = [i for j in edits for i in j]
        composite_edits += edits
    counts = {}
    for type_ in [x for x in edit_types if x != 'structure' and x != 'split']:
        counts[type_] = len([x for x in composite_edits if x['type'] == type_])
    return counts