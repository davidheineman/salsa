import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans
import plotly.graph_objects as go
import numpy as np
import matplotlib as mpl
import copy
from utils.names import *
from utils.util import *
from utils.dataloader import quality_mapping
from scipy.stats import kendalltau

# Temporary for getting rid of errors
import warnings
warnings.filterwarnings("ignore")

# Maps edit id to hex color
color_mapping = {
    'deletion': '#ee2a2a',
    'substitution': '#2186eb',
    'insertion': '#64C466',
    'split': '#F7CE46',
    'reorder': '#3ca3a7',
    'structure': '#FF9F15',

    # Information.MORE: '#64C466',
    # Information.SAME: '#2186eb',
    # Information.LESS: '#ee2a2a',
    # Information.DIFFERENT: '#b103fc',

    # Less saturated versions of these colors
    Information.MORE: '#86d95d',
    Information.SAME: '#428cd6',
    Information.LESS: '#f24949',
    Information.DIFFERENT: '#b103fc',

    'new_systems/asset.test.simp.second': 'orange',
    'new_systems/turk_corpus_random.txt': 'blue',
    'systems/T5.txt': 'red',
    'systems/asset.test.simp': 'green',
    'systems/con_simplification.txt': 'purple',

    'new-wiki-1/Muss': '#FFB145',
    'new-wiki-1/T5-3B': '#aabae3',
    'new-wiki-1/T5-11B': '#8b8be0',
    'new-wiki-1/GPT-3-zero-shot': '#FF4545',
    'new-wiki-1/GPT-3-few-shot': '#FF45D7',
    'new-wiki-1/Human 1 Writing': '#45FFDA',
    'new-wiki-1/Human 2 Writing': '#45FF7A',
    'aggregated/human': '#45FFDA',

    Error.COREFERENCE: '#e65388',
    Error.REPETITION: '#c3eb98',
    Error.CONTRADICTION: '#a2cf72',
    Error.HALLUCINATION: '#b4ed77',
    Error.FACTUAL: '#8bbf52',
    Error.IRRELEVANT: '#7ea836',
    Error.INFORMATION_REWRITE: '#e19df2',
    Error.BAD_DELETION: '#eb6565',
    Error.BAD_REORDER: '#81d3d6',
    Error.BAD_STRUCTURE: '#ffc573',
    Error.BAD_SPLIT: '#f5db87',
    Error.UNNECESSARY_INSERTION: '#b0f5b7',
    Error.COMPLEX_WORDING: '#8e88f7',

    ReorderLevel.COMPONENT: '#7db39a',
    ReorderLevel.WORD: '#54b387',
    Edit.STRUCTURE: '#ffa159',
    Edit.SPLIT: '#F7CE46',
    Quality.ERROR: '#ad9ef0',

    # For ratings graph
    'generalization': '#ee2a2a',
    'paraphrase': '#2186eb',
    'elaboration': '#64C466',
    'split': '#F7CE46',
    'reorder': '#3ca3a7',
    'structure': '#FF9F15',
    'all': '#ededed',

    # For splits
    'split-1': '#F7CE46',
    'split-2': '#dbb432',
    'split-3': '#a6871f',
    'split-4': '#876a07',
}

color_mapping_override = {
    ReorderLevel.COMPONENT: '#99d1b7',
    ReorderLevel.WORD: '#79b89a',
    Edit.STRUCTURE: '#f5b078',
    Edit.SPLIT: '#f0ce5d',
}

# Maps system codes to names
system_name_mapping = {
    'new_systems/asset.test.simp.second': 'ASSET 2',
    'systems/asset.test.simp': 'ASSET 1',
    'new_systems/simple_wiki.txt': 'Simp Wiki',
    'new_systems/turk_corpus_random.txt': 'Turk Corpus',
    'systems/Dress-Ls.lower': 'DRESS',
    'systems/Hybrid.lower': 'Hybrid',
    'systems/T5.txt': 'T5',
    'systems/lstm_w_split.txt': 'LSTM Split',
    'systems/transformer_w_split.txt': 'BERT Split',
    'systems/con_simplification.txt': 'Controllable',
    'new-wiki-1/T5-3B': 'T5 3B',
    'new-wiki-1/T5-11B': 'T5 11B',
    'new-wiki-1/Muss': 'MUSS',
    'new-wiki-1/GPT-3-zero-shot': 'Zero-shot GPT-3.5',
    'new-wiki-1/GPT-3-few-shot': 'Few-shot GPT-3.5',
    'new-wiki-1/Human 1 Writing': 'Human 1',
    'new-wiki-1/Human 2 Writing': 'Human 2',
    'aggregated/human': 'Human',

    'new-wiki-4/Ctrl-T5-3b': 'T5 3B Ctrl',
    'new-wiki-4/Ctrl-T5-11b': 'T5 11B Ctrl',
    'new-wiki-4/Alpaca-7b': 'Alpaca 7B',
    'new-wiki-4/Vicuna-7b': 'Vicuna 7B',
    'new-wiki-4/Davinci-003': 'GPT-3.5',
    'new-wiki-4/Turbo': 'ChatGPT', 
    'new-wiki-4/GPT-4': 'GPT-4',

    'aggregated/asset': 'ASSET',
    'aggregated/turk': 'Turk Corpus',
    'aggregated/simpeval': 'SimpEval'
}

# Don't need this 
impact_mapping_for_visualization = {
    'error': Quality.ERROR,
    'trivial': Quality.TRIVIAL,
    'no error': Quality.QUALITY
}

# Maps error codes to names, don't need this
error_name_mapping = {
    Error.COREFERENCE: 'Coreference',
    Error.INFORMATION_REWRITE: 'Information Rewrite',
    Error.REPETITION: 'Repetition',
    Error.CONTRADICTION: 'Contradiction',
    Error.HALLUCINATION: 'Hallucination',
    Error.IRRELEVANT: 'Irrelevant',
    Error.UNNECESSARY_INSERTION: 'Unnecessary Insertion',
    Error.COMPLEX_WORDING: 'Complex Wording'
}

# When saving, use a high DPI
# plt.rcParams['figure.dpi'] = 300

# Ordering of labels in graphs
systems = system_name_mapping.keys()
edit_type_labels = ['insertion', 'deletion', 'substitution', 'split', 'reorder', 'structure']
all_system_labels = [x for x in [
    'systems/Hybrid.lower',
    'systems/Dress-Ls.lower',
    'systems/lstm_w_split.txt',
    'systems/transformer_w_split.txt',
    'systems/con_simplification.txt',
    'systems/T5.txt',
    'new-wiki-1/T5-3B',
    'new-wiki-1/T5-11B',
    'new-wiki-1/Muss',
    'new-wiki-1/GPT-3-zero-shot',
    'new-wiki-1/GPT-3-few-shot',
    'new_systems/turk_corpus_random.txt',
    'new_systems/simple_wiki.txt',
    'systems/asset.test.simp',
    'new_systems/asset.test.simp.second',
    'new-wiki-1/Human 1 Writing',
    'new-wiki-1/Human 2 Writing',

    'new-wiki-4/Ctrl-T5-3b',
    'new-wiki-4/Ctrl-T5-11b',
    'new-wiki-4/Alpaca-7b',
    'new-wiki-4/Vicuna-7b'
    'new-wiki-4/Davinci-003',
    'new-wiki-4/Turbo',
    'new-wiki-4/GPT-4',

    'aggregated/turk',
    'aggregated/asset',
    'aggregated/simpeval',
    'aggregated/human'
] if x in systems]

# MatPlotLib parameters
width = 0.5
plt.rcParams["figure.figsize"] = [7.5, 4]
plt.rcParams["figure.autolayout"] = True
plt.rcParams["figure.max_open_warning"] = False

# Color utils
def clamp(val, minimum=0, maximum=255):
    if val < minimum:
        return minimum
    if val > maximum:
        return maximum
    return val

def colorscale(hexstr, scalefactor):
    hexstr = hexstr.strip('#')
    if scalefactor < 0 or len(hexstr) != 6:
        return hexstr
    r, g, b = int(hexstr[:2], 16), int(hexstr[2:4], 16), int(hexstr[4:], 16)
    r = clamp(r * scalefactor)
    g = clamp(g * scalefactor)
    b = clamp(b * scalefactor)
    return "#%02x%02x%02x" % (int(r), int(g), int(b))

def edit_type_by_system(data, flipped=True, normalized=False, all_datasets=False, humans=False):
    if humans:
        humans = ['Human', 'asset', 'turk_corpus']
        data = [sent for sent in copy.deepcopy(data) if any([human in sent['system'] for human in humans])]
        for sent_id in range(len(data)):
            sys_name = data[sent_id]['system']
            if 'Human' in sys_name:
                data[sent_id]['system'] = 'aggregated/simpeval'
            elif 'asset' in sys_name:
                data[sent_id]['system'] = 'aggregated/asset'
            elif 'turk_corpus' in sys_name:
                data[sent_id]['system'] = 'aggregated/turk'

    size = (8, 4)
    width = 0.5
    if all_datasets:
        size = (10, 4)
    if humans:
        size = (4, 4)
        width = 0.8

    line_location = [4.5, 4.5]
    if all_datasets:
        line_location = [6.5, 6.5]

    # Normalized will divide the number of edits by the total number of sentences

    # Create sums of different dimensions
    sum_edit_types = {system: sum_edits(data, system=system, normalized=normalized) for system in systems}
    system_labels = [x for x in all_system_labels if x in set([sent['system'] for sent in data])]

    if flipped:
        fig, ax = plt.subplots(figsize=size)
        bottom = [0 for x in range(len(system_labels))]
        for edit_type in edit_type_labels:
            val = [sum_edit_types[label][edit_type] for label in system_labels]
            displayed_x_labels = [system_name_mapping[label] for label in system_labels]
            ax.bar(displayed_x_labels, val, width, bottom=bottom, label=edit_type.capitalize(), color=color_mapping[edit_type])
            bottom = [bottom[i] + val[i] for i in range(len(val))]
        ax.set_xlabel('System')
        ax.set_title('Edit Types by System')
        ax.set_yticks([i*round(max(bottom)/5) for i in range(6)])

        if not humans:
            ax.plot(line_location, [0, ax.get_ylim()[-1]], ls='--', c='k')

        if humans:
            ax.set_title('')
            ax.set_ylabel('# Edits per Sentence')
            ax.set_xlabel('Dataset')
    else:
        fig, ax = plt.subplots(figsize=(6, 4))
        bottom = [0 for x in range(len(edit_type_labels))]

        for system in system_labels:
            val = [sum_edit_types[system][label] for label in edit_type_labels]
            ax.bar(edit_type_labels, val, width, bottom=bottom, label=system_name_mapping[system])
            bottom = [bottom[i] + val[i] for i in range(len(val))]
        ax.set_ylabel('Number of edits')
        ax.set_title('Edit Types by System')
    ax.legend()

    out_filename = '../paper/plot/edit-type-systems.pdf'
    if humans:
        out_filename = "../paper/plot/edit-type-human-written.pdf"
    plt.savefig(out_filename, format="pdf")

    plt.show()

def system_by_information_change(data):
    # Same as the plot above but instead lexical, syntactic, and content simplification
    sum_info_change_types = {system: sum_info_change(data, system=system) for system in systems}

    fig, ax = plt.subplots(figsize=(8, 4))

    information_change_labels = [inn for inn in Information]

    system_labels = [x for x in all_system_labels if x in set([sent['system'] for sent in data])]

    bottom = [0 for x in range(len(system_labels))]
    for in_change in information_change_labels:
        val = [sum_info_change_types[label][in_change] for label in system_labels]
        displayed_x_labels = [system_name_mapping[label] for label in system_labels]
        ax.bar(displayed_x_labels, val, width, bottom=bottom, label=in_change.value, color=color_mapping[in_change])
        bottom = [bottom[i] + val[i] for i in range(len(val))]
    ax.set_xlabel('System')
    ax.set_title('Information Change by System')
    ax.set_yticks([i*round(max(bottom)/5) for i in range(6)])
    ax.plot([4.5, 4.5], [0, ax.get_ylim()[-1]], ls='--', c='k')
    ax.legend()
    plt.show()

def errors_by_system(data, include_deletions=False):
    sum_errors_types = {system: sum_errors(data, system=system) for system in systems}
    plotted_errors = [x for x in Error if x != Error.BAD_DELETION or include_deletions]
    system_labels = [x for x in all_system_labels if x in set([sent['system'] for sent in data])]

    fig, ax = plt.subplots(figsize=(10, 4))
    bottom = [0 for x in range(len(plotted_errors))]
    width = 0.15

    count = 0 
    for system in system_labels:
        val = [sum_errors_types[system][label] for label in plotted_errors]
        x = np.arange(len(plotted_errors))
        ax.bar(x-(2*width)+count*width, val, width, label=system_name_mapping[system], color=color_mapping[system])
        bottom = [bottom[i] + val[i] for i in range(len(val))]
        count += 1
    ax.set_ylabel('Number of errors')
    ax.set_title('Errors by System')
    ax.plot([5.5, 5.5], [0, ax.get_ylim()[-1]], ls='--', c='k')
    ax.plot([8.5, 8.5], [0, ax.get_ylim()[-1]], ls='--', c='k')
    ax.legend(bbox_to_anchor=(1, 1), loc="upper left")
    plt.xticks(x, [x.value for x in plotted_errors], rotation=45, ha="right")
    plt.show()

def sankey_seperated(data):
    # Create a tree of edit types, following the decision tree
    root = Node(count_data(data), 'edits', -1)

    # Ideally shouldn't be doing this...
    edit_types = [val.value.lower() for val in Edit]
    information_mapping = {val.value.lower(): val for val in Information}

    counter = 0
    for edit_type in edit_types:
        root.add_child(Node(count_data(data, edit_type=edit_type), edit_type, counter))
        counter += 1

    for node in root.get_children():
        for info_change in information_mapping.values():
            node.add_child(Node(count_data(data, edit_type=node.label, information_impact=info_change), info_change, counter))
            counter += 1
        for child in node.get_children():
            for quality_type in Quality:
                child.add_child(Node(count_data(data, edit_type=node.label, information_impact=child.label, quality_type=quality_type), quality_type, counter))
                counter += 1

    # Convert the tree to a list of nodes & links
    stack = [child for child in root.get_children()]
    nodes, links = [], []
    while len(stack) > 0:
        node = stack.pop()

        # Map color if it has a mapping
        color = 'black'
        if node.label in color_mapping.keys():
            color = color_mapping[node.label]

        # Map label if it has a mapping
        in_mapping_back = {information_mapping[k]: k for k in information_mapping}
        if node.label in in_mapping_back.keys():
            node.label = in_mapping_back[node.label]
        impact_mapping_back = {impact_mapping_for_visualization[k]: k for k in impact_mapping_for_visualization}
        if node.label in impact_mapping_back.keys():
            node.label = impact_mapping_back[node.label]

        nodes.append({'id': node.id, 'label': node.label, 'color': color})

        # Get links to children
        for child in node.get_children():
            if child.amount > 0:
                links.append({'source': node.id, 'target': child.id, 'value': child.amount})
            stack.append(child)

    # Sort nodes by id
    nodes = sorted(nodes, key=lambda x: x['id'])

    # Convert dict tree values to lists
    labels, colors = [str(x['label']) for x in nodes], [x['color'] for x in nodes]
    sources, targets, values = [x['source'] for x in links], [x['target'] for x in links], [x['value'] for x in links]

    fig = go.Figure(data=[go.Sankey(
        node = dict(
        pad = 5,
        thickness = 10,
        line = dict(color = "black", width = 0.5),
        label = labels,
        color = colors
        ),
        link = dict(
        source = sources, # index of source node
        target = targets, # index of end node
        value = values,   # amount in link
        # label = data['link']['label'],   # label of link (not necessary)
        # color = data['link']['color']
        ),
        valueformat = "d",
        valuesuffix = " edits"
    )
    ])

    fig.update_layout(title_text="Edit Type Distribution", font_size=11, width=500, height=500)
    fig.show()

def sankey_combined(data):
    # Create nodes for each type
    nodes = {}
    links = []
    length_normalized = False
    counter = 0

    # Ideally shouldn't have to do this...
    edit_types = [val.value.lower() for val in Edit]
    information_mapping = {val.value.lower(): val for val in Information}

    for edit_type in edit_types:
        nodes[edit_type] = Node(count_data(data, edit_type=edit_type, length_normalized=length_normalized), edit_type, counter)
        counter += 1

    for info_change in Information:
        nodes[info_change] = Node(count_data(data, information_impact=info_change, length_normalized=length_normalized), info_change, counter)
        counter += 1

    for quality_type in Quality:
        nodes[quality_type] = Node(count_data(data, quality_type=quality_type, length_normalized=length_normalized), quality_type, counter)
        counter += 1

    for error_type in Error:
        nodes[error_type] = Node(count_data(data, error_type=error_type, length_normalized=length_normalized), error_type, counter)
        counter += 1

    for rating in range(4):
        nodes[rating] = Node(count_data(data, quality_type=Quality.QUALITY, rating=rating, length_normalized=length_normalized), rating, counter)
        counter += 1

    for rating in range(3):
        nodes["trivial_" + str(rating)] = Node(count_data(data, quality_type=Quality.TRIVIAL, rating=rating, length_normalized=length_normalized), "trivial_" + str(rating), counter)      
        counter += 1

    # Substitution trivial insertions have no efficacy, include this
    nodes["trivial_4"] = Node(count_data(data, quality_type=Quality.TRIVIAL, rating=None, length_normalized=length_normalized), "trivial_4", counter)
    counter += 1

    # create edit_type -> info_change links
    for edit_type in edit_types:
        for info_change in Information:
            amt = count_data(data, edit_type=edit_type, information_impact=info_change, length_normalized=length_normalized)
            links.append({'source': nodes[edit_type].id, 'target': nodes[info_change].id, 'value': amt})

    # create info_change -> quality_type links
    for info_change in Information:
        for quality_type in Quality:
            amt = count_data(data, information_impact=info_change, quality_type=quality_type, length_normalized=length_normalized)
            links.append({'source': nodes[info_change].id, 'target': nodes[quality_type].id, 'value': amt})

    # create quality_type -> error_type links
    for quality_type in Quality:
        for error_type in Error:
            amt = count_data(data, quality_type=quality_type, error_type=error_type, length_normalized=length_normalized)
            links.append({'source': nodes[quality_type].id, 'target': nodes[error_type].id, 'value': amt})

    # create quality_type -> rating links
    for rating in range(4):
        amt = count_data(data, quality_type=Quality.QUALITY, rating=rating, length_normalized=length_normalized)
        links.append({'source': nodes[Quality.QUALITY].id, 'target': nodes[rating].id, 'value': amt})

    # create trivial -> rating links
    for rating in range(3):
        trivial_node_name = "trivial_" + str(rating)
        amt = count_data(data, quality_type=Quality.TRIVIAL, rating=rating, length_normalized=length_normalized)
        links.append({'source': nodes[Quality.TRIVIAL].id, 'target': nodes[trivial_node_name].id, 'value': amt})

    # create trivial -> trivial paraphrase links
    trivial_node_name = "trivial_4"
    amt = count_data(data, quality_type=Quality.TRIVIAL, rating=None, length_normalized=length_normalized)
    links.append({'source': nodes[Quality.TRIVIAL].id, 'target': nodes[trivial_node_name].id, 'value': amt})

    nodes = [{'id': x.id, 'label': x.label, 'color': 'black'} for x in nodes.values()]

    for node in nodes:
        # Map color if it has a mapping
        if node['label'] in color_mapping.keys():
            node['color'] = color_mapping[node['label']]

        # Map label if it has a mapping
        name_mapping = {}
        name_mapping.update({information_mapping[k]: k for k in information_mapping})
        name_mapping.update({impact_mapping_for_visualization[k]: k for k in impact_mapping_for_visualization})
        name_mapping.update(error_name_mapping)
        name_mapping.update({quality_mapping[k]: k for k in quality_mapping})

        # Teporary trivial name mapping
        name_mapping.update({
            "trivial_0": "0 Rating",
            "trivial_1": "1 Rating",
            "trivial_2": "2 Rating",
            "trivial_4": "Trivial Paraphrase",
        })

        if node['label'] in name_mapping.keys():
            node['label'] = name_mapping[node['label']]

    # Convert dict tree values to lists
    labels, colors = [str(x['label']).capitalize() for x in nodes], [x['color'] for x in nodes]
    sources, targets, values = [x['source'] for x in links], [x['target'] for x in links], [x['value'] for x in links]

    fig = go.Figure(data=[go.Sankey(
            node = dict(
            pad = 15,
            thickness = 10,
            line = dict(color = "black", width = 0.5),
            label = labels,
            color = colors
            ),
            link = dict(
                source = sources, # index of source node
                target = targets, # index of end node
                value = values,   # amount in link
                # label = data['link']['label'],   # label of link (not necessary)
                # color = data['link']['color']
            ),
            valueformat = "d",
            valuesuffix = " edits"
        ),]   
    )
    fig.update_layout(
        title_text="", 
        # font_family="Times New Roman",
        font_color="black",
        font_size=11, 
        width=700,
        height=500
    )
    fig.show()
    
def draw_agreement(sents, paper=False):
    sents = sorted(sents, key=lambda x: x['user'], reverse=True)
    annotator = sorted(list(set([f"{x['user']}\nBatch {x['batch']}\nHIT {x['hit_id']+1}" for x in sents])), reverse=True)

    if paper:
        annotator = ['Ann 3', 'Ann 2', 'Ann 1']

    fig, ax = plt.subplots(2)
    for axis_num, sent_type in enumerate(['original_span', 'simplified_span']):
        if sent_type == 'original_span':
            b1 = ax[axis_num].barh(annotator, [len(sents[0]['original']) for i in sents], color="blue", alpha=0.2)
        elif sent_type == 'simplified_span':
            b1 = ax[axis_num].barh(annotator, [len(sents[0]['simplified']) for i in sents], color="blue", alpha=0.2)

        for edit_type in edit_type_labels:
            entry = []
            for edit_number in range(max([len([x for x in sent['edits'] if x['type'] == edit_type]) for sent in sents])):
                e = []
                for i in range(len(sents)):
                    edits = [x for x in sents[i]['edits'] if x['type'] == edit_type]
                    if edit_number < len(edits) and edits[edit_number][sent_type] is not None:
                        e.append(edits[edit_number][sent_type])
                    else:
                        e.append([(0, 0)])
                entry.append(e)
            
            for edit in entry:
                for i in range(max([len(x) for x in edit])):
                    spans = []
                    for ann in edit:
                        if i < len(ann):
                            spans.append(ann[i])
                        else:
                            spans.append((0, 0))
                    e = spans
                    b2 = ax[axis_num].barh(annotator, [x[1]-x[0] for x in e], left=[x[0] for x in e], color=color_mapping[edit_type], alpha=0.5)

        ax[axis_num].set_xticks([])

        if paper:
            sent_type_labels = {
                'original_span': 'Original',
                'simplified_span': 'Simplification'
            }
            ax[axis_num].set_title(sent_type_labels[sent_type], fontsize=14)
            ax[axis_num].tick_params(left=False, labelsize=12)

        ax[axis_num].spines['bottom'].set_visible(False)
        ax[axis_num].spines['top'].set_visible(False)
        ax[axis_num].spines['left'].set_visible(False)
        ax[axis_num].spines['right'].set_visible(False)
    
    # plt.legend([b1, b2], ["None", "Deletion", "Substitution"], title="Edit Type", loc="upper right")
    # fig.suptitle(f'Batch {sents[0]["batch"]} | HIT {sents[0]["hit_id"]+1}')
    fig.tight_layout()
    
    if not paper:
        fig.suptitle(f"{sents[0]['original'][:30]}...")

    if paper:
        out_filename = "../paper/plot/disagreement-highlights.pdf"
        plt.savefig(out_filename, format="pdf", bbox_inches='tight', pad_inches=0.0)

    fig.show()

def avg_span_size(annotations):
    span_size = [avg([x['size'] for x in annotations if x['edit_type'] == edit_type]) for edit_type in edit_type_labels]
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(edit_type_labels, span_size, width, color=[color_mapping[label] for label in edit_type_labels])
    ax.set_xlabel('System')
    ax.set_title('Average Edit Span Size')
    plt.show()

def score_distribution(data, include_simpeval=False):
    annotations = sorted([x for y in [sent['processed_annotations'] for sent in data] for x in y], key=lambda x: x['score'])

    # Print distribution of edit scores
    n_bins = 100

    if include_simpeval:
        fig, axs = plt.subplots(2, 2, tight_layout=True)
        axs[0, 0].hist([x['score'] for x in annotations], bins=n_bins)
        axs[0, 0].set_title("Distribution of Edit Scores")

        # Print distribution of sentence scores
        axs[0, 1].hist([x['score'] for x in data], bins=n_bins)
        axs[0, 1].set_title("Distribution of Sentence Scores")

        # Print distribution of simp eval scores
        axs[1, 0].hist([i for j in [x['simpeval_scores'] for x in data if x['simpeval_scores'] is not None] for i in j], bins=n_bins)
        axs[1, 0].set_title("Distribution of SimpEval Scores")

        # Print distribution of simp eval scores
        axs[1, 1].hist([avg(x['simpeval_scores']) for x in data if x['simpeval_scores'] is not None], bins=n_bins)
        axs[1, 1].set_title("Distribution of Avg. SimpEval Scores")
        fig.show()
    else:
        fig, axs = plt.subplots(1, 2, tight_layout=True)
        axs[0].hist([x['score'] for x in annotations], bins=n_bins)
        axs[0].set_title("Distribution of Edit Scores")

        # Print distribution of sentence scores
        axs[1].hist([x['score'] for x in data], bins=n_bins)
        axs[1].set_title("Distribution of Sentence Scores")
    fig.show()

def simpeval_agreement(data, average=True):
    if (average):
        scores = []
        for sent in data:
            if sent['simpeval_scores'] is not None and len(sent['simpeval_scores']) != 0:
                scores += [(avg(sent['simpeval_scores'], prec=5), sent['score'])]
            else:
                scores += [(0, sent['score'])]
    else:
        # Simply takes the first annotator
        scores = []
        for sent in data:
            if sent['simpeval_scores'] is not None and len(sent['simpeval_scores']) != 0:
                scores.append((int(sent['simpeval_scores'][0]), sent['score']))
            else:
                scores.append((0, sent['score']))
    pts = [p for p in scores if p[0] != 0]
    kt = kendalltau([p[0] for p in pts], [p[1] for p in pts])
    plt.scatter([p[0] for p in pts], [p[1] for p in pts], c ="red", alpha=0.2)
    plt.xlabel('Average SimpEval score')
    plt.ylabel('Our score')
    plt.figtext(.1, .8, f"corr = {kt.correlation:.2f} | p = {kt.pvalue:.2f}")
    plt.title(f'SimpEval Correlation ({len(pts)} sentences)')
    plt.show()

def edit_length(data, systems, type_='edit_dist', simpeval=False, average_scores=False):
    if average_scores:
        new_data = copy.deepcopy(data)
        for id_ in set([sent['id'] for sent in data]):
            sents = [sent for sent in data if sent['id'] == id_]
            new_score = avg([sent['score'] for sent in sents])
            for i in range(len(new_data)):
                if new_data[i]['id'] == id_:
                    new_data[i]['score'] = new_score
        data = new_data

    total_sent = 0
    for system in [s for s in all_system_labels if s in systems]:
        if type_ == 'edit_dist':
            plt.ylabel('Edit Distance')
            if simpeval:
                scores = [(avg(sent['simpeval_scores'], prec=10), sent['ed']) for sent in data if sent['system'] == system]
            else:
                scores = [(sent['score'], sent['ed']) for sent in data if sent['system'] == system]
        elif type_ == 'char_diff':
            plt.ylabel('% of sentence modified')
            if simpeval:
                scores = [(avg(sent['simpeval_scores'], prec=10), sum([x['size'] for x in sent['processed_annotations']])) for sent in data if sent['system'] == system]
            else:
                scores = [(sent['score'], sum([x['size'] for x in sent['processed_annotations']])) for sent in data if sent['system'] == system]
        plt.scatter([p[0] for p in scores], [p[1] for p in scores], c=color_mapping[system], alpha=0.3, label=system_name_mapping[system])
        total_sent += len(scores)
    if simpeval:
        plt.xlabel('SimpEval score')
    else:
        plt.xlabel('Our score')
    # plt.title(f'Scoring vs. Edits ({total_sent} sentences)')
    plt.gcf().set_size_inches(7, 5)
    plt.legend()
    out_filename = f'../paper/plot/edit-distance-vs-score.pdf'
    plt.savefig(out_filename, format="pdf", bbox_inches='tight', pad_inches=0.0)
    plt.show()

def edits_by_family(data, family=None):
    fig, ax = plt.subplots(3, 1, figsize=(6, 13))
    width = 0.35

    for plt_idx, family in enumerate(Family):
        out = get_edits_by_family(data, family)
        # Get the system labels by preserving the order of systems
        system_labels = [x for x in system_name_mapping if x in out.keys()]
        x = np.arange(len(system_labels))

        # Graph the quality edits
        quality_data = {system : out[system]['quality'] for system, _ in out.items()}
        bottom = [0 for x in range(len(system_labels))]
        if family == Family.CONTENT:
            quality_iterator = Information
        elif family == Family.SYNTAX:
            quality_iterator = [x for x in ReorderLevel] + [Edit.STRUCTURE]
        elif family == Family.LEXICAL:
            quality_iterator = [Information.SAME]
        for quality_type in quality_iterator:
            val = [quality_data[label][quality_type] for label in system_labels]
            if sum(val) != 0:
                # Custom labels
                label = quality_type.value
                if family == Family.SYNTAX:
                    label = 'Quality ' + quality_type.value.lower() + ' edit'

                ax[plt_idx].bar(x - width/2 - 0.05, val, width, bottom=bottom, label=quality_type.value, color=color_mapping[quality_type])
            bottom = [bottom[i] + val[i] for i in range(len(val))]

        ax[plt_idx].set_yticks([i*round(max(bottom)/5) for i in range(6)])

        # Graph the error edits
        error_data = {system : out[system]['error'] for system, _ in out.items()}
        bottom = [0 for x in range(len(system_labels))]
        if family == Family.CONTENT:
            error_iterator = Error
        elif family == Family.SYNTAX:
            error_iterator = [x for x in ReorderLevel] + [Edit.STRUCTURE]
        elif family == Family.LEXICAL:
            error_iterator = [Error.COMPLEX_WORDING, Quality.ERROR]
        for error_type in error_iterator:
            val = [error_data[label][error_type] for label in system_labels]
            if sum(val) != 0:
                # Custom labels
                label = error_type.value
                if family == Family.SYNTAX or Family.LEXICAL:
                    if label == 'Error':
                        label = 'Grammar'
                    label += ' Error'

                ax[plt_idx].bar(x + width/2 + 0.05, val, width, bottom=bottom, label=label, color=color_mapping[error_type])
            bottom = [bottom[i] + val[i] for i in range(len(val))]

        displayed_x_labels = [system_name_mapping[label] for label in system_labels]

        if family == Family.CONTENT:
            ax[plt_idx].set_title('Conceptual Edits')
        elif family == Family.SYNTAX:
            ax[plt_idx].set_title('Syntax Edits')
        elif family == Family.LEXICAL:
            ax[plt_idx].set_title('Lexical Edits')
        
        if family == Family.LEXICAL:
            ax[plt_idx].set_xlabel('System')
        ax[plt_idx].set_xticklabels(['none'] + displayed_x_labels)
        # ax.plot([2.5, 2.5], [0, ax.get_ylim()[-1]], ls='--', c='k')
        # p5, = plot([0],  marker='None',
        #    linestyle='None', label='dummy-empty')
        # leg3 = legend([p5, p1, p2, p5, p3, p4],
        #       ['Quality Edits'] + categories + ['Error Edits'] + categories,
        #       bbox_to_anchor=(1, 1), loc="upper left", ncol=1)

        ax[plt_idx].legend(loc='upper center', bbox_to_anchor=(0.5, -0.15),
          fancybox=True, ncol=2)
        
        #.legend(bbox_to_anchor=(1, 1), loc="upper left")

        # Set the margins a little higher than the max value
        plt.ylim(0, max([sum(x.values()) for x in quality_data.values()]) + 10)

    out_filename = f'../paper/plot/edit-ratings-all.pdf'
    plt.savefig(out_filename, format="pdf")

    plt.tight_layout()
    plt.show()


def edits_by_family_separated(data, savefig=False):
    fig, ax = plt.subplots(3, 2, figsize=(6, 12))
    width = 0.7

    for plt_idx, family in enumerate(Family):
        out = get_edits_by_family(data, family)
        # Get the system labels by preserving the order of systems
        system_labels = [x for x in system_name_mapping if x in out.keys()]
        x = np.arange(len(system_labels))

        # Graph the quality edits
        quality_data = {system : out[system]['quality'] for system, _ in out.items()}
        bottom = [0 for x in range(len(system_labels))]
        if family == Family.CONTENT:
            quality_iterator = Information
        elif family == Family.SYNTAX:
            quality_iterator = [x for x in ReorderLevel] + [Edit.STRUCTURE] + [Edit.SPLIT]
        elif family == Family.LEXICAL:
            quality_iterator = [Information.SAME]
        for quality_type in quality_iterator:
            val = [quality_data[label][quality_type] for label in system_labels]
            if sum(val) != 0:
                # Custom labels
                label = quality_type.value
                # if family == Family.SYNTAX:
                #     label = 'Quality ' + quality_type.value.lower() + ' edit'
                if quality_type == Information.SAME:
                    label = 'Paraphrase'

                ax[plt_idx, 0].bar(x, val, width, bottom=bottom, label=label, color=color_mapping[quality_type])
            bottom = [bottom[i] + val[i] for i in range(len(val))]

        # Graph the error edits
        error_data = {system : out[system]['error'] for system, _ in out.items()}
        bottom = [0 for x in range(len(system_labels))]
        if family == Family.CONTENT:
            error_iterator = [e for e in Error if e != Error.UNNECESSARY_INSERTION]
        elif family == Family.SYNTAX:
            error_iterator = [x for x in ReorderLevel] + [Edit.STRUCTURE] + [Edit.SPLIT]
        elif family == Family.LEXICAL:
            error_iterator = [Error.COMPLEX_WORDING, Quality.ERROR, Error.UNNECESSARY_INSERTION]
        for error_type in error_iterator:
            val = [error_data[label][error_type] for label in system_labels]

            # This is a really awful solution, but it would be too much to change the classification of this error
            if family == Family.LEXICAL and error_type == Error.UNNECESSARY_INSERTION:
                tmp = get_edits_by_family(data, Family.CONTENT)
                tmp = {system : tmp[system]['error'] for system, _ in tmp.items()}
                val = [tmp[label][Error.UNNECESSARY_INSERTION] for label in system_labels]

            if sum(val) != 0:
                # Custom labels
                label = error_type.value
                if family == Family.SYNTAX or Family.LEXICAL:
                    if label == 'Error':
                        label = 'Grammar'
                    # label += ' Error'

                ax[plt_idx, 1].bar(x, val, width, bottom=bottom, label=label, color=color_mapping[error_type])
            bottom = [bottom[i] + val[i] for i in range(len(val))]

        displayed_x_labels = [system_name_mapping[label] for label in system_labels]

        font_size = 8

        ax[plt_idx,0].tick_params(labelsize=font_size)
        ax[plt_idx,1].tick_params(labelsize=font_size)
        
        ax[plt_idx,0].set_xticklabels(['none'] + displayed_x_labels, rotation=30, ha="right")
        ax[plt_idx,1].set_xticklabels(['none'] + displayed_x_labels, rotation=30, ha='right')

        ax[plt_idx,0].spines[['right', 'top']].set_visible(False)
        ax[plt_idx,1].spines[['right', 'top']].set_visible(False)

        trans = mtrans.Affine2D().translate(10, 0)
        for t in ax[plt_idx,0].get_xticklabels() + ax[plt_idx,1].get_xticklabels():
            t.set_transform(t.get_transform()+trans)

        # ax[plt_idx,1].set_yticklabels([])

        font_size = 8
        legend_loc = (0.5, -0.35)

        if family == Family.LEXICAL:
            ax[plt_idx,0].set_xlabel('System')
            ax[plt_idx,1].set_xlabel('System')
            legend_loc = (0.5, -0.45)
        elif family == Family.CONTENT:
            ax[plt_idx,0].set_title('Success ↑ (# Quality / Sent.)')
            ax[plt_idx,1].set_title('Failure ↓ (# Error / Sent.)')

        ax[plt_idx,0].legend(loc='upper center', bbox_to_anchor=legend_loc,
            fancybox=True, ncol=2, borderaxespad=1.,fontsize=font_size,
            facecolor='white',edgecolor='black',framealpha=1,frameon=False,
            columnspacing=1,handlelength=1,handleheight=1,handletextpad=0.4,
            borderpad=0.2)

        ax[plt_idx,1].legend(loc='upper center', bbox_to_anchor=legend_loc,
            fancybox=True, ncol=2, borderaxespad=1.,fontsize=font_size,
            facecolor='white',edgecolor='black',framealpha=1,frameon=False,
            columnspacing=1,handlelength=1,handleheight=1,handletextpad=0.4,
            borderpad=0.2)

        for ha in ax[plt_idx,0].legend_.legendHandles + ax[plt_idx,1].legend_.legendHandles:
            ha.set_edgecolor("black")

        # Set the margins a little higher than the max value
        max_quality = max([sum(x.values()) for x in quality_data.values()])
        tick_range_quality = np.arange(0, max_quality*1.2, step=0.5)
        ax[plt_idx,0].set_yticks(tick_range_quality)

        # ax[plt_idx,0].set_yticks([i*round(max(bottom)/5) for i in range(6)])

        # max_error = max([sum(x.values()) for x in error_data.values()])
        # tick_range_error = np.arange(0, max_error*1.2, step=0.2)
        # ax[plt_idx,1].set_yticks(tick_range_error)

        # tick_range_quality = np.arange(0, max([sum(x.values()) for x in quality_data.values()]) + 10, step=50)
        # max_error = 101
        # if family == Family.CONTENT: 
        #     max_error = 201
        # tick_range_error = np.arange(0, max_error, step=20) # (len(data)/len(out.keys())) + 10        
        # ax[plt_idx,1].set_yticks(tick_range_error)

    # Add titles
    fig.suptitle('Conceptual Edits', fontsize=14)
    plt.figtext(0.5, (2/3) - 0.023, "Syntax Edits", va="center", ha="center", size=14)
    plt.figtext(0.5, (1/3), "Lexical Edits", va="center", ha="center", size=14)

    plt.tight_layout()
    plt.subplots_adjust(top=1.25)
    if savefig:
        out_filename = f'../paper/plot/edit-ratings-all-separated.pdf'
        plt.savefig(out_filename, format="pdf", bbox_inches='tight', pad_inches=0.0)
        plt.close(fig)
    else:
        plt.show()

# Select one of : Paraphrase, Split, Structure, Reorder
# Could do this with deletions as well
def ratings_by_edit_type(data, edit_type):
    out = get_ratings_by_edit_type(data, edit_type)

    fig, ax = plt.subplots(figsize=(8, 4))
    width = 0.12

    # Get the system labels by preserving the order of systems
    system_labels = [x for x in system_name_mapping if x in out.keys()]
    x = np.arange(len(system_labels))

    custom_color_mapping = {
        'quality': {
            0: '#b8ffbf',
            1: '#91ff9c',
            2: '#61ed6f'
        },
        'trivial': '#cccccc',
        'error': {
            0: '#ffbaba',
            1: '#fc8d8d',
            2: '#f76a6a'
        }
    }

    # Graph the quality edits
    spacing = [x + width, x + 2*width, x + 3*width]
    quality_data = {system : out[system]['quality'] for system, _ in out.items()}
    for rating in range(3):
        bottom = [0 for x in range(len(system_labels))]
        val = [quality_data[label][rating] for label in system_labels]
        ax.bar(spacing[rating], val, width, label=rating + 1, color=custom_color_mapping['quality'][rating])
        
    # Graph the error edits
    spacing = [x - width, x - 2*width, x - 3*width]
    error_data = {system : out[system]['error'] for system, _ in out.items()}
    for rating in reversed(range(3)):
        bottom = [0 for x in range(len(system_labels))]
        val = [error_data[label][rating] for label in system_labels]
        ax.bar(spacing[rating], val, width,label=-rating-1, color=custom_color_mapping['error'][rating])

    # Graph the trivial edits
    trvial_data = {system : out[system]['trivial'] for system, _ in out.items()}
    bottom = [0 for x in range(len(system_labels))]
    val = [trvial_data[label] for label in system_labels]
    ax.bar(x, val, width, label=0, color=custom_color_mapping['trivial'])

    displayed_x_labels = [system_name_mapping[label] for label in system_labels]

    ax.set_title(f'{edit_type.capitalize()} Ratings by System')
    ax.set_xlabel('System')
    ax.set_xticklabels(['none'] + displayed_x_labels)
    ax.legend(bbox_to_anchor=(1, 1), loc="upper left")

    # Set the margins a little higher than the max value
    plt.ylim(0, max([max(x.values()) for x in quality_data.values()]) + 10)

    plt.show()

def avg_edit_ratings(data):
    out = get_edits_by_type(data, Quality.QUALITY)

    fig, ax = plt.subplots(figsize=(8, 4))
    width = 0.12

    # Get the system labels by preserving the order of systems
    system_labels = [x for x in system_name_mapping if x in out.keys()]
    edit_labels = list(out[list(out.keys())[0]].keys())
    x = np.arange(len(edit_labels))

    # Graph the edits
    spacing = [x - 2*width, x - width, x, x + width, x + 2*width, x + 3*width]
    for i, system in enumerate(system_labels):
        val = [out[system][label] for label in edit_labels]
        ax.bar(spacing[i], val, width, label=system_name_mapping[system]) #, color=color_mapping[edit_label])

    displayed_x_labels = [label.value for label in edit_labels]

    ax.set_title(f'Avg. Edit Rating')
    ax.set_xlabel('System')
    ax.set_xticklabels(['none'] + displayed_x_labels)
    ax.set_yticks(np.arange(0, 3, 0.25))
    ax.legend(bbox_to_anchor=(1, 1), loc="upper left")

    # Set the margins a little higher than the max value
    plt.ylim(1, 2.5)

    plt.show()

def edit_ratings_barh_old(data):
    fam = edit_ratings_by_family(data)
    fig, ax = plt.subplots(len(fam.keys()), 4)
    for i, family in enumerate(fam.keys()):
        ratings = fam[family]

        for j, system in enumerate([s for s in all_system_labels if s in ratings.keys()]):
            left = 0
            color = color_mapping[family]
            for k, rating in enumerate(ratings[system]):
                if j == 0:
                    label = family.capitalize()
                else:
                    label = ' '
                
                ax[i, j].barh(label, rating, left=left, color=color, alpha=k*(1/7))
                left += rating
            if i == 0:
                ax[i, j].set_title(system_name_mapping[system])

            ax[i, j].set_xticks([])

            ax[i, j].spines['bottom'].set_visible(False)
            ax[i, j].spines['top'].set_visible(False)
            ax[i, j].spines['left'].set_visible(False)
            ax[i, j].spines['right'].set_visible(False)

    fig.tight_layout()
    plt.show()

def edit_ratings_barh(data, include_all=True, old_formatting=False, size_weighted=False):
    if old_formatting:
        edit_ratings_barh_old(data)
        return

    fam = edit_ratings_by_family(data, size_weighted=size_weighted)
    sys = list(list(fam.values())[0].keys())

    if include_all:
        plt.rcParams["figure.figsize"] = [12.5, 2.5]
    else:
        fam.pop('all', None)
        plt.rcParams["figure.figsize"] = [11, 4.5]

    family_order = [
        'elaboration',
        'generalization',
        'paraphrase',
        'reorder',
        'split',
        'structure',
        'all'
    ]

    custom_family_mapping = {
        'elaboration': 'More Information',
        'generalization': 'Less Information',
        'paraphrase': 'Same Information',
        'reorder': 'Reorder',
        'split': 'Sentence Split',
        'structure': 'Structure',
        'all': 'All',
    }

    # fig, ax = plt.subplots(len(sys), len(fam.keys()))

    import matplotlib.gridspec as gridspec
    fig = plt.figure(figsize=(15, 3))
    gs = gridspec.GridSpec(
        len(sys)+len(sys), 
        len(fam.keys()),
        height_ratios=[i for j in [[1, 0.25] for _ in range(len(sys))] for i in j],
        width_ratios=[1 for _ in range(len(fam.keys()))], 
        hspace=0.05, 
        wspace=0.05
    )
    ax = [[plt.subplot(gs[i, j]) for j in range(len(fam.keys()))] for i in range(2*len(sys))]
    # ax = gs.subplots(fig)

    for i, family in enumerate(family_order):
        ratings = fam[family]

        for j, system in enumerate([s for s in all_system_labels if s in ratings.keys()]):
            # for spacing
            curr_ax = ax[(j*2)+1][i]
            curr_ax.set_xticks([])
            curr_ax.spines['bottom'].set_visible(False)
            curr_ax.spines['top'].set_visible(False)
            curr_ax.spines['left'].set_visible(False)
            curr_ax.spines['right'].set_visible(False)
            curr_ax.set_visible(False)

            # curr_ax = ax[j, i]
            curr_ax = ax[j*2][i]

            left = 0
            curr_plots = []
            for k, rating in enumerate(ratings[system]):
                if k < 3:
                    color = '#5e5e5e'
                elif k > 3:
                    color = color_mapping[family]
                else:
                    color = '#b8b398'

                if i == 0:
                    label = system_name_mapping[system]
                    if 'GPT' in label:
                        label = label.replace(' GPT', '\nGPT')
                    curr_ax.tick_params(left=False, labelsize=12)
                else:
                    label = ' '
                    curr_ax.axis('off')
                # curr_ax.tick_params(labelleft=False, labelright=False)
                # curr_ax.tick_params(axis='both', which='both', length=0)
                
                dem = 3
                scalar = [0.6, 1, 1.3, 1, 0.8, 1, 1.2]
                color = colorscale(color, scalar[k]) # abs(3-k)*(1/dem) + (1/dem)

                # curr_ax.margins(y=0.05, x=0.01)

                bar_plot = curr_ax.barh(label, rating, left=left, color=color, edgecolor='#cfcfcf',
                    height=1,) ##6e6e6e # alpha=abs(3-k)*(1/dem) + (1/dem)
                curr_ax.tick_params(labelsize=12)
                
                curr_ax.add_patch(mpl.patches.Rectangle((0, -0.5), 1, 1, fill=None, alpha=1, linewidth=0.5))

                curr_plots += [bar_plot]
                left += rating
            if j == 0:
                # add padding
                curr_ax.set_title(custom_family_mapping[family], pad=15, fontsize=14)
            elif j == len(ratings.keys()) - 1:
                labels = [f'–{abs(x-3)} ' if x - 3 < 0 else f'+{x-3}' for x in range(7)]
                legend_font_size = 10.5
                legend = curr_ax.legend(
                    handles=curr_plots, labels=labels, bbox_to_anchor=(0.5, -1.4), # -1.2 
                    loc='lower center', borderaxespad=0.,fontsize=legend_font_size,ncol=7, 
                    facecolor='white',edgecolor='black',framealpha=1,frameon=False,
                    columnspacing=0.1,handlelength=1,handleheight=1,
                    handletextpad=-1, borderpad=0, title=' Error         Quality', # handletextpad Should be 0
                    title_fontproperties={'size': legend_font_size},
                )
                handles, labels = curr_ax.get_legend_handles_labels()
                for ha in curr_ax.legend_.legendHandles:
                    ha.set_edgecolor("black")
                for text in legend.get_texts():
                    text.set_position((0, -15))

            curr_ax.set_xticks([])

            curr_ax.spines['bottom'].set_visible(False)
            curr_ax.spines['top'].set_visible(False)
            curr_ax.spines['left'].set_visible(False)
            curr_ax.spines['right'].set_visible(False)

    # plt.subplots_adjust(wspace=0, hspace=0, bottom=0.5)

    # Arbitrary text to force padding at bottom of figure
    fig.text(0.5, -0.1, ' ', ha='center', fontsize=14)

    plt.tight_layout()
    plt.subplots_adjust()

    if size_weighted:
        out_filename = "../paper/plot/edit-level-scores.pdf"
    else:
        out_filename = "../paper/plot/appendix/edit-level-scores-non-weighted.pdf"
    plt.savefig(out_filename, format="pdf", bbox_inches='tight', pad_inches=0.0)

    plt.show()