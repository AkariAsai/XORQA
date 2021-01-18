#!/bin/bash
mkdir -p models
cd models
# download models
mkdir -p checkpoints
cd checkpoints
mkdir checkpoints_trans_eng
cd checkpoints_trans_eng
wget https://nlp.cs.washington.edu/xorqa/XORQA_site/data/models/checkpoints_trans_eng/dpr_biencoder_best.cpt
wget https://nlp.cs.washington.edu/xorqa/XORQA_site/data/models/checkpoints_trans_eng/dpr_reader_best.cpt
# download embeddings
cd ..
mkdir embeddings_en
cd embeddings_en
for i in 0 1 2 3 5;
do 
  wget https://nlp.cs.washington.edu/xorqa/XORQA_site/data/models/embeddings_en/wiki_emb_$i 
done
cd ..
