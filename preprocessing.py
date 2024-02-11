from scipy import sparse
from collections import OrderedDict, defaultdict
import numpy as np
from typing import List, Dict, Tuple


WORD = 0
TAG = 1


class FeatureStatistics:
    def __init__(self):
        self.n_total_features = 0  # Total number of features accumulated

        # Init all features dictionaries
        feature_dict_list = ["f100","f101","f102","f103","f104","f105","f106","f107","f108","f109"]  # the feature classes used in the code
        self.feature_rep_dict = {fd: OrderedDict() for fd in feature_dict_list}
        '''
        A dictionary containing the counts of each data regarding a feature class. For example in f100, would contain
        the number of times each (word, tag) pair appeared in the text.
        '''
        self.tags = set()  # a set of all the seen tags
        self.tags.add("~")
        self.tags_counts = defaultdict(int)  # a dictionary with the number of times each tag appeared in the text
        self.words_count = defaultdict(int)  # a dictionary with the number of times each word appeared in the text
        self.histories = []  # a list of all the histories seen at the test

    def get_word_tag_pair_count(self, file_path) -> None:
        """

            Extract out of text all word/tag pairs
            @param: file_path: full path of the file to read
            Updates the histories list
        """
        with open(file_path) as file:
            for line in file:
                if line[-1:] == "\n":
                    line = line[:-1]
                split_words = line.split(' ')
                sentence = [("*", "*"), ("*", "*")] # We added for optimization
                for word_idx in range(len(split_words)):
                    cur_word, cur_tag = split_words[word_idx].split('_')
                    self.tags.add(cur_tag)
                    self.tags_counts[cur_tag] += 1
                    self.words_count[cur_word] += 1
                    pair = (cur_word,cur_tag) # We added for optimization
                    sentence.append(pair) # We added for optimization
                    # f100
                    if (cur_word, cur_tag) not in self.feature_rep_dict["f100"]:
                        self.feature_rep_dict["f100"][(cur_word, cur_tag)] = 1
                    else:
                        self.feature_rep_dict["f100"][(cur_word, cur_tag)] += 1
                # sentence = [("*", "*"), ("*", "*")]
                # for pair in split_words:
                #     sentence.append(tuple(pair.split("_")))
                sentence.append(("~", "~"))

                for i in range(2, len(sentence) - 1):
                    curr_word = sentence[i][0] # ADDED CODE FOR f101+102
                    cur_tag = sentence[i][1]
                    prefixes = []
                    suffixes = []
                    if len(curr_word) >= 5:
                        prefixes,suffixes = get_prefixes_suffixes(curr_word)

                    history = (
                        sentence[i][0], sentence[i][1], sentence[i - 1][0], sentence[i - 1][1], sentence[i - 2][0],
                        sentence[i - 2][1], sentence[i + 1][0],prefixes,suffixes)

                    self.histories.append(history)

                    # f101+102
                    if len(curr_word)>=5:
                        for suffix,prefix in zip(suffixes,prefixes):
                            if (suffix, cur_tag) not in self.feature_rep_dict["f101"]:
                                self.feature_rep_dict["f101"][(suffix, cur_tag)] = 1
                            else:
                                self.feature_rep_dict["f101"][(suffix, cur_tag)] += 1
                            if (prefix, cur_tag) not in self.feature_rep_dict["f102"]:
                                self.feature_rep_dict["f102"][(prefix, cur_tag)] = 1
                            else:
                                self.feature_rep_dict["f102"][(prefix, cur_tag)] += 1
                    # f103
                    if (sentence[i - 2][1], sentence[i - 1][1],sentence[i][1]) not in self.feature_rep_dict["f103"]:
                        self.feature_rep_dict["f103"][(sentence[i - 2][1], sentence[i - 1][1],sentence[i][1])] = 1
                    else:
                        self.feature_rep_dict["f103"][(sentence[i - 2][1], sentence[i - 1][1],sentence[i][1])] += 1

                    # f104 + f106

                    if (sentence[i - 1][1],sentence[i][1]) not in self.feature_rep_dict["f104"]:
                        self.feature_rep_dict["f104"][(sentence[i - 1][1],sentence[i][1])] = 1
                    else:
                        self.feature_rep_dict["f104"][(sentence[i - 1][1],sentence[i][1])] += 1

                    if (sentence[i - 1][0],sentence[i][1]) not in self.feature_rep_dict["f106"]:
                        self.feature_rep_dict["f106"][(sentence[i - 1][0],sentence[i][1])] = 1
                    else:
                        self.feature_rep_dict["f106"][(sentence[i - 1][0],sentence[i][1])] += 1

                    #f105

                    if (sentence[i][1]) not in self.feature_rep_dict["f105"]:
                        self.feature_rep_dict["f105"][(sentence[i][1])] = 1
                    else:
                        self.feature_rep_dict["f105"][(sentence[i][1])] += 1

                    #f107
                    if (sentence[i][0],sentence[i-1][1]) not in self.feature_rep_dict["f107"]:
                        self.feature_rep_dict["f107"][(sentence[i][0],sentence[i-1][1])] = 1
                    else:
                        self.feature_rep_dict["f107"][(sentence[i][0],sentence[i-1][1])] += 1

                    #f108
                    numeric,template = is_numeric(sentence[i][0])
                    if numeric:
                        if (template,sentence[i][1]) not in self.feature_rep_dict["f108"]:
                            self.feature_rep_dict["f108"][(template,sentence[i][1])] = 1
                        else:
                            self.feature_rep_dict["f108"][(template,sentence[i][1])] += 1

                    #f109

                    # if has_uppercase(sentence[i][0]):
                    #     if (sentence[i][0],sentence[i][1]) not in self.feature_rep_dict["f109"]:
                    #             self.feature_rep_dict["f109"][(sentence[i][0],sentence[i][1])] = 1
                    #     else:
                    #             self.feature_rep_dict["f109"][(sentence[i][0],sentence[i][1])] += 1




def get_prefixes_suffixes(word):
    prefixes = [word[:i] for i in range(2, min(5, len(word)-2))]
    suffixes = [word[-i:] for i in range(2, min(5, len(word)-2))]
    return prefixes, suffixes
class Feature2id:
    def __init__(self, feature_statistics: FeatureStatistics, threshold: int):
        """
        @param feature_statistics: the feature statistics object
        @param threshold: the minimal number of appearances a feature should have to be taken
        """
        self.feature_statistics = feature_statistics  # statistics class, for each feature gives empirical counts
        self.threshold = threshold  # feature count threshold - empirical count must be higher than this

        self.n_total_features = 0  # Total number of features accumulated

        # Init all features dictionaries
        self.feature_to_idx = {
            "f100": OrderedDict(),
            "f101": OrderedDict(),
            "f102": OrderedDict(),
            "f103": OrderedDict(),
            "f104": OrderedDict(),
            "f105": OrderedDict(),
            "f106": OrderedDict(),
            "f107": OrderedDict(),
            "f108": OrderedDict(),
            # "f109": OrderedDict(),
        }
        self.represent_input_with_features = OrderedDict()
        self.histories_matrix = OrderedDict()
        self.histories_features = OrderedDict()
        self.small_matrix = sparse.csr_matrix
        self.big_matrix = sparse.csr_matrix

    def get_features_idx(self) -> None:
        """
        Assigns each feature that appeared enough time in the train files an idx.
        Saves those indices to self.feature_to_idx
        """
        threshold_for_pre_suf = 30 # ADDED threshold for f101 and f102
        upper_treshold = 25
        upper2_thresh = 5


        threshold = self.threshold
        for feat_class in self.feature_statistics.feature_rep_dict:
            if feat_class not in self.feature_to_idx:
                continue
            if feat_class == "f101" or feat_class == "f102" :
                threshold = threshold_for_pre_suf
            if feat_class == "f104":
                threshold = upper_treshold
            if feat_class == "f103":
                threshold=upper2_thresh
            for feat, count in self.feature_statistics.feature_rep_dict[feat_class].items():
                if count >= threshold:
                    self.feature_to_idx[feat_class][feat] = self.n_total_features
                    self.n_total_features += 1
            threshold = self.threshold
        print(f"you have {self.n_total_features} features!")

    def calc_represent_input_with_features(self) -> None:
        """
        initializes the matrices used in the optimization process - self.big_matrix and self.small_matrix
        """
        big_r = 0
        big_rows = []
        big_cols = []
        small_rows = []
        small_cols = []
        for small_r, hist in enumerate(self.feature_statistics.histories):
            for c in represent_input_with_features(hist, self.feature_to_idx):
                small_rows.append(small_r)
                small_cols.append(c)
            for r, y_tag in enumerate(self.feature_statistics.tags):
                history = (hist[0], y_tag, hist[2], hist[3], hist[4], hist[5], hist[6],hist[7],hist[8]) # We added prefixes and sufi
                demi_hist = history[:7]
                self.histories_features[demi_hist] = []
                for c in represent_input_with_features(history, self.feature_to_idx): # we changed demi_hist to history
                    big_rows.append(big_r)
                    big_cols.append(c)
                    self.histories_features[demi_hist].append(c)
                big_r += 1
        self.big_matrix = sparse.csr_matrix((np.ones(len(big_rows)), (np.array(big_rows), np.array(big_cols))),
                                            shape=(len(self.feature_statistics.tags) * len(
                                                self.feature_statistics.histories), self.n_total_features),
                                            dtype=bool)
        self.small_matrix = sparse.csr_matrix(
            (np.ones(len(small_rows)), (np.array(small_rows), np.array(small_cols))),
            shape=(len(
                self.feature_statistics.histories), self.n_total_features), dtype=bool)


def represent_input_with_features(history: Tuple, dict_of_dicts: Dict[str, Dict[Tuple[str, str], int]])\
        -> List[int]:
    """
        Extract feature vector in per a given history
        @param history: tuple{c_word, c_tag, p_word, p_tag, pp_word, pp_tag, n_word}
        @param dict_of_dicts: a dictionary of each feature and the index it was given
        @return a list with all features that are relevant to the given history
    """
    c_word = history[0]
    c_tag = history[1]
    p_word = history[2]
    p_tag = history[3]
    pp_word = history[4]
    pp_tag = history[5]
    n_word = history[6]
    prefixes = history[7]
    suffixes = history[8]
    features = []
    numeric,template = is_numeric(c_word)

    # f100
    if (c_word, c_tag) in dict_of_dicts["f100"]:
        features.append(dict_of_dicts["f100"][(c_word, c_tag)])
    # f101+102
    for suffix,prefix in zip(suffixes,prefixes):
        if (suffix, c_tag) in dict_of_dicts["f101"]:
            features.append(dict_of_dicts["f101"][(suffix, c_tag)])
        if (prefix, c_tag) in dict_of_dicts["f102"]:
            features.append(dict_of_dicts["f102"][(prefix, c_tag)])
    # f103
    if (pp_tag,p_tag,c_tag) in dict_of_dicts["f103"]:
        features.append(dict_of_dicts["f103"][(pp_tag,p_tag,c_tag)])
    # f104
    if (p_tag, c_tag) in dict_of_dicts["f104"]:
        features.append(dict_of_dicts["f104"][(p_tag, c_tag)])
    # f105
    if (c_tag) in dict_of_dicts["f105"]:
        features.append(dict_of_dicts["f105"][(c_tag)])
    # f106
    if (p_word,c_tag) in dict_of_dicts["f106"]:
        features.append(dict_of_dicts["f106"][(p_word,c_tag)])
    #f107
    if (n_word,c_tag) in dict_of_dicts["f107"]:
        features.append(dict_of_dicts["f107"][(n_word,c_tag)])
    # f108
    if numeric:
        if (template, c_tag) in dict_of_dicts["f108"]:
            features.append(dict_of_dicts["f108"][(template, c_tag)])
    # f109
    # if (c_word, c_tag) in dict_of_dicts["f109"]:
    #     features.append(dict_of_dicts["f109"][(c_word, c_tag)])



    return features


def preprocess_train(train_path, threshold):
    # Statistics
    statistics = FeatureStatistics()
    statistics.get_word_tag_pair_count(train_path)


    # feature2id
    feature2id = Feature2id(statistics, threshold)
    feature2id.get_features_idx()
    feature2id.calc_represent_input_with_features()

    print(feature2id.n_total_features)

    for dict_key in feature2id.feature_to_idx:
        print(dict_key, len(feature2id.feature_to_idx[dict_key]))
    return statistics, feature2id


def read_test(file_path, tagged=True) -> List[Tuple[List[str], List[str]]]:
    """
    reads a test file
    @param file_path: the path to the file
    @param tagged: whether the file is tagged (validation set) or not (test set)
    @return: a list of all the sentences, each sentence represented as tuple of list of the words and a list of tags
    """
    true_pred = [] # raz added
    list_of_sentences = []
    with open(file_path) as f:
        for line in f:
            if line[-1:] == "\n":
                line = line[:-1]
            sentence = (["*", "*"], ["*", "*"])
            split_words = line.split(' ')
            for word_idx in range(len(split_words)):
                if tagged:
                    cur_word, cur_tag = split_words[word_idx].split('_')
                    true_pred.extend([cur_tag])  # raz added
                else:
                    cur_word, cur_tag = split_words[word_idx], ""
                sentence[WORD].append(cur_word)
                sentence[TAG].append(cur_tag)

            sentence[WORD].append("~")
            sentence[TAG].append("~")
            list_of_sentences.append(sentence)
    return list_of_sentences,true_pred # raz added true_pred

def is_numeric(word):

    # List of words that represent numbers
    number_words = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
                    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
                    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
                    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "million",
                    "billion", "trillion"]
    contains_letter = False
    contains_digit = False
    letters = ''
    chars = ''

    for i, char in enumerate(word):
        if char.isdigit():
            contains_digit = True
        elif char.isalpha():
            contains_letter = True
            letters += char
        else:

            chars += char
            if i < len(word) - 1:  # check if the string have more
                if (word[i + 1].isdigit() and contains_letter == False):  # no letters
                    if (contains_digit):
                        return True, chars
                elif (word[i + 1].isalpha() and contains_digit == False):  # e.g Four-year
                    if (letters.lower() in number_words):
                        template = word[i:len(word)]
                        return True, template
                elif (word[i + 1].isalpha() and contains_digit == True):
                    return True, word[i:len(word)]
                else:
                    chars += word[i + 1]

    if (contains_digit == True):
        if (contains_letter == False):
            return True, 'only_digit'
    else:  # digit false
        if contains_letter == True:
            if (word.lower() in number_words):  # two,Two
                return True, 'only_letters'
        else:  # no digitis and no letters
            return False, ''

    return False, ''

# def alpha_and_numeric(word):
#     # Remove unwanted characters
#     # List of words that represent numbers
#     number_words = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
#                     "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
#                     "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
#                     "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "million",
#                     "billion", "trillion"]
#
#
#     contains_digit = False
#     contains_letter = False
#     letters = ''
#     chars = ''



def has_uppercase(word):
    """
    Use any Becuase it can has upper case char in the middle
    of a word. Example : eBay (brand)
    """
    return word[0].isupper()

