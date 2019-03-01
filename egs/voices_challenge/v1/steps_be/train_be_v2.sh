#!/bin/bash
# Copyright 2018 Johns Hopkins University (Jesus Villalba)  
# Apache 2.0.
#
set -e 

cmd=run.pl
lda_dim=150
plda_type=splda
y_dim=100
z_dim=150
w_mu=1
w_b=0
w_w=0
adapt_y_dim=90

if [ -f path.sh ]; then . ./path.sh; fi
. parse_options.sh || exit 1;

vector_file=$1
data_dir=$2
adapt_vector_file1=$3
adapt_data_dir1=$4
output_dir=$5

mkdir -p $output_dir/log

for f in utt2spk; do
  if [ ! -f $data_dir/$f ]; then
    echo "$0: no such file $data_dir/$f"
    exit 1;
  fi
done

train_list=$output_dir/train_utt2spk
adapt_list1=$output_dir/adapt1_utt2spk

awk -v fv=$vector_file 'BEGIN{
while(getline < fv)
{
   files[$1]=1
}
}
{ if ($1 in files) {print $1,$2}}' $data_dir/utt2spk > $train_list

awk -v fv=$adapt_vector_file1 'BEGIN{
while(getline < fv)
{
   files[$1]=1
}
}
{ if ($1 in files) {print $1,$2}}' $adapt_data_dir1/utt2spk > $adapt_list1


# sort --random-source=$adapt_vector_file1 -R $adapt_data_dir1/utt2spk |
# awk -v fv=$adapt_vector_file1 'BEGIN{
# while(getline < fv)
# {
#    files[$1]=1
# }
# }
# { 
#   if ($1 in files) { 
#      seg=$1;
#      sub(/.*-VOiCES-/,"",seg);
#      split(seg,f,"-");
#      seg_name=f[4]"-"f[5];
#      if(!(seg_name in seen)){
#          seen[seg_name]=1;
#          print $1,$2;
#      }
#   }
# }'  | sort -k1,1 > $adapt_list1



$cmd $output_dir/log/train_be.log \
     python steps_be/train-be-v2.py \
     --iv-file scp:$vector_file \
     --train-list $train_list \
     --adapt-iv-file scp:$adapt_vector_file1 \
     --adapt-list $adapt_list1 \
     --lda-dim $lda_dim \
     --plda-type $plda_type \
     --y-dim $y_dim --z-dim $z_dim \
     --output-path $output_dir \
     --w-mu $w_mu --w-w $w_w 

