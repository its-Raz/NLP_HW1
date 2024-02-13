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
        feature_dict_list = ["f100", "f101", "f102", "f103", "f104", "f105",
                             "f106", "f107", "f108", "f109","f110","f111"]  # the feature classes used in the code
        self.feature_rep_dict = {fd: OrderedDict() for fd in feature_dict_list}
        '''
        A dictionary containing the counts of each data regarding a feature class. For example in f100, would contain
        the number of times each (word, tag) pair appeared in the text.
        '''
        self.tags = set()  # a set of all the seen tags
        self.tags.add("~")
        # a dictionary with the number of times each tag appeared in the text
        self.tags_counts = defaultdict(int)
        # a dictionary with the number of times each word appeared in the text
        self.words_count = defaultdict(int)
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
                # We added for optimization
                sentence = [("*", "*"), ("*", "*")]
                for word_idx in range(len(split_words)):
                    cur_word, cur_tag = split_words[word_idx].split('_')
                    self.tags.add(cur_tag)
                    self.tags_counts[cur_tag] += 1
                    self.words_count[cur_word] += 1
                    pair = (cur_word, cur_tag)  # We added for optimization
                    sentence.append(pair)  # We added for optimization
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
                    curr_word = sentence[i][0]  # ADDED CODE FOR f101+102
                    cur_tag = sentence[i][1]
                    prefixes = []
                    suffixes = []
                    if len(curr_word) >= 5:
                        prefixes, suffixes = get_prefixes_suffixes(curr_word)

                    history = (
                        sentence[i][0], sentence[i][1], sentence[i -
                                                                 1][0], sentence[i - 1][1], sentence[i - 2][0],
                        sentence[i - 2][1], sentence[i + 1][0], prefixes, suffixes)

                    self.histories.append(history)

                    # f101+102
                    if len(curr_word) >= 4:
                        for suffix, prefix in zip(suffixes, prefixes):
                            if (suffix, cur_tag) not in self.feature_rep_dict["f101"]:
                                self.feature_rep_dict["f101"][(
                                    suffix, cur_tag)] = 1
                            else:
                                self.feature_rep_dict["f101"][(
                                    suffix, cur_tag)] += 1
                            if (prefix, cur_tag) not in self.feature_rep_dict["f102"]:
                                self.feature_rep_dict["f102"][(
                                    prefix, cur_tag)] = 1
                            else:
                                self.feature_rep_dict["f102"][(
                                    prefix, cur_tag)] += 1
                    # f103
                    if (sentence[i - 2][1], sentence[i - 1][1], sentence[i][1]) not in self.feature_rep_dict["f103"]:
                        self.feature_rep_dict["f103"][(
                            sentence[i - 2][1], sentence[i - 1][1], sentence[i][1])] = 1
                    else:
                        self.feature_rep_dict["f103"][(
                            sentence[i - 2][1], sentence[i - 1][1], sentence[i][1])] += 1

                    # f104 + f106

                    if (sentence[i - 1][1], sentence[i][1]) not in self.feature_rep_dict["f104"]:
                        self.feature_rep_dict["f104"][(
                            sentence[i - 1][1], sentence[i][1])] = 1
                    else:
                        self.feature_rep_dict["f104"][(
                            sentence[i - 1][1], sentence[i][1])] += 1

                    if (sentence[i - 1][0], sentence[i][1]) not in self.feature_rep_dict["f106"]:
                        self.feature_rep_dict["f106"][(
                            sentence[i - 1][0], sentence[i][1])] = 1
                    else:
                        self.feature_rep_dict["f106"][(
                            sentence[i - 1][0], sentence[i][1])] += 1

                    # f105

                    if (sentence[i][1]) not in self.feature_rep_dict["f105"]:
                        self.feature_rep_dict["f105"][(sentence[i][1])] = 1
                    else:
                        self.feature_rep_dict["f105"][(sentence[i][1])] += 1

                    # f107
                    if (sentence[i][0], sentence[i-1][1]) not in self.feature_rep_dict["f107"]:
                        self.feature_rep_dict["f107"][(
                            sentence[i][0], sentence[i-1][1])] = 1
                    else:
                        self.feature_rep_dict["f107"][(
                            sentence[i][0], sentence[i-1][1])] += 1

                    # f108
                    template = build_template(sentence[i][0])
                    if template != "OnlyAlpha" and template != "Neither": # anything else contains numerical rep
                        if (template, sentence[i][1]) not in self.feature_rep_dict["f108"]:
                            self.feature_rep_dict["f108"][(
                                template, sentence[i][1])] = 1
                        else:
                            self.feature_rep_dict["f108"][(
                                template, sentence[i][1])] += 1

                    # f109
                    if has_uppercase(sentence[i][0]):
                        plural = is_plural(sentence[i][0])
                        uppers = more_then_one_upper(sentence[i][0])
                        if (plural,uppers,sentence[i][1]) not in self.feature_rep_dict["f109"]:
                                self.feature_rep_dict["f109"][(plural,uppers,sentence[i][1])] = 1
                        else:
                                self.feature_rep_dict["f109"][(plural,uppers,sentence[i][1])] += 1
                    # f110+f111
                    if len(sentence[i][0])>=4:
                        common_suf,suffix = common_suffix(sentence[i][0])
                        common_pre,prefix = common_prefix(sentence[i][0])
                        if common_suf:
                            if (suffix,sentence[i-1][1], sentence[i][1]) not in self.feature_rep_dict["f110"]:
                                self.feature_rep_dict["f110"][(suffix,sentence[i-1][1], sentence[i][1])] = 1
                            else:
                                self.feature_rep_dict["f110"][(suffix,sentence[i-1][1], sentence[i][1])] += 1
                        if common_pre:
                            if (prefix,sentence[i-1][1], sentence[i][1]) not in self.feature_rep_dict["f111"]:
                                self.feature_rep_dict["f111"][(prefix,sentence[i-1][1], sentence[i][1])] = 1
                            else:
                                self.feature_rep_dict["f111"][(prefix,sentence[i-1][1], sentence[i][1])] += 1


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
        # feature count threshold - empirical count must be higher than this
        self.threshold = threshold

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
            "f109": OrderedDict(),
            "f110": OrderedDict(),
            "f111": OrderedDict(),
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
        threshold_for_pre_suf = 30  # ADDED threshold for f101 and f102
        upper_treshold = 25
        upper2_thresh = 5
        upper9=10
        upper4=10
        upper10=5
        threshold = self.threshold
        for feat_class in self.feature_statistics.feature_rep_dict:
            if feat_class not in self.feature_to_idx:
                continue
            # if feat_class == "f101" or feat_class == "f102":
            #     threshold = threshold_for_pre_suf
            # if feat_class == "f104":
            #     threshold = upper_treshold
            # if feat_class == "f103":
            #     threshold = upper2_thresh
            # if feat_class == "f108":
            #     threshold=upper4
            # if feat_class == "f109":
            #     threshold = upper9
            # if feat_class == "f110" or feat_class == "f111":
            #     threshold = upper10
            # if feat_class == "f106" :
            #     threshold=5

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
                history = (hist[0], y_tag, hist[2], hist[3], hist[4], hist[5],
                           hist[6], hist[7], hist[8])  # We added prefixes and sufi
                demi_hist = history[:7]
                self.histories_features[demi_hist] = []
                # we changed demi_hist to history
                for c in represent_input_with_features(history, self.feature_to_idx):
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
    template = build_template(c_word)


    # f100
    if (c_word, c_tag) in dict_of_dicts["f100"]:
        features.append(dict_of_dicts["f100"][(c_word, c_tag)])
    # f101+102
    for suffix, prefix in zip(suffixes, prefixes):
        if (suffix, c_tag) in dict_of_dicts["f101"]:
            features.append(dict_of_dicts["f101"][(suffix, c_tag)])
        if (prefix, c_tag) in dict_of_dicts["f102"]:
            features.append(dict_of_dicts["f102"][(prefix, c_tag)])
    # f103
    if (pp_tag, p_tag, c_tag) in dict_of_dicts["f103"]:
        features.append(dict_of_dicts["f103"][(pp_tag, p_tag, c_tag)])
    # f104
    if (p_tag, c_tag) in dict_of_dicts["f104"]:
        features.append(dict_of_dicts["f104"][(p_tag, c_tag)])
    # f105
    if (c_tag) in dict_of_dicts["f105"]:
        features.append(dict_of_dicts["f105"][(c_tag)])
    # f106
    if (p_word, c_tag) in dict_of_dicts["f106"]:
        features.append(dict_of_dicts["f106"][(p_word, c_tag)])
    # f107
    if (n_word, c_tag) in dict_of_dicts["f107"]:
        features.append(dict_of_dicts["f107"][(n_word, c_tag)])
    # f108
    if template != "OnlyAlpha" and template!="Neither":
        if (template, c_tag) in dict_of_dicts["f108"]:
            features.append(dict_of_dicts["f108"][(template, c_tag)])
    # f109
    if has_uppercase(c_word):
        plural = is_plural(c_word)
        uppers = more_then_one_upper(c_word)
        if (plural,uppers, c_tag) in dict_of_dicts["f109"]:
            features.append(dict_of_dicts["f109"][(plural,uppers, c_tag)])
    #f110
    if len(c_word)>=4:
        com_suffix,suffix = common_suffix(c_word)
        com_prefix,prefix = common_prefix(c_word)
        if com_suffix:
            if (suffix, p_tag, c_tag) in dict_of_dicts["f110"]:
                features.append(dict_of_dicts["f110"][(suffix, p_tag, c_tag)])
        if com_prefix:
            if (prefix, p_tag, c_tag) in dict_of_dicts["f111"]:
                features.append(dict_of_dicts["f111"][(prefix, p_tag, c_tag)])

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
    true_pred = []  # raz added
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
    return list_of_sentences, true_pred  # raz added true_pred


def get_word_type(word):
    has_alpha = False
    has_digit = False

    for char in word:
        if char.isalpha():
            has_alpha = True
        elif char.isdigit():
            has_digit = True

        # Break the loop if both conditions are met
        if has_alpha and has_digit:
            break

    if has_alpha and has_digit:
        return "AlphaNumeric"
    elif has_alpha:
        return "Alpha"
    elif has_digit:
        return "Numeric"
    else:
        return "Neither"


def is_numeric_with_or_without_signs(word):
    # signs without ' - ' beacuse we did a pre check on it.
    template = ""
    current_is_digit = False
    for char in word:
        if char.isdigit() == False:
            current_is_digit = False
            template += char
        else:
            if(current_is_digit==False):
                template+='digit'
                current_is_digit = True

    return template


def is_numerical_string(word):
    # List of words that represent numbers
    number_words = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine",
                    "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen",
                    "seventeen", "eighteen", "nineteen", "twenty", "thirty", "forty", "fifty",
                    "sixty", "seventy", "eighty", "ninety", "hundred", "thousand", "million",
                    "billion", "trillion"]
    # lower the word
    word = word.lower()
    # plural to singel if there is a 's' in the end.
    if word[-1] == 's':
        word = word[0:-1]

    # Check if the word is in the list of number words
    return word in number_words


def return_our_tag_of_word(word):
    word_type = get_word_type(word)
    if word_type == "Alpha":
        if is_numerical_string(word) == True:
            return "numerical_string"
        else:
            return "OnlyAlpha"
    elif word_type == "Numeric":
        return is_numeric_with_or_without_signs(word)
    elif word_type == "Neither":
        return "Neither"
    # for AlphaNumeric:
    return "Mixed"


def build_template(word):
    # samples :
    # four-ship  -> numerical_string-OnlyAlpha
    # 1\/2-year  -> \/-OnlyAlpha
    # 2003-2005  -> OnlyDigits-OnlyDigits
    template = ""
    array_of_words = word.split("-")
    if(len(array_of_words)==1):
        template+=return_our_tag_of_word(word)
        return template
    else:
        for word in array_of_words:
            template += return_our_tag_of_word(word)
            template += '-'
        # remove the last -
    return template[0:-1]


def has_uppercase(word):
    """
    Use any Becuase it can has upper case char in the middle
    of a word. Example : eBay (brand)
    """
    return word[0].isupper()

def more_then_one_upper(word):
    counter = 0
    for char in word:
        if char.isupper():
            counter+=1
    if counter > 1:
        return True
    return False
def is_plural(word):
    if word[-1] == 's':
        if word[-2] == 's':
            return False
    return True

def common_suffix(word):
    #TODO y is in ity ify, s in ness ious, enous , run from 4/5 last letters
    suffixes_length_1 = ["s", "y"]
    suffixes_length_2 = ["er", "or", "ty", "al", "ic", "ly", "en", "es", "ed"]
    suffixes_length_3 = ["ist", "ity", "ful",  "ion", "ate", "ify", "ize", "ise", "hip","ive", "dom"]
    suffixes_length_4 = ["ness", "ible", "ious",  "ship", "hood"]
    suffixes_length_5 = ["ation", "ition", "ative", "itive", "enous"]
    suffixes_lists = [
        suffixes_length_1,
        suffixes_length_2,
        suffixes_length_3,
        suffixes_length_4,
        suffixes_length_5
    ]
    suffix = ''
    for index, char in enumerate(reversed(word), 0):
        suffix+=char
        if suffix in suffixes_lists[index]:
            if suffix == 's':
                if word[-2:] == 'es':
                    return True, 'es'
                else:
                    return True, suffix
            return True,suffix
        if index == (len(word) - 1) or index == 4:
            return False,''
    return False,''

def common_prefix(word):

    pre_fixes_1_letters = []
    prefixes_2_letters = ['un', 're', 'in', 'im', 'en', 'em', 'de', 'dis', 'ex', "ir","bi"]
    prefixes_3_letters = ['pre', 'pro', 'sub', 'mis', 'non', 'tri', 'uni', 'tri',  "dis"]
    prefixes_4_letters = ['anti', 'auto', 'over', 'semi', 'post', 'mega',  'mini', 'mono', 'tele']
    prefixes_5_letters = ['super', 'hyper', 'under', 'inter', 'extra', 'infra', 'multi', 'macro', 'micro']
    prefixes_list = [pre_fixes_1_letters,prefixes_2_letters,prefixes_3_letters,prefixes_4_letters,prefixes_5_letters]
    prefix = ''
    for index, char in enumerate(word, 0):
        prefix += char
        if prefix in prefixes_list[index]:
            return True, prefix
        if index == (len(word) - 1) or index == 3:
            return False, ''
    return False, ''