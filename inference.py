from preprocessing import read_test
from tqdm import tqdm
import numpy as np
import math
from sklearn.metrics import accuracy_score

MIN_VALUE = -99999


def memm_viterbi(sentence, pre_trained_weights, feature2id):
    """
    Write your MEMM Viterbi implementation below
    You can implement Beam Search to improve runtime
    Implement q efficiently (refer to conditional probability definition in MEMM slides)
    """
    print('here')

    beam_threshold = 2
    all_tags = feature2id.feature_statistics.tags

    current_pai = {}
    prev_pai = {}
    bp = {}
    predictions = []
    pp_tags = ['*']  # S(k-2)
    p_tags = ['*']  # S(k-1)
    c_tags = list(all_tags)  # Sk
    p_pairs = get_all_possible_pairs(pp_tags, p_tags)
    for k in range(2, len(sentence) - 1):
        c_pairs = get_all_possible_pairs(p_tags, c_tags)  # pai(k,u,v) u from S(k-1) c_tag=all tags
        q = calculate_q_probability(pre_trained_weights, c_tags, p_pairs, sentence, k, feature2id)
        for pair in c_pairs:
            prev_tag = pair[0]
            curr_tag = pair[1]
            if k == 2:
                current_pai[('*', curr_tag)] = q[('*', '*', curr_tag)]

            else:
                if k == 3:
                    current_pai[(prev_tag, curr_tag)] = prev_pai[('*', prev_tag)] * q[('*', prev_tag, curr_tag)]
                else:
                    tag_max = ('', MIN_VALUE)
                    # q_probabilities[(pair[0],pair[1],curr_tag)]
                    for t in pp_tags:
                        if (t,prev_tag) in p_pairs:
                            value = prev_pai[(t, prev_tag)] * q[(t, prev_tag, curr_tag)]
                            if value > tag_max[1]:
                                tag_max = (t, value)
                        else:
                            continue
                    current_pai[(prev_tag, curr_tag)] = tag_max[1]
                    bp[(k - 1, prev_tag, curr_tag)] = tag_max[0]
        sort_curr_pai = sorted(current_pai.items(), key=lambda x: x[1], reverse=True)[:beam_threshold]
        current_pai = {key: value for key, value in sort_curr_pai}
        p_pairs = list(current_pai.keys())
        prev_pai = current_pai.copy()
        current_pai = {}
        p_tags = [tup[1] for tup in p_pairs]  # S(k-1)
        pp_tags = [tup[0] for tup in p_pairs]
    max_key = max(prev_pai, key=prev_pai.get)
    last_tag = max_key[1]
    prev_last_tag = max_key[0]
    predictions.extend([last_tag, prev_last_tag])
    for k in range(len(sentence) - 3, 2, -1):
        t = bp[(k, prev_last_tag, last_tag)]
        predictions.append(t)
        last_tag = prev_last_tag
        prev_last_tag = t
    print('hi!')
    predictions.append('*')
    predictions.reverse()

    return predictions


def create_history(pp_tag, p_tag, c_tag, sentence, index):
    c_word = sentence[index]
    p_word = sentence[index - 1]
    ne_word = sentence[index + 1]
    history = [c_word, c_tag, p_word, p_tag, pp_tag, ne_word]
    return history


def calculate_q_probability(weights, tags_3, possible_perv_pairs, sentence, index, feature2id):
    # tags_1 is pp_tag tags_2 is p_tag
    q_probabilities = {}
    denominator = {}
    for pair in possible_perv_pairs:
        for curr_tag in tags_3:
            history = create_history(pair[0], pair[1], curr_tag, sentence, index)
            value = math.exp(feature_weights_inner_product(weights, feature2id, history, curr_tag))
            q_probabilities[(pair[0], pair[1], curr_tag)] = value  # THIS IS THE NEMRATOR BEFORE DIVISION
            if pair in denominator:
                denominator[pair] += value
            else:
                denominator[pair] = value
    for key, value in q_probabilities.items():
        q_probabilities[key] = value / (denominator[(key[0], key[1])])

    return q_probabilities


def get_all_possible_pairs(tags_1, tags_2):
    x, y = np.meshgrid(tags_1, tags_2)

    return list(zip(x.flatten(), y.flatten()))


def feature_weights_inner_product(weights, feature2id, history, tag):
    feature_vecotr = create_feature_vector(history, weights.size, feature2id.feature_to_idx, tag)
    return np.inner(weights, feature_vecotr)


def create_feature_vector(history, size, feature_to_idx, c_tag):
    vec_features = np.zeros(size)
    c_word = history[0]
    p_word = history[2]
    p_tag = history[3]
    pp_tag = history[4]
    ne_word = history[5]
    # f100
    if (c_word, c_tag) in feature_to_idx['f100']:
        index = feature_to_idx['f100'][(c_word, c_tag)]
        vec_features[index] = 1
    # f103
    if (pp_tag, p_tag, c_tag) in feature_to_idx['f103']:
        index = feature_to_idx['f103'][(pp_tag, p_tag, c_tag)]
        vec_features[index] = 1
    # f104
    if (p_tag, c_tag) in feature_to_idx['f104']:
        index = feature_to_idx['f104'][(p_tag, c_tag)]
        vec_features[index] = 1
    # f105
    if c_tag in feature_to_idx['f105']:
        index = feature_to_idx['f105'][c_tag]
        vec_features[index] = 1
    # f106
    if (p_word, c_tag) in feature_to_idx['f106']:
        index = feature_to_idx['f106'][(p_word, c_tag)]
        vec_features[index] = 1
    # f106
    if (ne_word, c_tag) in feature_to_idx['f107']:
        index = feature_to_idx['f107'][(ne_word, c_tag)]
        vec_features[index] = 1

    return vec_features


def tag_all_test(test_path, pre_trained_weights, feature2id, predictions_path):
    tagged = "test" in test_path
    test,true_pred = read_test(test_path, tagged=tagged)

    output_file = open(predictions_path, "a+")
    predictions = [] # raz added
    for k, sen in tqdm(enumerate(test), total=len(test)):
        sentence = sen[0]
        pred = memm_viterbi(sentence, pre_trained_weights, feature2id)[1:]
        predictions.extend(pred) # raz added
        sentence = sentence[2:]
        for i in range(len(pred)):
            if i > 0:
                output_file.write(" ")
            output_file.write(f"{sentence[i]}_{pred[i]}")
        output_file.write("\n")
    output_file.close()
    return predictions,true_pred # raz added

