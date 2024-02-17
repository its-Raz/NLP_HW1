import pickle
from preprocessing import preprocess_train
from optimization import get_optimal_vector
from inference import tag_all_test
import time


def main():

    model = 1 # FLAG TO CHANGE BETWEEN MODEL 1 AND 2

    if model == 1:
        threshold = 1
        lam = 0.38
        train_path = "data/train1.wtag"
        test_path = "data/test1.wtag"
        weights_path = 'weights.pkl'
        predictions_path = 'comp_m1_206897969_315507780.wtag'
    else:
        threshold = 1
        lam = 0.38
        train_path = "data/train2.wtag"
        test_path = "data/test1.wtag"
        weights_path = 'weights.pkl'
        predictions_path = 'comp_m2_206897969_315507780.wtag'
    pretime = time.time()
    statistics, feature2id = preprocess_train(train_path, threshold)

    get_optimal_vector(statistics=statistics, feature2id=feature2id, weights_path=weights_path, lam=lam)
    # time after
    print(f"time of optimization is: {time.time() - pretime}")

    with open(weights_path, 'rb') as f:
        optimal_params, feature2id = pickle.load(f)
    pre_trained_weights = optimal_params[0]

    print(pre_trained_weights)
    tag_all_test(test_path, pre_trained_weights, feature2id, predictions_path)

if __name__ == '__main__':
    main()
