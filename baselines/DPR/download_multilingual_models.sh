#!/bin/bash
mkdir -p models
cd models
# download models
mkdir -p checkpoints
cd checkpoints
mkdir checkpoints_multilingual
cd checkpoints_multilingual
wget https://nlp.cs.washington.edu/xorqa/XORQA_site/data/models/checkpoints_multilingual/dpr_biencoder_best.cpt
wget https://nlp.cs.washington.edu/xorqa/XORQA_site/data/models/checkpoints_multilingual/dpr_reader_best.cpt
# download embeddings
mkdir embeddings_multi
cd embeddings_multi
for i in 1 2 3 4 5;
do 
  wget https://nlp.cs.washington.edu/xorqa/XORQA_site/data/models/embeddings_multi/wiki_emb_$i 
done
cd ..

