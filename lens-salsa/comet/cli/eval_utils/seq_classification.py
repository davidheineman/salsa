from sklearn.metrics import precision_recall_fscore_support

def add_alignment_tokens(encoder, pred_sentences, gold_sentences, spec_t):
    # If labels are misaligned in sentences, this can lead to different tokenizations.
    # Thus add an "other sentence has an edit token here"-token to both sentences
    span_tokens = list(encoder.tokenizer.get_added_vocab().keys())
    for i in range(len(pred_sentences)):
        pred, gold = pred_sentences[i].lower(), gold_sentences[i].lower()
        pred_idx, gold_idx = 0, 0

        # Force solution to encoding issue
        pred = pred.replace('âģĵ', '–').replace('âģ', '').replace('ļ', '’')\
            .replace('ã©', 'é').replace('ã¨', 'è').replace('ľ', '“')\
            .replace('ŀ', '”').replace('ãń', 'í').replace('ã¡', 'á')\
            .replace('¡', 'á').replace('ã', '') # .replace('')

        while pred_idx < len(pred) and gold_idx < len(gold):
            found = False
            for token in span_tokens:
                if pred[pred_idx:pred_idx+len(token)] == token:
                    pred_idx += len(token)
                    gold = gold[:gold_idx] + spec_t + gold[gold_idx:]
                    gold_idx += len(spec_t)
                    found = True
                if gold[gold_idx:gold_idx+len(token)] == token:
                    gold_idx += len(token)
                    pred = pred[:pred_idx] + spec_t + pred[pred_idx:]
                    pred_idx += len(spec_t)
                    found = True
            if not found:
                assert pred[pred_idx] == gold[gold_idx], f'{pred[pred_idx]} {gold[gold_idx]}\n{pred}\n{gold}'
                gold_idx += 1
                pred_idx += 1
        pred_sentences[i], gold_sentences[i] = pred, gold
    
    # Add filler token
    encoder.tokenizer.add_tokens([spec_t])

    return pred_sentences, gold_sentences
    
def get_predictions(encoder, pred_sentences, gold_sentences, filler_token_id):
    # Use model tokenizer to get masked inputs
    pred_labels = encoder.subword_tokenize(pred_sentences, True, filler_token_id)['in_span_mask']
    gold_labels = encoder.subword_tokenize(gold_sentences, True, filler_token_id)['in_span_mask']

    # For debugging.
    # print(f"Filler token: {filler_token_id}")
    # for i in range(len(scores)):
    #     pad_token_id = -1
    #     pred = encoder.subword_tokenize([pred_sentences[i]], True, filler_token_id)
    #     gold = encoder.subword_tokenize([gold_sentences[i]], True, filler_token_id)

    #     if len([
    #             x.masked_select(x.ne(pad_token_id)).tolist()
    #             for x in pred['in_span_mask'].unbind(dim=0)
    #         ][0]) != len([
    #             x.masked_select(x.ne(pad_token_id)).tolist()
    #             for x in gold['in_span_mask'].unbind(dim=0)
    #         ][0]):
    #         print("mismatch:")
    #         print(pred)
    #         print(gold)
    #         print(pred_sentences[i])
    #         print(gold_sentences[i])

    # Convert masked inputs to set of lists and merge
    pad_token_id = encoder.in_span_mask_pad_id
    pred_labels = [
        x.masked_select(x.ne(pad_token_id)).tolist()
        for x in pred_labels.unbind(dim=0)
    ]
    gold_labels = [
        x.masked_select(x.ne(pad_token_id)).tolist()
        for x in gold_labels.unbind(dim=0)
    ]

    return pred_labels, gold_labels

def render_table(scores, metric, error_types=False):
    encoder, source_column, target_column, span_tokens = metric.model.encoder, \
            metric.source_column, metric.target_column, metric.span_tokens

    spec_t = '<spec>'

    column_names = {
        'src': ['src_tagged', source_column],
        'mt': ['mt_tagged', target_column],
    }

    # Evaluate for specific error types
    if error_types:
        column_names['src'][1] = 'word_qe_error_types_original'
        column_names['mt'][1] = 'word_qe_error_types_simplified'
        error_type_vocab = ['bad_cmplx', 'bad_del']
        for token in error_type_vocab:
            encoder.add_span_tokens(f'<{token}>', f'</{token}>', False)

    pred_labels, gold_labels = [], []
    for col in list(column_names.keys()):
        pred_sentences = [s[column_names[col][0]] for s in scores]
        gold_sentences = [s[column_names[col][1]] for s in scores]

        pred_sentences, gold_sentences = add_alignment_tokens(encoder, pred_sentences, gold_sentences, spec_t)
        filler_token_id = encoder.tokenizer.get_added_vocab()[spec_t]
        preds, golds = get_predictions(encoder, pred_sentences, gold_sentences, filler_token_id)
        
        pred_labels += preds
        gold_labels += golds

    # Convert set of lists to single list
    new_preds, new_golds = [], []
    for x, y in zip(pred_labels, gold_labels):
        if len(x) == len(y):
            new_preds += [x]
            new_golds += [y]
        else:
            print(f"Excluding two inputs of different sizes:\n{x}\n{y}")
    pred_labels, gold_labels = new_preds, new_golds

    pred_labels = [i for j in pred_labels for i in j]
    gold_labels = [i for j in gold_labels for i in j]

    assert len(pred_labels) == len(gold_labels)

    if isinstance(span_tokens[0], int):
        tk_iter = {s: s for s in span_tokens}
    else:
        tk_iter = {i + 1: s for i, s in enumerate(span_tokens)}
        tk_iter[0] = 'ok'
        
        if error_types:
            error_type_idx = []
            for token in error_type_vocab:
                error_type_idx += [len(tk_iter)]
                tk_iter[len(tk_iter)] = token

    # token_map = {
    #     'ok': 'No change',
    #     'good': 'Quality',
    #     'bad': 'Error  '
    # }
    
    # Calculate metrics based on predictions
    print('\t\tPrec\tRecall\tF1')
    print('LENS-SALSA:')
    for token_idx, token in tk_iter.items():
        p, g = [i == token_idx for i in pred_labels], [i == token_idx for i in gold_labels]
        if error_types:
            if token == 'bad':
                # true if gold is bad or any error token
                g = [any([i == j for j in [token_idx] + [error_type_idx]]) for i in gold_labels]
            elif token in error_type_vocab:
                p = [i == 2 for i in pred_labels]
                g = [i == token_idx for i in gold_labels]
        precision, recall, f1, support = precision_recall_fscore_support(g, p, average='binary', zero_division=0)
        print(f'{token}:\t{precision:.2f}\t{recall:.2f}\t{f1:.2f}')

    print('\nBaseline:')
    for token_idx, token in tk_iter.items():
        p, g = [0 == token_idx for _ in gold_labels], [i == token_idx for i in gold_labels]
        precision, recall, f1, support = precision_recall_fscore_support(g, p, average='binary', zero_division=0)
        print(f'{token}:\t{precision:.2f}\t{recall:.2f}\t{f1:.2f}')