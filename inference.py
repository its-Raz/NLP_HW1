from preprocessing import read_test
from tqdm import tqdm
import numpy as np
import math


def memm_viterbi(sentence, pre_trained_weights, feature2id):
    """
    Write your MEMM Viterbi implementation below
    You can implement Beam Search to improve runtime
    Implement q efficiently (refer to conditional probability definition in MEMM slides)
    """
    all_tags = feature2id.feature_statistics.tags
    current_pai = {}
    prev_pai = {}
    bp = {}
    predictions = []
    for k in range(2,len(sentence)-1):
        for curr_tag in all_tags:
            for prev_tag in all_tags:
                tag_max = ('', 0)
                for t in all_tags:
                    history = create_history(t,prev_tag,curr_tag,sentence,k)
                    q = calculate_q_probability(pre_trained_weights,feature2id,history)
                    if k == 1:
                        value = q
                    else:
                        value = prev_pai[(prev_tag,curr_tag)]*q
                    if value > tag_max[1]:
                        tag_max = (t,value)
                current_pai[(prev_tag,curr_tag)] = tag_max[1]
                bp[(k,prev_tag,curr_tag)] = tag_max[0]
        prev_pai = current_pai

    # backtracking
    max_key = max(current_pai, key=current_pai.get)
    last_tag = max_key[1]
    prev_last_tag = max_key[0]
    predictions.append(last_tag)
    predictions.append(prev_last_tag)
    for k in range (len(sentence)-4,1,-1):



    return 0










def create_history(pp_tag,p_tag,c_tag,sentence,index):
    curr_word = sentence[index]
    prev_word = sentence[index-1]
    next_word = sentence[index+1]
    history = [curr_word,c_tag]
    return history

def calculate_q_probability(weights, feature2id, history):
    # TODO: optimize
    curr_tag = history[1]
    numerator = math.exp(feature_weights_inner_product(weights, feature2id, history,curr_tag))
    all_tags = feature2id.feature_statistics.tags
    denominator = 0
    for tag in all_tags:
        denominator += math.exp(feature_weights_inner_product(weights, feature2id, history, tag))
    return numerator / denominator


def feature_weights_inner_product(weights, feature2id, history,tag):
    feature_vecotr = create_feature_vector(history, weights.size, feature2id.feature_to_idx,tag)
    return np.inner(weights, feature_vecotr)


def create_feature_vector(history, size, feature_to_idx,curr_tag):
    vec_features = np.zeros(size)
    curr_word = history[0]
    # f100
    if (curr_word, curr_tag) in feature_to_idx['f100']:
        index = feature_to_idx['f100'][(curr_word, curr_tag)]
        vec_features[index] = 1
    # TODO ADD ALL POSSIBLE FEATURES
    return vec_features


def tag_all_test(test_path, pre_trained_weights, feature2id, predictions_path):
    tagged = "test" in test_path
    test = read_test(test_path, tagged=tagged)

    output_file = open(predictions_path, "a+")

    for k, sen in tqdm(enumerate(test), total=len(test)):
        sentence = sen[0]
        pred = memm_viterbi(sentence, pre_trained_weights, feature2id)[1:]
        sentence = sentence[2:]
        for i in range(len(pred)):
            if i > 0:
                output_file.write(" ")
            output_file.write(f"{sentence[i]}_{pred[i]}")
        output_file.write("\n")
    output_file.close()
