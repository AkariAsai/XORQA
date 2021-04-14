#!/bin/bash
mkdir -p models
cd models
# download models
mkdir -p checkpoints
cd checkpoints
mkdir checkpoints_multilingual
cd checkpoints_multilingual
wget https://nlp.cs.washington.edu/xorqa/XORQA_site/data/models/checkpoints_multilingual_20210412/dpr_biencoder_best.cpt
wget https://nlp.cs.washington.edu/xorqa/XORQA_site/data/models/checkpoints_multilingual_20210412/dpr_multilingual_reader_best.cpt
# download embeddings
mkdir embeddings_multi
cd embeddings_multi
for i in 0 1 2 3 4 5 6 7;
do 
  wget https://nlp.cs.washington.edu/xorqa/XORQA_site/data/models/embeddings_multilingual_fine_tuned_final/wikipedia_split/wiki_emb_$i 
done
cd ..

