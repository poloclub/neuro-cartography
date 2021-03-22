

# python main.py --gpu 1 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed3a
# python main.py --gpu 1 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed3b
# python main.py --gpu 1 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed3b_3x3
# python main.py --gpu 1 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed3b_5x5
# python main.py --gpu 1 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed4a
# python main.py --gpu 1 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed4a_3x3
# python main.py --gpu 1 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed4a_5x5

# python main.py --gpu 1 --lsh_top_imgs T --save_top_imgs T --blk mixed3a
# python main.py --gpu 1 --lsh_top_imgs T --save_top_imgs T --blk mixed3b
# python main.py --gpu 1 --lsh_top_imgs T --save_top_imgs T --blk mixed3b_3x3
# python main.py --gpu 1 --lsh_top_imgs T --save_top_imgs T --blk mixed3b_5x5
# python main.py --gpu 1 --lsh_top_imgs T --save_top_imgs T --blk mixed4a
# python main.py --gpu 1 --lsh_top_imgs T --save_top_imgs T --blk mixed4a_3x3
# python main.py --gpu 1 --lsh_top_imgs T --save_top_imgs T --blk mixed4a_5x5

python main.py --compute_hash_value_neuron T --gpu 1 --blk mixed3a --batch_size 500
python main.py --compute_hash_value_neuron T --gpu 1 --blk mixed3b --batch_size 500
python main.py --compute_hash_value_neuron T --gpu 1 --blk mixed3b_3x3 --batch_size 500
python main.py --compute_hash_value_neuron T --gpu 1 --blk mixed3b_5x5 --batch_size 500
# python main.py --compute_hash_value_neuron T --gpu 1 --blk mixed4a --batch_size 500
# python main.py --compute_hash_value_neuron T --gpu 1 --blk mixed4a_3x3 --batch_size 500
# python main.py --compute_hash_value_neuron T --gpu 1 --blk mixed4a_5x5 --batch_size 500

# python main.py --gen_bucket T --gpu 1 --blk mixed3a --batch_size 500
# python main.py --gen_bucket T --gpu 1 --blk mixed3b --batch_size 500
# python main.py --gen_bucket T --gpu 1 --blk mixed3b_3x3 --batch_size 500
# python main.py --gen_bucket T --gpu 1 --blk mixed3b_5x5 --batch_size 500
# python main.py --gen_bucket T --gpu 1 --blk mixed4a --batch_size 500
# python main.py --gen_bucket T --gpu 1 --blk mixed4a_3x3 --batch_size 500
# python main.py --gen_bucket T --gpu 1 --blk mixed4a_5x5 --batch_size 500
