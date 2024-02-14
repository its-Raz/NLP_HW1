import pickle
from inference import tag_all_test

"""
This file will generate the competition files for model 1 and model 2.
Take into account that this file will generate both of the files on the same weights.
This is unless you call the function below from main.py file.
Otherwise look at the end of this file where we generate the files and change the weights paths accordingly
"""


def create_tagged_files(test_path, weights_path, predictions_path):
    """
    Tags the test_path, with weights from weights_path and 
    feature indices in feature2id which is create when training on the train path
    and returns output to predictions_path
    """
    with open(weights_path, 'rb') as f:
        optimal_params, feature2id = pickle.load(f)
    for feature in feature2id.feature_to_idx['f100']:
        if feature == ('The', 'DT'):
            print("yes")
    pre_trained_weights = optimal_params[0]

    print(pre_trained_weights)
    tag_all_test(test_path, pre_trained_weights, feature2id, predictions_path)


if __name__ == '__main__':
    # model 1
    test_path = "data/comp1.words"
    weights_path = 'weights.pkl'
    predictions_path = "comp_m1_206897969_123.wtag"
    create_tagged_files(test_path, weights_path, predictions_path)

    # model 2
    test_path = "data/comp2.words"
    weights_path = 'weights.pkl'
    predictions_path = "comp_m2_206897969_123.wtag"
    create_tagged_files(test_path, weights_path, predictions_path)
