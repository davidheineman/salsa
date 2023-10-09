from scipy.stats import kendalltau, pearsonr, spearmanr
import heapq

metrics = ['bleu', 'sari', 'bertscore', 'comet', 'lens_score', 'lens-salsa']
condition_name_mapping = {
    'salsa_lexical_quality_score': 'Lexical',
    'salsa_syntax_quality_score': 'Syntax',
    'salsa_conceptual_quality_score': 'Conceptual',
    'salsa_lexical_error_score': 'Lexical',
    'salsa_syntax_error_score': 'Syntax',
    'salsa_conceptual_error_score': 'Conceptual',
    'salsa_error_score': 'All Error',
    'salsa_quality_score': 'All Quality',
    'salsa_score': 'All Edits'
}
prec = 3

def render_table(scores):
    all_results = []

    # Calculate metric corrleation
    for metric in metrics:
        sys_results = []
        for condition in condition_name_mapping.keys():
            p = pearsonr(
                [float(s[f'{condition}']) for s in scores if s[metric] is not None], 
                [float(s[metric]) for s in scores if s[metric] is not None]
            )
            sp = spearmanr(
                [float(s[f'{condition}']) for s in scores if s[metric] is not None], 
                [float(s[metric]) for s in scores if s[metric] is not None]
            )
            results = (round(sp[0], prec), round(p[0], prec))
            sys_results += [results]
        all_results += [sys_results]

    # Render LaTeX table
    delimiters = [
        '\multirow{3}{*}{\\rotatebox[origin=c]{90}{Quality}}',
        '\multirow{3}{*}{\\rotatebox[origin=c]{90}{Error}}',
        '\multirow{3}{*}{\\rotatebox[origin=c]{90}{All}}'
    ]

    out = ''
    for i, condition in enumerate(condition_name_mapping.keys()):
        line = ''

        if i % 3 == 0:
            if i != 0:
                line += '\\midrule\n'
            line += f'{delimiters[int(i/3)]} '
            
        line += f'& {condition_name_mapping[condition]} & '
        a_max_p, b_max_p = heapq.nlargest(2, [x[i][0] for x in all_results])
        a_max_sp, b_max_sp = heapq.nlargest(2, [x[i][1] for x in all_results])
        for j, metric in enumerate(metrics):
            p = all_results[j][i][0]
            sp = all_results[j][i][1]

            if str(p) == 'nan':
                p = '---'
            if str(sp) == 'nan':
                sp = '---'

            if p == a_max_p:
                p = f'\\textbf{{{round(p, prec):.3f}}}'
            elif sp == a_max_sp:
                sp = f'\\textbf{{{round(sp, prec):.3f}}}'
            elif p == b_max_p:
                p = f'\\underline{{{round(p, prec):.3f}}}'
            elif sp == b_max_sp:
                sp = f'\\underline{{{round(sp, prec):.3f}}}'
            else:
                p = f'{round(p, prec):.3f}'

            # line += f'{p} & {sp} & '
            line += f'{p} & '
        out += line[:-2] + '\\tabularnewline\n'
    print(out)