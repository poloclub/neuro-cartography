# python main.py --gpu 5 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed5a
# python main.py --gpu 5 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed5a_3x3
# python main.py --gpu 5 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed5a_5x5
# python main.py --gpu 5 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed5b
# python main.py --gpu 5 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed5b_3x3
# python main.py --gpu 5 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --blk mixed5b_5x5

# python main.py --gpu 5 --lsh_top_imgs T --save_top_imgs T --blk mixed5a
# python main.py --gpu 5 --lsh_top_imgs T --save_top_imgs T --blk mixed5a_3x3
# python main.py --gpu 5 --lsh_top_imgs T --save_top_imgs T --blk mixed5a_5x5
# python main.py --gpu 5 --lsh_top_imgs T --save_top_imgs T --blk mixed5b
# python main.py --gpu 5 --lsh_top_imgs T --save_top_imgs T --blk mixed5b_3x3
# python main.py --gpu 5 --lsh_top_imgs T --save_top_imgs T --blk mixed5b_5x5

python main.py --compute_hash_value_neuron T --gpu 4 --blk mixed4e --batch_size 400
python main.py --compute_hash_value_neuron T --gpu 4 --blk mixed4e_3x3 --batch_size 400
python main.py --compute_hash_value_neuron T --gpu 4 --blk mixed4e_5x5 --batch_size 400
python main.py --compute_hash_value_neuron T --gpu 4 --blk mixed5a --batch_size 400
python main.py --compute_hash_value_neuron T --gpu 4 --blk mixed5a_3x3 --batch_size 400
python main.py --compute_hash_value_neuron T --gpu 4 --blk mixed5a_5x5 --batch_size 400
# python main.py --compute_hash_value_neuron T --gpu 5 --blk mixed5b
# python main.py --compute_hash_value_neuron T --gpu 5 --blk mixed5b_3x3
# python main.py --compute_hash_value_neuron T --gpu 5 --blk mixed5b_5x5


# python main.py --gen_bucket T --gpu 5 --blk mixed5a
# python main.py --gen_bucket T --gpu 5 --blk mixed5a_3x3
# python main.py --gen_bucket T --gpu 5 --blk mixed5a_5x5
# python main.py --gen_bucket T --gpu 5 --blk mixed5b
# python main.py --gen_bucket T --gpu 5 --blk mixed5b_3x3
# python main.py --gen_bucket T --gpu 5 --blk mixed5b_5x5
