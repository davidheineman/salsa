import sys, json, csv
from jsonargparse import ArgumentParser

sys.path.append('..')

from utils import metric_correlation, seq_classification
from lens_salsa import LENS_SALSA

def batch_evaluate(metric, data, tagging_model=False, use_references=False, threshold=0.5):
    complex = [sent['src'] for sent in data]
    simple = [sent['mt'] for sent in data]
    references = [sent['references'] for sent in data] if use_references else None

    pred = metric.score(complex, simple, references=references, gpus=1)

    # Recover tagging predictions and add to scores
    lens_scores = pred.scores
    if tagging_model:
        output_tags = pred.metadata.subword_scores
        tagged = metric.recover_output(output_tags, threshold=threshold)

    out = []
    for i, sent in enumerate(data):
        sent['lens-salsa'] = lens_scores[i]
        if tagging_model:
            sent['src_tagged'] = tagged[i]['src_tagged']
            sent['mt_tagged'] = tagged[i]['mt_tagged']
        out += [sent]

    return data

def run_evaluation(model_path, val_data_path=None, output_filename=None, threshold=0.5):
    metric = LENS_SALSA(model_path, rescale=True)

    train_data_path = metric.model.hparams.train_data[0].replace('~', '/nethome/dheineman3')
    if val_data_path is None:
        val_data_path = metric.model.hparams.validation_data[0].replace('~', '/nethome/dheineman3')

    # Use validation data to calculate correlation
    with open(val_data_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = []
        for row in reader:
            for field in reader.fieldnames:
                if field not in row:
                    row[field] = None
            data += [row]

    print(f"Calculating scores for {len(data)} sentences")

    lens_scores = batch_evaluate(metric, data, metric.is_tagging_model, threshold=threshold)

    # Sanity: Exclude any scores for sentences in train file
    with open(train_data_path, newline='') as csv_file:
        csv_data = csv.DictReader(csv_file)
        train_data = [row for row in csv_data]
    num_filtered = 0
    train_inputs, train_outputs = [s['src'] for s in train_data], [s['mt'] for s in train_data]
    for s in lens_scores:
        if s['src'] in train_inputs or s['mt'] in train_outputs:
            s['lens-salsa'] = None
            num_filtered += 1
    print(f"Detected {num_filtered}/{len(lens_scores)} sentences in valid set and test set, filtering...")

    # Print correlation with SALSA scores
    metric_correlation.render_table(lens_scores)

    # Get edit-level performance
    if metric.is_tagging_model:
        fine_grained_errors = not metric.continuous_word_labels and len(metric.span_tokens) == 2
        seq_classification.render_table(lens_scores, metric, fine_grained_errors)

    # Output scores into final file
    if output_filename:
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(lens_scores, f, indent=4)

def read_arguments() -> ArgumentParser:
    parser = ArgumentParser(description="Command for evaluating LENS-SALSA models.")
    parser.add_argument('--model_path', type=str, required=True, help='Path to the trained model file')
    parser.add_argument('--val_data_path', type=str, default=None, help='Path to validation data, if not the data specified in the model config (optional)')
    parser.add_argument('--output_file', type=str, default=None, help='Output file name (optional)')
    return parser

if __name__ == '__main__':
    parser = read_arguments()
    cfg = parser.parse_args()
    
    for threshold in [0.000001, 0.00001, 0.0001, 0.001, 0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.75, 1]:
        print(threshold)
        run_evaluation(cfg.model_path, cfg.val_data_path, cfg.output_file, threshold)

