import re


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
            if (current_is_digit == False):
                template += 'digits'
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


def regex_function(word):
    # Regular expression pattern to split the string by uppercase letters, lowercase letters, and digits
    pattern = r'[A-Za-z]+|\d+|\D'
    return re.findall(pattern, word)


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
        return word
    # for AlphaNumeric - never used beacuse regex
    return "AlphaNumeric"


def build_template(word):
    # samples :
    # four-ship  -> numerical_string-OnlyAlpha
    # 1\/2-year  -> \/-OnlyAlpha
    # 2003-2005  -> OnlyDigits-OnlyDigits
    regex_list = regex_function(word)
    list_to_concat = []
    for word in regex_list:
        list_to_concat.append(return_our_tag_of_word(word))

    return ''.join(list_to_concat)


print(build_template("$23"))
