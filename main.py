import pickle
from preprocessing import preprocess_train
from optimization import get_optimal_vector
from inference import tag_all_test
from sklearn.metrics import accuracy_score

def main():
    threshold = 1
    lam = 1

    train_path = "data/train3.wtag"
    test_path = "data/test2.wtag"

    weights_path = 'weights.pkl'
    predictions_path = 'predictions.wtag'

    statistics, feature2id = preprocess_train(train_path, threshold)
    get_optimal_vector(statistics=statistics, feature2id=feature2id, weights_path=weights_path, lam=lam)

    with open(weights_path, 'rb') as f:
        optimal_params, feature2id = pickle.load(f)
    pre_trained_weights = optimal_params[0]

    print(pre_trained_weights)
    pred,true_pred,words = tag_all_test(test_path, pre_trained_weights, feature2id, predictions_path) # raz added
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

    for (true, pred), word in mistakes_counts.items():
        print(" ,True label:", true, "Predicted label:", pred, " Words", word," Number of mistakes:",len(word))
    print('here')

if __name__ == '__main__':
    main()
