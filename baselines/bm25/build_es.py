from elasticsearch import Elasticsearch
import argparse
import os
from utils import get_analyzer
from doc_db import DocDB
import re
import json
from tqdm import tqdm

def build_index(index_prefix, db_path, lcode, es_index_settings, port=9200):
    db = DocDB(db_path)

    # initialize the elastic search
    config = {'host': 'localhost', 'port': port}
    es = Elasticsearch([config])
    index_name = "{0}_{1}".format(index_prefix, lcode)
    if es.indices.exists(index=index_name):
        es.indices.delete(index=index_name)
    index_settings = es_index_settings

    es.indices.create(index=index_name, body={"settings": index_settings["settings"]})
    # populate index
    # load DB and index in Elastic Search
    es.ping()
    doc_ids = db.get_doc_ids()
    count = 0
    for doc_id in tqdm(doc_ids):
        sections_paras = db.get_doc_text_section_separations(doc_id)
        for section in sections_paras:
            section_name = section["section_name"]
            parent_section_name = section["parent_section_name"]
            paragraphs = section["paragraphs"]
            title = doc_id.split("_0")[0]
            for para_idx, para in enumerate(paragraphs):
                para_title_id = "title:{0}_parentSection:{1}_sectionName:{2}_sectionIndex:{3}".format(title, parent_section_name, section_name, para_idx)
                rec = {"document_text": para, "document_title": para_title_id}
                try:
                    index_status = es.index(index=index_name, id=count, body=rec)
                    count += 1
                except:
                    print(f'Unable to load document {para_title_id}.')

    n_records = es.count(index=index_name)['count']
    print(f'Successfully loaded {n_records} into {index_name}')
    return es

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
    parser.add_argument('--db_path', type=str, required=True,
                        help='Path to sqlite db holding document texts')
    parser.add_argument('--lcode', type=str, required=True,
                        help='language code')
    parser.add_argument('--config_file_path', type=str, required=True,
                        help='path to the congig file')
    parser.add_argument('--port', type=int, required=True,
                        help='path to the congig file')
    parser.add_argument('--index_prefix', type=str, required=True,
                        help='path to the congig file')

    args = parser.parse_args()
    question_text = "What did Ron Paul majored in college?"
    es = build_index(args.index_prefix, args.db_path, args.lcode, json.load(open(args.config_file_path)), port=args.port)
    res = search_es(es_obj=es, index_name="{0}_{1}".format(args.index_prefix, args.lcode), question_text=question_text, n_results=10)
    print(res)

if __name__ == '__main__':
    main()