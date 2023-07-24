import csv, sys
sys.path.append('../analysis')
from utils.all import *

tag_priority = ['substitution', 'insertion', 'deletion'] # last values are high priority
tag_map = {
    'substitution': 'sub',
    'insertion': 'ins',
    'deletion': 'del',
    None: 'ok'
}

def get_edit_values(tags):
    edit_types = []

    for tag in tags.keys():
        tag_edit_types = list(tags[tag].keys())
        added_tag = None
        for t in tag_priority:
            if t in tag_edit_types:
                added_tag = t
        edit_types += [tag_map[added_tag]]

    return {
        'edit_types': edit_types
    }

def get_tag_values(tags, family_constraint=None):
    # Recover word QE
    word_qe, word_ratings, edit_qe, edit_id, word_qe_error_types = [], [], [], [], []
    for tag in tags.keys():
        ratings = [i for j in tags[tag].values() for i in j]
        if family_constraint:
            ratings = [ann for ann in ratings if ann['family'] == family_constraint]

        # {GOOD, BAD, OK}, bad > good > ok
        word_quality = 'ok'
        if any([edit['word_qe'] == 'bad' for edit in ratings]):
            word_quality = 'bad'
        elif any([edit['word_qe'] == 'good' for edit in ratings]):
            word_quality = 'good'
        word_qe += [word_quality]

        # {GOOD, BAD, BAD_CMPLX, BAD_DEL, OK}, bad > good > ok
        word_quality = 'ok'
        if any([edit['word_qe'] == 'bad' for edit in ratings]):
            word_quality = 'bad'
            if any([edit['error_type'] == Error.COMPLEX_WORDING for edit in ratings]):
                word_quality = 'bad_cmplx'
            elif any([edit['error_type'] == Error.BAD_DELETION for edit in ratings]):
                word_quality = 'bad_del'
        elif any([edit['word_qe'] == 'good' for edit in ratings]):
            word_quality = 'good'
        word_qe_error_types += [word_quality]

        # [-3, 3], greater magnitude takes prioirty
        word_rating = 0
        if len(ratings) != 0:
            word_rating = max([edit['word_rating'] for edit in ratings if edit['word_rating'] is not None] + [0], key=abs)
        word_ratings += [word_rating]

        # {EDIT, NO EDIT}, edit > no edit
        edit_qe += ['edit' if any([edit['edit_qe'] for edit in ratings]) else 'noedit']

        # {BAD, OK}, bad > ok
        word_id = 'ok'
        if any([edit['word_qe'] == 'bad' for edit in ratings]):
            word_id = 'bad'
        edit_id += [word_id]
    return {
        'word_qe': word_qe, 
        'word_ratings': word_ratings, 
        'edit_qe': edit_qe,
        'edit_id': edit_id,

        'word_qe_error_types': word_qe_error_types
    }

# Recover the sentence iteratively, as in only switch tags when the
# array value has changed
def write_tagged_sentence(sent, tags, tag_values):
    prev_value = None
    orig = sent
    out = ""
    for i, span in enumerate(list(tags.keys())):
        curr_value = tag_values[i]
        if prev_value == None:
            out += f"<{curr_value}>"
        elif prev_value != curr_value:
            out += f"</{prev_value}> <{curr_value}>"
        else:
            out += " "

        out += f'{orig[span[0]:span[1]]}'

        prev_value = curr_value
    out += f'</{prev_value}>'
    return out

def lcs(str1, str2):
    m, n = len(str1), len(str2)
    table = [[0] * (n + 1) for _ in range(m + 1)]
    max_length, end_position = 0, 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if str1[i - 1] == str2[j - 1]:
                table[i][j] = table[i - 1][j - 1] + 1
                if table[i][j] > max_length:
                    max_length = table[i][j]
                    end_position = i
    return str1[end_position - max_length:end_position]

"""
Convert a list of phrases to single word alignments using a (quite poor) rule-based system
to convert edits to word alignment
"""
def phrase_to_word_alignment(sent, in_new, out_new, out_pred_spans):
    # Create a list of words which need rule-based alignment
    word_alignments, alignment_out = [], []
    for tag in out_pred_spans:
        word_alignments += [(in_new[tag], out_new[tag])]

    for in_edit, out_edit in word_alignments:
        in_align, out_align = [None for _ in in_edit], [None for _ in out_edit]
        in_words, out_words = [sent['original'][e[0]:e[1]] for e in in_edit], [sent['simplified'][e[0]:e[1]] for e in out_edit]

        # Assign alignment to any words that are the same greeedily
        for i, in_word in enumerate(in_words):
            found = False
            for j, out_word in enumerate(out_words):
                if not found and in_word == out_word and out_align[j] is None:
                    in_align[i] = j
                    out_align[j] = i
                    found = True

        # Assign alignment to any words with > 60% overlap and > 6 chars each greedily
        for i, in_word in enumerate(in_words):
            found = False
            for j, out_word in enumerate(out_words):
                if not found and len(lcs(in_word,out_word)) > 0.6*len(in_word) and out_align[j] is None:
                    in_align[i] = j
                    out_align[j] = i
                    found = True

        # Island-based assignment algorithm: We'll basically only jump across words when both
        # pointers are ready
        i, j = 0, 0
        while i < len(in_words) or j < len(out_words):
            if in_align[i] is not None and out_align[j] is not None:
                i += 1
                j += 1
            elif in_align[i] is None:
                in_align[i] = j
                i += 1
            elif out_align[j] is None:
                out_align[j] = i
                j += 1
            else:
                in_align[i] = j
                out_align[j] = i
                i += 1
                j += 1
            if i >= len(in_words) and j < len(out_words):
                i = len(in_words) - 1
            if j >= len(out_words) and i < len(in_words):
                j = len(out_words) - 1

        
        out_align = [(in_edit[i], out_edit[in_align[i]]) for i in range(len(in_edit))] + \
            [(in_edit[out_align[i]], out_edit[i]) for i in range(len(out_edit))]
        alignment_out += sorted(list(set(out_align)))
    return alignment_out

"""
Given an alignment, some subsitutions will be full edits.
"""
def align_edits(alignment, orig_tags, simp_tags, sent, collapse_phrase_alignment=False):
    out_tmp = copy.deepcopy(alignment)

    # Get tags for spans which need alignment 
    out_pred_spans = [x[1] for x in out_tmp]
    excl = []
    for sp in out_pred_spans:
        for tag in simp_tags:
            if tag[0] == sp[0] and tag[1] == sp[1]:
                excl += [sp]
    out_pred_spans = sorted(list(set([x for x in out_pred_spans if x not in excl])))

    # Get all tags within the larger edit tag
    out_new = {}
    for sp in out_pred_spans:
        for tag in simp_tags:
            if tag[0] >= sp[0] and tag[1] <= sp[1]:
                if sp not in out_new:
                    out_new[sp] = []
                out_new[sp] += [tag]
    in_new = {}
    for sp in out_pred_spans:
        for in_tag, out_tag in out_tmp:
            if out_tag[0] == sp[0] and out_tag[1] == sp[1]:
                if sp not in in_new:
                    in_new[sp] = []
                in_new[sp] += [in_tag]

    if collapse_phrase_alignment:
        # Collapses phrases to word alignment using a rule-based system
        alignment_out = phrase_to_word_alignment(sent, in_new, out_new, out_pred_spans)
    else:
        # Adds all alignment within a phrase as an alignment
        assert in_new.keys() == out_new.keys()
        alignment_out = []
        for k in in_new.keys():
            for in_val in in_new[k]:
                for out_val in out_new[k]:
                    alignment_out += [(in_val, out_val)]

    out_tmp = sorted([x for x in out_tmp if x[1] not in out_pred_spans] + alignment_out)

    return out_tmp

def get_word_alignment(orig_tags, simp_tags, sent):
    # Get empty tags in output
    word_alignment = []
    simp_iter = 0
    simp_tags_iter = [t for t in simp_tags.keys() if len(simp_tags[t].keys()) == 0\
        and sent['simplified'][t[0]:t[1]] != '||']
    for tag in orig_tags.keys():
        tag_edit_types = list(orig_tags[tag].keys())
        if len(tag_edit_types) == 0:
            if simp_iter >= len(simp_tags_iter):
                simp_iter -= 1
            word_alignment += [(tag, simp_tags_iter[simp_iter])]
            simp_iter += 1
            pass
        elif 'deletion' in tag_edit_types:
            continue
        elif 'substitution' in tag_edit_types:
            tag_edit_values = list(set(orig_tags[tag]['substitution']))
            # May not be the best solution: alwasys take the first alignment:
            if len(tag_edit_values) != 0:
                tag_edit_values = tag_edit_values[0]
                word_alignment += [(tag, tag_edit_values)]
        else:
            raise Exception(f"Unknown tag type: {tag_edit_types}")
    return word_alignment

def print_alignment(sent, alignment):
    for t_in, t_out in alignment:
        print(f"{sent['original'][t_in[0]:t_in[1]]} -> {sent['simplified'][t_out[0]:t_out[1]]}")

# To create data format for Neural Janaca, it works a bit different. Here's some example
# data:

# It exists in this format: ID, sent1, _, sent2, _, _, _, sure_align, poss_align
# Important to note tokenization is performed via spaces

# sure_align = sure alignments
# poss_align = possible alignments
# In Chao's paper, he uses sure+poss as the default evaluation setup.

# 0:0
# Today there are only around 20,000 wild lions left in the world .
# N/A
# By one estimate , fewer than 20,000 lions exist in the wild , a drop of about 40 percent in the past two decades .
# N/A
# 1
# 1
# 5-6 6-11 7-7 8-8 9-9 10-10 12-24
# 0-0 0-1 0-2 3-4 3-5 4-4 4-5

# 1:1
# Other experts say there is little proof that grass-fed beef is healthier .
# N/A
# " There 's little definitive data to suggest grass-fed beef is healthier for you , " said Chad Carr , an associate professor in the university 's department of animal sciences .
# N/A
# 1
# 1
# 2-16 3-1 4-2 5-3 6-4 6-5 8-8 9-9 10-10 11-11 12-31
# 1-17 1-18 7-6 7-7

# 2:2
# Lindsey Carillo , 31 , grew up in a suburb but wanted to expose her kids to city life .
# N/A
# Lindsey Carillo , 31 , grew up in a suburb of Detroit but wanted to expose her kids to city living .
# N/A
# 1
# 1
# 0-0 1-1 2-2 3-3 4-4 5-5 6-6 7-7 8-8 9-9 10-12 11-13 12-14 13-15 14-16 15-17 16-18 17-19 18-20 19-21

def get_word_alignment_string(sent, collapse_phrase_alignment=False):
    orig_tags = get_annotations_per_token([sent], 'original', collapse_composite=True, remove_reorder=True, \
        remove_none=False, get_alignment=True)
    simp_tags = get_annotations_per_token([sent], 'simplified', collapse_composite=True, remove_reorder=True, \
        remove_none=False, get_alignment=True)

    word_alignment = get_word_alignment(orig_tags, simp_tags, sent)
    alignment = align_edits(word_alignment, orig_tags, simp_tags, sent, collapse_phrase_alignment)
    
    orig_tags = get_annotations_per_token([sent], 'original', collapse_composite=True, remove_reorder=True, \
        remove_none=False)
    simp_tags = get_annotations_per_token([sent], 'simplified', collapse_composite=True, remove_reorder=True, \
        remove_none=False)
    
    orig_ids = {k: i for i, k in enumerate(orig_tags.keys()) if orig_tags[k] is not set()}
    simp_ids = {k: i for i, k in enumerate(simp_tags.keys()) if simp_tags[k] is not set()}
    
    return ' '.join([f"{orig_ids[x[0]]}-{simp_ids[x[1]]}" for x in alignment])

def write_csv(filename, data):
    headers = list(data[0].keys())
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)

"""
Write data in word alignment format to .tsv
"""
def write_tsv_align(file_path, data, collapse_phrase_alignment=False):
    align_out = []
    for i, s in enumerate(data):
        align_out += [[
            f'{i}:{i}',
            s['src'],
            'N/A',
            s['mt'],
            'N/A', '1', '1',
            s['alignment'] if not collapse_phrase_alignment else s['alignment-no-phrases'],
            'N/A',
            s['alignment-error-labels-input'],
            s['alignment-error-labels-output']
        ]]

    with open(file_path, "w", encoding='utf-8') as f:
        for r in align_out:
            f.write('\t'.join(r) + '\n')
