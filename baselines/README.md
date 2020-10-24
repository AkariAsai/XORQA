# Baselines for XOR QA

This repository contains the information about the baselines used in the original XOR QA paper. 

## List of baselines
### Retriever 
In our experiment, we have tried three different models (term-based, term-based model followed by neural paragraph ranker, end-to-end neural retriever). The codes for each baseline is available below:

- BM25: BWe use ElasticSearch's python client to retrieve documents in English or in target languages. code is available [here](https://github.com/AkariAsai/XORQA/baselines/bm25/README.md).
- [Dense Passage Retriever](https://github.com/facebookresearch/DPR) ([Karpukhin et al., 2020](https://arxiv.org/abs/2004.04906)): 
- [Path Retriever](https://github.com/AkariAsai/learning_to_retrieve_reasoning_paths) ([Asai et al., 2020](https://arxiv.org/abs/1911.10470))


### Machine Translation for query and answer
We have trained with fairseq on OPUS corpus, as well as HuggingFace Models from Helsinki NLP. The source code is available at [XOR_QA_MTPipeline](https://github.com/jungokasai/XOR_QA_MTPipeline) 
