#!/bin/bash
mkdir -p models
cd models
# download models
mkdir -p checkpoints
cd checkpoints
mkdir checkpoints_multilingual_v2
cd checkpoints_multilingual_v2
wget https://nlp.cs.washington.edu/xorqa/XORQA_site/data/models/checkpoints_multilingual_v2/dpr_biencoder_best.cpt
wget https://nlp.cs.washington.edu/xorqa/XORQA_site/data/models/checkpoints_multilingual_v2/dpr_reader_best.cpt
# download embeddings
mkdir embeddings_multi_v2
cd embeddings_multi_v2
for i in 0 1 2 3 4 5;
do 
  wget https://nlp.cs.washington.edu/xorqa/XORQA_site/data/models/embeddings_multi_v2/wiki_emb_$i 
done
cd ..

