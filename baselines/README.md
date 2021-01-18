# Baselines for XOR QA
This repository contains the information about the baselines used in the original XOR QA paper. 

## Updates
- Update as of 01/2020: Codes for running DPR based baselines are ready.

## List of baselines
### Retriever 
In our experiment, we have tried three different models (term-based, term-based model followed by neural paragraph ranker, end-to-end neural retriever). The codes for each baseline is available below:

- BM25: We use ElasticSearch's python client to retrieve documents in English or in target languages. The code is available [here](bm25).
- [Dense Passage Retriever](https://github.com/facebookresearch/DPR) ([Karpukhin et al., 2020](https://arxiv.org/abs/2004.04906)): The code (some minor modifications of the original DPR implementations) is [here](DPR). 
- [Path Retriever](https://github.com/AkariAsai/learning_to_retrieve_reasoning_paths) ([Asai et al., 2020](https://arxiv.org/abs/1911.10470))


### Machine Translation for query and answer
We have trained with fairseq on OPUS corpus, as well as HuggingFace Models from Helsinki NLP. The source code is available at [XOR_QA_MTPipeline](https://github.com/jungokasai/XOR_QA_MTPipeline). 
