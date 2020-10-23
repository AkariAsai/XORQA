from __future__ import print_function
from collections import Counter
import string
import re
import argparse
import json
import sys
import jsonlines

def read_jsonlines(eval_file_name):
    lines = []
    print("loading examples from {0}".format(eval_file_name))
    with jsonlines.open(eval_file_name) as reader:
        for obj in reader:
            lines.append(obj)
    return lines


def normalize_answer(s):
    """Lower text and remove punctuation, articles and extra whitespace."""
    def remove_articles(text):
        return re.sub(r'\b(a|an|the)\b', ' ', text)

    def white_space_fix(text):
        return ' '.join(text.split())

    def remove_punc(text):
        exclude = set(string.punctuation)
        return ''.join(ch for ch in text if ch not in exclude)

    def lower(text):
        return text.lower()

    return white_space_fix(remove_articles(remove_punc(lower(s))))


def f1_score(prediction, ground_truth):
    prediction_tokens = normalize_answer(prediction).split()
    ground_truth_tokens = normalize_answer(ground_truth).split()
    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0, 0,0
    precision = 1.0 * num_same / len(prediction_tokens)
    recall = 1.0 * num_same / len(ground_truth_tokens)
    f1 = (2 * precision * recall) / (precision + recall)
    #print(precision)
    return f1, precision, recall


def exact_match_score(prediction, ground_truth):
    return (normalize_answer(prediction) == normalize_answer(ground_truth))


def metric_max_over_ground_truths(metric_fn, prediction, ground_truths):
    scores_for_ground_truths = []
    scores_prec = []
    scores_recall = []
    for ground_truth in ground_truths:
        if metric_fn == f1_score:
            score, prec, recall = metric_fn(prediction, ground_truth)
            scores_prec.append(prec)
            scores_recall.append(recall)
        else:
            score = metric_fn(prediction, ground_truth)
        scores_for_ground_truths.append(score)
    if metric_fn == f1_score:
        return max(scores_for_ground_truths), max(scores_prec), max(scores_recall)
    else:
        return max(scores_for_ground_truths)


def evaluate(dataset, predictions, per_lang=False, lang="ja"):
    f1 = exact_match = total = 0
    precision = recall = 0
    for qa in dataset:
        if per_lang is True and lang != qa["lang"]:
            continue
        total += 1
        if qa['id'] not in predictions:
            message = 'Unanswered question ' + qa['id'] + \
                ' will receive score 0.'
            print(message, file=sys.stderr)
            continue

        ground_truths = qa["answers"]
        prediction = predictions[qa['id']]["answer"] if isinstance( predictions[qa['id']], dict) else predictions[qa['id']] 
        exact_match += metric_max_over_ground_truths(
            exact_match_score, prediction, ground_truths)
        f1_tmp, prec_tmp, recall_tmp = metric_max_over_ground_truths(
            f1_score, prediction, ground_truths)
        f1 += f1_tmp
        precision += prec_tmp
        recall += recall_tmp
    if total == 0:
        print("no examples in this language")
        return False
    exact_match = 100.0 * exact_match / total
    f1 = 100.0 * f1 / total
    precision = 100.0 * precision / total 
    recall = 100.0 * recall / total
    return {'exact_match': exact_match, 'f1': f1, "precision": precision, "recall": recall}


if __name__ == '__main__':
    expected_version = '1.1'
    parser = argparse.ArgumentParser(
        description='Evaluation for SQuAD ' + expected_version)
    parser.add_argument('--data_file', help='Dataset file')
    parser.add_argument('--pred_file', help='Prediction File')
    args = parser.parse_args()
    dataset = read_jsonlines(args.data_file)
    with open(args.pred_file) as prediction_file:
        predictions = json.load(prediction_file)

    f1_total, em_total = 0.0, 0.0
    lang_count = 0
    langs = ["ar", "bn", "fi", "ja", "ko", "ru", "te"]
    for lang in langs:
        print("Evaluating F1, EM scores for {}".format(lang))
        lang_result = evaluate(dataset, predictions, True, lang)
        if lang_result is False:
            continue
        print("F1: {}, EM:{}".format(lang_result["f1"], lang_result["exact_match"]))
        lang_count += 1
        f1_total += lang_result["f1"]
        em_total += lang_result["exact_match"]

    print("Avg scores:")
    print("F1: {0}, EM: {1}".format(f1_total /lang_count, em_total / lang_count))
