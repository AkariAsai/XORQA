from elasticsearch import Elasticsearch
import argparse
import os
from doc_db import DocDB
import re
from tqdm import tqdm
import jsonlines
import json

def read_jsonlines(file_name):
    lines = []
    print("loading examples from {0}".format(file_name))
    with jsonlines.open(file_name) as reader:
        for obj in reader:
            lines.append(obj)
    return lines

def search_es(es_obj, index_name, question_text, n_results=5):
    # construct query
    query = {
            'query': {
                'match': {
                    'document_text': question_text
                    }
                }
            }
    
    res = es_obj.search(index=index_name, body=query, size=n_results)
    
    return res

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--index_name_prefix', type=str, required=True,
                        help='Path to index')
    parser.add_argument('--input_data_file_name', type=str, required=True,
                        help='Path to index')
    parser.add_argument('--port', type=int, required=True,
                        help='Path to index')
    parser.add_argument('--output_fp', type=str)

    args = parser.parse_args()
    input_data = read_jsonlines(args.input_data_file_name)
    config = {'host': 'localhost', 'port': args.port}
    es = Elasticsearch([config])
    result = {}
    # telugu is not supported.
    langs = ["ar", "fi", "ja", "ko", "ru", "bn"]
    squad_style_dev_data = {'data': [], 'version': 'v2.0'}
    for item in tqdm(input_data):
        question = item["question"]
        lang =  item["lang"]
        if lang not in langs:
            continue
        index_name = args.index_name_prefix + "_" + lang
        res = search_es(es_obj=es, index_name=index_name, question_text=question, n_results=20)
        result[item["id"]] = {"hits": res["hits"]["hits"], "answers": item["answers"], "has_answer":False, "question": question}
        for hit in res["hits"]["hits"]:
            answers = [{"text": answer, "answer_start": hit["_source"]["document_text"].find(answer)} for answer in item["answers"]]
            squad_example = {'context': hit["_source"]["document_text"],
                            'qas': [{'question': question, 'is_impossible': False,
                                    'answers': answers,
                                        'id': item["id"]}]}
            squad_style_dev_data["data"].append(
                                {"title": hit["_source"]["document_title"], 'paragraphs': [squad_example]})

    # evaluate top 20 accuracy
    for q_id in result:
        hits = result[q_id]["hits"]
        answers = result[q_id]["answers"]
        for answer in answers:
            for hit in hits:
                if answer in hit["_source"]["document_text"]:
                    result[q_id]["has_answer"] = True
                    break

    with open(args.output_fp, 'w') as outfile:
        json.dump(result, outfile)
    with open("_squad_format" + args.output_fp, 'w') as outfile:
        json.dump(squad_style_dev_data, outfile)
    

    # calc top 20 recall 
    top_20_accuracy = len([q_id for q_id, item in result.items() if item["has_answer"] is True]) / len(result)
    # per language performance 
    langs = ["ar", "bn", "fi", "ja", "ko", "ru", "te"]
    per_lang_performance = {}
    for lang in langs:
        question_count = len([q_id for q_id, item in result.items() if lang in q_id])
        top_20_accuracy_lang = len([q_id for q_id, item in result.items() if item["has_answer"] is True and lang in q_id]) / question_count
        per_lang_performance[lang] = top_20_accuracy_lang
    print(top_20_accuracy)
    print(per_lang_performance)

if __name__ == '__main__':
    main()