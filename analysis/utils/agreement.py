from utils.util import get_annotations_per_token, generate_token_dict
from statsmodels.stats import inter_rater as irr
import numpy as np

def token_level_disagreement(data, collapse_composite=False, majority_disagreement=False):
    total_agreement = []
    MAX_HIT = max([x['id'] for x in data])+1
    for sent_id in range(0, MAX_HIT):
        sents = [x for x in data if x['id'] == sent_id]
        orig_tokens = get_annotations_per_token(sents, 'original', collapse_composite=collapse_composite)
        simp_tokens = get_annotations_per_token(sents, 'simplified', collapse_composite=collapse_composite)

        arr_edits = []
        for edits in list(orig_tokens.values()) + list(simp_tokens.values()):
            out = []
            for k, v in edits.items():
                for amt in range(v):
                    out += [k]
            for i in range(3 - len(out)):
                out += [None]
            arr_edits += [out]

        if majority_disagreement:
            # This takes edits with a 2 agreeing annotators and 1 disagreeing annotator
            # and reports agreement between the majority and minority classes
            disagreement = []
            for edit in arr_edits:
                majority, minority = None, None
                if edit[0] == edit[1]:
                    majority = edit[0]
                    minority = edit[2]
                elif edit[1] == edit[2]:
                    majority = edit[1]
                    minority = edit[0]
                elif edit[0] == edit[2]:
                    majority = edit[0]
                    minority = edit[1]
                
                if majority is None or minority is None or majority == minority:
                    continue
            
                disagreement += [[majority, minority]]
        else:
            # This replicates each edit and calculates pairwise agreement
            # [A1, A2]
            # [A2, A3]
            # [A3, A1]
            interwoven = []
            for edit in arr_edits:
                interwoven += [[edit[0], edit[1]]]
                interwoven += [[edit[1], edit[2]]]
                interwoven += [[edit[0], edit[2]]]
            
            disagreement = []
            for edit in interwoven:
                # Important point, could be 'or'
                if edit[0] is None or edit[1] is None:
                    continue
                # Cannot display agreement
                if edit[0] == edit[1]:
                    continue
                disagreement += [edit]

        total_agreement += disagreement
    return total_agreement

def get_second_order_annotations_per_token(sents, sent_type, remove_none=True):
    edit_dict_value = sent_type + '_span'
    tokens = generate_token_dict(sents[0][sent_type])
    
    # Iterate through all annotators' edits
    for sent in sents:
        edits = sent['edits']
        
        for edit in edits:
            if edit[edit_dict_value] is None:
                continue

            for elongated_span in edit[edit_dict_value]:
                composite_spans = [
                    (entry[0] + elongated_span[0], entry[1] + elongated_span[0]) 
                    for entry in list(
                        generate_token_dict(sents[0][sent_type][elongated_span[0]:elongated_span[1]]).keys()
                    )
                ]

                for c_span in composite_spans:
                    if c_span in tokens.keys():                       
                        type_ = edit['type']

                        # Extract subtype from edit entry
                        if type_ == 'substitution':
                            subtype = edit['annotation'][0]
                            if subtype == 'more':
                                type_ = 'elaboration_substitution'
                            elif subtype == 'less':
                                type_ = 'generalization_substitution'
                            elif subtype == 'same':
                                type_ = 'paraphrasing_substitution'
                            elif subtype == 'different':
                                type_ = 'paraphrasing_different'
                            else:
                                print(edit)
                        elif type_ == 'reorder':
                            subtype = edit['annotation'][-1]
                            if subtype == 'word':
                                type_ = 'word_reorder'
                            elif subtype == 'component':
                                type_ = 'component_reorder'
                            else:
                                continue
                            # If the annotator does not specify, we skip

                        # Increment the edit type
                        if type_ not in tokens[c_span].keys():
                            tokens[c_span][type_] = 0
                        tokens[c_span][type_] += 1
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

def get_error_stats(data, error):
    total_agreement = None
    MAX_HIT = max([x['id'] for x in data])+1
    for sent_id in range(0, MAX_HIT):
        sents = [x for x in data if x['id'] == sent_id]

        sents_errors = []
        for sent in sents:
            errors = []
            for ann in sent['processed_annotations']:
                if (error.value == 'grammar_error' and ann['grammar_error']) or ann['error_type'] == error:
                    errors += [1]
                else:
                    errors += [0]
            sents_errors += [1 if any(errors) == True else 0]

        # Converts error array to 0/1 mapping using alphabetical ordering
        if len(sents_errors) == 3:
            if total_agreement is None:
                total_agreement = np.asarray([sents_errors])
            else:
                total_agreement = np.append(total_agreement, np.asarray([sents_errors]), axis=0)

    if total_agreement.sum() == 0:
        print(f'No {error.value} errors', end='\n\n')
        return None

    stats = {}
    agg = irr.aggregate_raters(total_agreement)
    stats['fleiss'] = irr.fleiss_kappa(agg[0], method='fleiss')

    # Delete columns with all 0s
    total_agreement = total_agreement.T
    idx = np.argwhere(np.all(total_agreement[..., :] == 0, axis=0))
    total_agreement = np.delete(total_agreement, idx, axis=1)
    total_agreement = total_agreement.T

    # % two agree
    two_agree = []
    for entry in total_agreement:
        two_agree.append(np.sum(entry) >= 2)
    stats['two'] = 100*sum(two_agree) / total_agreement.shape[0]

    # % frequency
    stats['freq'] = 100*len(total_agreement) / MAX_HIT

    return stats