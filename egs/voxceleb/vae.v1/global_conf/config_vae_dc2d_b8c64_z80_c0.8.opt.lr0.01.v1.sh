# VAE with symmetric deep conv 2D encoder-decoder with 
# 8 residual blocks, 64 base channels , latent_channels=80, compression factor=0.8

nnet_data=voxceleb2cat_train
batch_size_1gpu=32
eff_batch_size=512 # effective batch size
min_chunk=400
max_chunk=400
ipe=1
lr=0.01
dropout=0
latent_dim=80
model_type=vae
narch=dc2d
vae_opt=""
enc_opt="--enc.in-conv-channels 64 --enc.in-kernel-size 5 --enc.in-stride 1 --enc.conv-repeats 2 2 2 2 --enc.conv-channels 64 128 256 512 --enc.conv-kernel-sizes 3 --enc.conv-strides 1 2 2 2"
dec_opt="--dec.in-channels 80 --dec.in-conv-channels 512 --dec.in-kernel-size 3 --dec.in-stride 1 --dec.conv-repeats 2 2 2 2 --dec.conv-channels 512 256 128 64 --dec.conv-kernel-sizes 3 --dec.conv-strides 1 2 2 2"

opt_opt="--optim.opt-type adam --opt.lr $lr --opt.beta1 0.9 --opt.beta2 0.95 --opt.weight-decay 1e-5 --opt.amsgrad"
lrs_opt="--lrsched.lrsch-type exp_lr --lrsched.decay-rate 0.5 --lrsched.decay-steps 16000 --lrsched.hold-steps 16000 --lrsched.min-lr 1e-5 --lrsched.warmup-steps 8000 --lrsched.update-lr-on-opt-step"
nnet_name=${model_type}_${narch}_b8c64_z${latent_dim}_c0.8_do${dropout}_optv1_adam_lr${lr}_b${eff_batch_size}.$nnet_data
nnet_num_epochs=400
num_augs=5
nnet_dir=exp/vae_nnets/$nnet_name
nnet=$nnet_dir/model_ep0400.pth

# xvector network trained with recipe v1.1
xvec_nnet_name=fbank80_stmn_lresnet34_e256_arcs30m0.3_do0_adam_lr0.05_b512_amp.v1
xvec_nnet_dir=../v1.1/exp/xvector_nnets/$xvec_nnet_name
xvec_nnet=$xvec_nnet_dir/model_ep0070.pth
