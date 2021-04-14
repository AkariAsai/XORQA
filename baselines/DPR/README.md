
## DPR baselines
[Dense Passage Retriever (DPR; Karpukhin et al., 2020)](https://arxiv.org/abs/2004.04906) encodes documents into fixed-sized dense representations and retrieves relevant documents based on approximate nearest neighbor search between query representations, without using sparse vector representations (e.g., TF-IDF).    

This repository includes the code (forked from the original implementation with some minor modifications on data processing) and scripts to run the evaluations.

### Requirements
We tested the code with [`transformers==3.0.2`](https://github.com/huggingface/transformers/releases/tag/v3.0.2) and [PyTorch 1.6.0/1.7.1](https://pytorch.org/). 

### Download checkpoints and embeddings
You can download the model checkpoints and generated embeddings for translate-test and multilingual baselines by running the scripts below. 

- Translate-test baseline
```sh
bash download_trans_test_models.sh
```

- Multilingual baseline
```sh
bash download_multilingual_models.sh
```

Also, please download the preprocessed wikipedia file (a `tsv` file, where each line includes a 100-token length document chunk of English Wikipedia).

```
wget https://nlp.cs.washington.edu/xorqa/XORQA_site/data/models/enwiki_20190201_w100.tsv
```

### Evaluations
This section explains how to reproduce the results of our baseline models. 

If you just want to take a look at the actual prediction results of our baselines, you can download the prediction results on the dev set [here (google drive)](https://drive.google.com/drive/folders/14WI97TAfQ23CjtKSZ-LU8tQTtCFCfal6?usp=sharing).

#### 0. Download the input data file (For Translate-test baseline)
To reproduce the results of the translate-test baselines without running MT systems by yourself, you can use our translation results obtained by Google Translate or our own NMT systems from [this link](https://drive.google.com/file/d/1KyCC_8PjOjvQRjdQFvc3_ufirT7s7LaB/view?usp=sharing).

The files follow the original XOR QA data file, and each `question` is translated by a machine translation system from the original language to English.


#### 1. Retrieve Top Wikipedia paragraphs (XOR-retrieve)
```
python dense_retriever.py \
    --model_file {path to checkpoint file} \
    --ctx_file {path to psgs_w100.tsv file} --n-docs 100 \
    --qa_file {path to test/dev qas file} \
    --encoded_ctx_file "{glob expression for generated files}" \
    --out_file {specify the name of the retrieval output file}  \
    --validation_workers 4 --batch_size 64 
```
The results will be output to the path specified by `out_file`. You can run the xor-retrieve task evaluations using this output file.

e.g., 
If you want to run the evaluations on the translate-test baseline (our NMT) on XOR QA retrieve task, please run the code below: 
```
python dense_retriever.py \
    --model_file models/checkpoints/checkpoints_trans_eng/dpr_biencoder_best.cpt \
    --ctx_file psgs_w100.tsv --n-docs 50 \
    --qa_file xor_retrieve_eng_span_dev_our_nmt_q.jsonl \
    --encoded_ctx_file "models/checkpoints/embeddings_en/wiki_emb_*" \
    --out_file retriever_results_trans_en_dev_our_nmt.json \
    --validation_workers 4 --batch_size 64 
```
The output will be stores into `out_file` (DPR retrieval result format) and `{out_file}_xor_retrieve_results.json` (XOR retrieve evaluation format). You can directly feed the latter file to the evaluation script.

```
python eval_xor_retrieve_final.py --data_file xor_dev_retrieve_eng_span.jsonl --pred_file {out_file}_xor_retrieve_results.json 
```

#### 2. Run the reader model (XOR Eng Span)
After running the retrieval model, you can run the reader component to get the final results. 

```
python train_reader.py \
    --dev_file /path/to/retriever/prediction/file.json \
    --prediction_results_file /path/to/output/prediction/file.json \
    --eval_top_docs 50 --dev_file /path/to/out_file \
    --model_file models/checkpoints/checkpoints_trans_eng/dpr_reader_best.cpt \
    --dev_batch_size 8 --passages_per_question_predict 100 --sequence_length 350
```

The final results in the XOR-EngSpan evaluation format will be saved into `{prediction_results_file}_predictions.json`. 

You can get the final evaluation score by running the command below:
```
python eval_xor_engspan_final.py --data_file xor_dev_retrieve_eng_span.jsonl --pred_file {prediction_results_file}_predictions.json
```

e.g., Run translate-test baseline (translated by our NMT)
```
python train_reader.py \
    --prediction_results_file reader_results_trans_en_dev_our_nmt.json \ # final results will be stored into reader_results_trans_en_dev_our_nmt_predictions.json
    --eval_top_docs 50 \
    --dev_file retriever_results_trans_en_dev_our_nmt.json \
    --model_file models/checkpoints/models_translate_test/dpr_reader_best.cpt \
    --dev_batch_size 8 --passages_per_question_predict 100 --sequence_length 350
```

### Training
For the details of the model training, please refer the instructions in [the original DPR repository](https://github.com/facebookresearch/DPR).

#### Training data
You can download the training data [here](https://drive.google.com/drive/folders/1JtHDWS6kW-pkzHZZ8P6F723pAe9CT1Tc?usp=sharing). 

The `positive_ctxs` are the gold paragraphs we annotated, and we split the gold paragraphs into 100 word length as in the original DPR. When the gold paragraph can be splitted into more than one chunks, we map the short answer span locations and choose the chunk where the original short answer is extracted as the `positive_ctxs`. The `hard_negative_ctxs` are selected by randomly sampling one of the top 5 paragraphs selected by our BERT based paragraph ranker, without answer strings. 

During training, we use one `positive_ctxs` and one `hard_negative_ctxs` in addition to the in-batch negative context following the original DPR training. 

For the definition of the `hard_negative_ctxs`, `negative_ctxs` and `positive_ctxs` of DPR, please see [the detailed discussions](https://github.com/facebookresearch/DPR/issues/42) in the original DPR repository. 

#### Training
To train DPR retrievers, (a) we first fine-tune the model on NQ train data which can be downloaded by following instructions of the original DPR repository. Then, (b) we fine-tune the model using our data, setting the `--model_file` option to the model file path from the initial step (a) (i.e., dpr_multilingual_checkpoint_nq/best.cp in the command below). 


**Note:** please set the `--restart` option during (b). As reported in the original DPR repository, when you start fine-tuning from `--model_file`, the learning rate is stick to 0.0, and I made small code changes to avoid this. 

e.g., 
````
python -m torch.distributed.launch --nproc_per_node=8 train_dense_encoder.py \
--max_grad_norm 2.0 --encoder_model_type hf_bert --pretrained_model_cfg bert-base-multilingual-uncased \
--model_file "dpr_multilingual_checkpoint_nq/best.cp" --seed 12345 \
--sequence_length 256 --warmup_steps 1237 --batch_size 12 --do_lower_case \
--train_file "xorqa_dpr_data_query=L_hard_negative=1/dpr_train_data.json" \
--dev_file  "xorqa_dpr_data_query=L_hard_negative=1/dpr_dev_data.json" \
-output_dir multilingual_dpr --learning_rate 2e-05 --num_train_epochs 40 \
--dev_batch_size 12 --val_av_rank_start_epoch 10 --restart
````
