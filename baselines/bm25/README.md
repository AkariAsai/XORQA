# BM25 based retriever

This director contains the codes for BM2 based retriever for monolingual document retrieval. We use ElasticSearch (ES) Python client as ES supports diverse set of languages, and 6 out of 7 target languages of TyDi-XOR QA are covered by Elastic Search.

## Elastic Search Insolation
To run ElasticSearch in your local environment, you need to install ElasticSearch first. We install ES by running the scripts provided by [CLIReval](https://github.com/ssun32/CLIReval) library (Sun et al., ACL demo 2020). 

```
git clone https://github.com/ssun32/CLIReval.git
cd CLIReval
pip install -r requirements.txt
bash scripts/install_external_tools.sh
```

Whenever you run ES in your local environment, you need to start an ES instance. 

```
bash scripts/server.sh [start|stop]
```

## Index documents and search
1. Create db from preprocessed Wikipedia data (i.e., extract text data by running [wikiextractor](https://github.com/attardi/wikiextractor)) by running the command below.

```
python build_db.py /path/to/your/preprocessed/wiki/data/dir /path/to/output/filename.db
```


2. Index documents
After downloading and preprocessing Wikipedia dumps, please run the command below. The `lcode` denotes [the ISO 639-1 code code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) of the target language. 


| languages        | lcode           |
| ------------- |:-------------:| 
| Arabic    | ar | 
| Bengali    | bn | 
| Finnish    | fi | 
| Japanese    | ja | 
| Korean    | ko | 
| Russian    | ru | 

```
python build_es_simple.py --db_path /path/to/your/db --lcode [language_code] --config_file_path /path/to/config --port 9200
```

e.g., to build an index for Bengali using the `bn_wikipedia_20190201.db`, run the command below.
```
python build_es_simple.py --db_path bn_wikipedia_20190201.db --lcode bn --config_file_path es_configs/bn_config.json --port 9200
```

**Note**: We follow the basic configurations for each language analyzer & tokenizer, which may not be fully optimized. 

The current configurations are [es_configs](https://github.com/AkariAsai/XORQA/baselines/bm25/es_configs/). We follow documentations of language analyzers can be seen [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis-lang-analyzer.html).

For Japanese and Korean, we use [Kuromoji](https://www.elastic.co/guide/en/elasticsearch/plugins/7.9/analysis-kuromoji.html) and [Nori](https://www.elastic.co/guide/en/elasticsearch/plugins/7.9/analysis-nori.html), respectively. 


3. Search documents based on BM25 scores

To search documents for our tydi-xor data (e.g., `xor_dev_retrieve_eng_span.jsonl`)using ES, you can run the command below.
```
python es_search_multi.py --index_name_prefix wikipedia_search_test_ \
--input_data_file_name /path/to/input/file/name \
--output_fp /path/to/output --port 9200
```