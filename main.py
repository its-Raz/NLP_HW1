import pickle
from preprocessing import preprocess_train
from optimization import get_optimal_vector
from inference import tag_all_test
from sklearn.metrics import accuracy_score

import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
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
        test_path = "data/comp2.words"
        weights_path = 'weights.pkl'
        predictions_path = 'comp_m2_206897969_315507780.wtag'

    statistics, feature2id = preprocess_train(train_path, threshold)
    # the time before optimization
    pretime = time.time()
    get_optimal_vector(statistics=statistics, feature2id=feature2id,
                       weights_path=weights_path, lam=lam)
    # time after
    print(f"time of optimization is: {time.time() - pretime}")

    # create_tagged_files(test_path, weights_path, predictions_path)

    with open(weights_path, 'rb') as f:
        optimal_params, feature2id = pickle.load(f)
    pre_trained_weights = optimal_params[0]

    print(pre_trained_weights)
    pred, true_pred, words = tag_all_test(
        test_path, pre_trained_weights, feature2id, predictions_path)  # raz added
    print('after tag')

    # CONFUSION MATRIX
    tags = list(set(true_pred))
    cm = confusion_matrix(true_pred, pred, labels=tags)
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=tags)

    disp.plot()

    plt.figure(figsize=(20, 12))
    disp.plot(ax=plt.gca(), xticks_rotation=90)
    plt.show()

    accuracy = accuracy_score(pred, true_pred)
    print("Accuracy:", accuracy)
    mistakes_counts = {}
    mistakes_counts2 = {}

    print('here')

    # Iterate through the lists
    for word, true, predict in zip(words, true_pred, pred):
        # If the prediction is incorrect, update the mistake count for this (word, true, pred) tuple
        if true != predict:
            key = (true, predict)
            key2 = true
            if key in mistakes_counts:

                mistakes_counts[key].append(word)
            else:
                mistakes_counts[key] = []
                mistakes_counts[key].append(word)
            if key2 in mistakes_counts2:
                mistakes_counts2[key2] = mistakes_counts2[key2] + 1
            else:
                mistakes_counts2[key2] = 1
    top_10_mistakes = dict(sorted(mistakes_counts2.items(), key=lambda item: item[1], reverse=True))
    top_10_keys = list(top_10_mistakes.keys())[:10]
    top_10_values = list(top_10_mistakes.values())[:10]

    # Print the top 10 keys and values
    print(f"Top 10 Mistakes tags: {top_10_keys}")
    print(f"Top 10 Number of mistakes: {top_10_values}")
    sorted_dict = dict(
        sorted(mistakes_counts.items(), key=lambda item: item[0]))
    for (true, pred), word in sorted_dict.items():
        print(" ,True label:", true, "Predicted label:", pred,
              " Words", word, " Number of mistakes:", len(word))
    print('here')


if __name__ == '__main__':
    main()
