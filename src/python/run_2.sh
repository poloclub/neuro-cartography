# python main.py --gpu 2 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --num_top_imgs 200 --blk mixed4d 
# python main.py --gpu 2 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --num_top_imgs 200 --blk mixed4d_3x3
# python main.py --gpu 2 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --num_top_imgs 200 --blk mixed4d_5x5
# python main.py --gpu 2 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --num_top_imgs 200 --blk mixed4e
# python main.py --gpu 2 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --num_top_imgs 200 --blk mixed4e_3x3
# python main.py --gpu 2 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --num_top_imgs 200 --blk mixed4e_5x5
# python main.py --gpu 2 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --num_top_imgs 200 --blk mixed5a
# python main.py --gpu 2 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --num_top_imgs 200 --blk mixed5a_3x3
# python main.py --gpu 2 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --num_top_imgs 200 --blk mixed5a_5x5
# python main.py --gpu 2 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --num_top_imgs 200 --blk mixed5b
# python main.py --gpu 2 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --num_top_imgs 200 --blk mixed5b_3x3
# python main.py --gpu 2 --find_top_imgs T --lsh_top_imgs T --save_top_imgs T --num_top_imgs 200 --blk mixed5b_5x5

# python main.py --gpu 4 --lsh_top_imgs T --save_top_imgs T --blk mixed4d
# python main.py --gpu 4 --lsh_top_imgs T --save_top_imgs T --blk mixed4d_3x3
# python main.py --gpu 4 --lsh_top_imgs T --save_top_imgs T --blk mixed4d_5x5
# python main.py --gpu 4 --lsh_top_imgs T --save_top_imgs T --blk mixed4e
# python main.py --gpu 4 --lsh_top_imgs T --save_top_imgs T --blk mixed4e_3x3
# python main.py --gpu 4 --lsh_top_imgs T --save_top_imgs T --blk mixed4e_5x5

python main.py --compute_hash_value_neuron T --gpu 3 --blk mixed4e --batch_size 500
python main.py --compute_hash_value_neuron T --gpu 3 --blk mixed4e_3x3 --batch_size 500
python main.py --compute_hash_value_neuron T --gpu 3 --blk mixed4e_5x5 --batch_size 500
# python main.py --compute_hash_value_neuron T --gpu 2 --blk mixed4c --batch_size 500
# python main.py --compute_hash_value_neuron T --gpu 2 --blk mixed4c_3x3 --batch_size 500
# python main.py --compute_hash_value_neuron T --gpu 2 --blk mixed4c_5x5 --batch_size 500
# python main.py --compute_hash_value_neuron T --gpu 4 --blk mixed4d 
# python main.py --compute_hash_value_neuron T --gpu 4 --blk mixed4d_3x3 
# python main.py --compute_hash_value_neuron T --gpu 4 --blk mixed4d_5x5
# python main.py --compute_hash_value_neuron T --gpu 4 --blk mixed4e 
# python main.py --compute_hash_value_neuron T --gpu 4 --blk mixed4e_3x3 
# python main.py --compute_hash_value_neuron T --gpu 4 --blk mixed4e_5x5


# python main.py --gen_bucket T --gpu 4 --blk mixed4d 
# python main.py --gen_bucket T --gpu 4 --blk mixed4d_3x3 
# python main.py --gen_bucket T --gpu 4 --blk mixed4d_5x5
# python main.py --gen_bucket T --gpu 4 --blk mixed4e 
# python main.py --gen_bucket T --gpu 4 --blk mixed4e_3x3 
# python main.py --gen_bucket T --gpu 4 --blk mixed4e_5x5
