import pickle
from preprocessing import preprocess_train
from optimization import get_optimal_vector
from inference import tag_all_test
from sklearn.metrics import accuracy_score
from generate_comp_tagged import create_tagged_files

import time


def main():
    threshold = 0.10
    lam = 0.38

    train_path = "data/train1.wtag"
    test_path = "data/comp1.words"

    weights_path = 'weights.pkl'
    predictions_path = 'comp_m1_206897969_123.wtag'

    statistics, feature2id = preprocess_train(train_path, threshold)
    # the time before optimization
    pretime = time.time()

    get_optimal_vector(statistics=statistics, feature2id=feature2id,
                       weights_path=weights_path, lam=lam)
    # time after
    print(f"time of optimization is: {time.time() - pretime}")

    create_tagged_files(test_path, weights_path, predictions_path)

    # MODEL 2
    train_path = "data/train2.wtag"
    test_path = "data/comp2.words"

    threshold = 0.05
    lam = 0.38
    weights_path = 'weights.pkl'
    predictions_path = 'comp_m2_206897969_123.wtag'

    statistics, feature2id = preprocess_train(train_path, threshold)
    # the time before optimization
    pretime = time.time()

    get_optimal_vector(statistics=statistics, feature2id=feature2id,
                       weights_path=weights_path, lam=lam)
    # time after
    print(f"time of optimization is: {time.time() - pretime}")

    create_tagged_files(test_path, weights_path, predictions_path)

    with open(weights_path, 'rb') as f:
        optimal_params, feature2id = pickle.load(f)
    pre_trained_weights = optimal_params[0]

    print(pre_trained_weights)
    pred, true_pred, words = tag_all_test(
        test_path, pre_trained_weights, feature2id, predictions_path)  # raz added
    print('after tag')

    accuracy = accuracy_score(pred, true_pred)
    print("Accuracy:", accuracy)
    mistakes_counts = {}

    # Iterate through the lists
    for word, true, predict in zip(words, true_pred, pred):
        # If the prediction is incorrect, update the mistake count for this (word, true, pred) tuple
        if true != predict:
            key = (true, predict)
            if key in mistakes_counts:

                mistakes_counts[key].append(word)
            else:
                mistakes_counts[key] = []
                mistakes_counts[key].append(word)
    sorted_dict = dict(
        sorted(mistakes_counts.items(), key=lambda item: item[0]))
    for (true, pred), word in sorted_dict.items():
        print(" ,True label:", true, "Predicted label:", pred,
              " Words", word, " Number of mistakes:", len(word))
    print('here')


if __name__ == '__main__':
    main()
