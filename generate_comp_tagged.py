import pickle
from inference import tag_all_test

"""
This file will generate the competition files for model 1 and model 2.
Take into account that this file will generate both of the files on the same weights.
This is unless you call the function below from main.py file.
Otherwise look at the end of this file where we generate the files and change the weights paths accordingly
"""

if __name__ == '__main__':
    # model 1
    test_path = "data/comp1.words"
    weights_path = 'weights_1.pkl'
    predictions_path = "comp_m1_206897969_315507780.wtag"
    with open(weights_path, 'rb') as f:
        optimal_params, feature2id_1 = pickle.load(f)
    pre_trained_weights_1 = optimal_params[0]
    tag_all_test(
        test_path, pre_trained_weights_1, feature2id_1, predictions_path)

    # model 2
    test_path = "data/comp2.words"
    weights_path = 'weights_2.pkl'
    predictions_path = "comp_m2_206897969_315507780.wtag"
    with open(weights_path, 'rb') as f:
        optimal_params, feature2id_2 = pickle.load(f)
    pre_trained_weights_2 = optimal_params[0]
    tag_all_test(
        test_path, pre_trained_weights_2, feature2id_1, predictions_path)
