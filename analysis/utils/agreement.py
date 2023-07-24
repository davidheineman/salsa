# Returns whether two spans are exactly the same
def span_agree(span1, span2):
    if (span1[0] == None and span2[0] == None) or (span1[0][0] == span2[0][0] and span1[0][1] == span2[0][1]):
        if (span1[1] == None and span2[1] == None) or (span1[1][0] == span2[1][0] and span1[1][1] == span2[1][1]):
            return True
    return False

# Returns whether all the spans within two annotations are exactly the same
def ann_agree(ann1, ann2):
    if len(ann1) != len(ann2):
        return False
    for i in range(len(ann1)):
        if not span_agree(ann1[i], ann2[i]):
            return False
    return True

# Returns the number of all three, two of three and no annotators agreeing
# drop_no_spans: whether to drop sentences with no annotations
def calculate_agreement(data, edit_type, drop_no_spans=False):
    agreement = [0, 0, 0]
    for id in set([x['id'] for x in data]):
        sents = [x for x in data if x['id'] == id]
        
        # Extract the span changes for each edit type
        spans1 = [(x['original_span'], x['simplified_span']) for x in [x for x in sents[0]['edits'] if x['type'] == edit_type]]
        spans2 = [(x['original_span'], x['simplified_span']) for x in [x for x in sents[1]['edits'] if x['type'] == edit_type]]
        spans3 = [(x['original_span'], x['simplified_span']) for x in [x for x in sents[2]['edits'] if x['type'] == edit_type]]
            
        # skip when there were no spans to identify
        if drop_no_spans and len(spans1) == 0 and len(spans2) == 0 and len(spans3) == 0:
            continue

        ag1 = ann_agree(spans1, spans2)
        ag2 = ann_agree(spans2, spans3)
        ag3 = ann_agree(spans1, spans3)

        if ag1 and ag2 and ag3:
            agreement[0] += 1
        elif ag1 or ag2 or ag3:
            agreement[1] += 1
        else:
            agreement[2] += 1    
    a, b, c = agreement
    return a, b, c