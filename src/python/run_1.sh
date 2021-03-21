# python main.py --gpu 2 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed4b
# python main.py --gpu 2 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed4b_3x3
# python main.py --gpu 2 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed4b_5x5
# python main.py --gpu 2 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed4c
# python main.py --gpu 2 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed4c_3x3
# python main.py --gpu 2 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed4c_5x5

# python main.py --gpu 2 --lsh_top_imgs T --save_top_imgs T --blk mixed4b
# python main.py --gpu 2 --lsh_top_imgs T --save_top_imgs T --blk mixed4b_3x3
# python main.py --gpu 2 --lsh_top_imgs T --save_top_imgs T --blk mixed4b_5x5
# python main.py --gpu 2 --lsh_top_imgs T --save_top_imgs T --blk mixed4c
# python main.py --gpu 2 --lsh_top_imgs T --save_top_imgs T --blk mixed4c_3x3
# python main.py --gpu 2 --lsh_top_imgs T --save_top_imgs T --blk mixed4c_5x5

# python main.py --compute_hash_value_neuron T --gpu 2 --blk mixed4b --batch_size 500
# python main.py --compute_hash_value_neuron T --gpu 2 --blk mixed4b_3x3 --batch_size 500
# python main.py --compute_hash_value_neuron T --gpu 2 --blk mixed4b_5x5 --batch_size 500
# python main.py --compute_hash_value_neuron T --gpu 2 --blk mixed4c --batch_size 500
# python main.py --compute_hash_value_neuron T --gpu 2 --blk mixed4c_3x3 --batch_size 500
# python main.py --compute_hash_value_neuron T --gpu 2 --blk mixed4c_5x5 --batch_size 500

# python main.py --gen_bucket T --gpu 2 --blk mixed4b --batch_size 500
# python main.py --gen_bucket T --gpu 2 --blk mixed4b_3x3 --batch_size 500
# python main.py --gen_bucket T --gpu 2 --blk mixed4b_5x5 --batch_size 500
# python main.py --gen_bucket T --gpu 2 --blk mixed4c --batch_size 500
# python main.py --gen_bucket T --gpu 2 --blk mixed4c_3x3 --batch_size 500
# python main.py --gen_bucket T --gpu 2 --blk mixed4c_5x5 --batch_size 500

python main.py --gpu 2 --gen_emb T --reduce_emb T --emb_version 0
python main.py --gpu 2 --gen_emb T --reduce_emb T --emb_version 1
python main.py --gpu 2 --gen_emb T --reduce_emb T --emb_version 2
python main.py --gpu 2 --gen_emb T --reduce_emb T --emb_version 3
python main.py --gpu 2 --gen_emb T --reduce_emb T --emb_version 4
python main.py --gpu 2 --gen_emb T --reduce_emb T --emb_version 5

