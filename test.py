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


# Example usage:
word1 = "tw#@o"
word2 = "2:00"
word3 = "123"
word4 = "abc123"

print("Word Type:", get_word_type(word1))  # Output: Alpha
print("Word Type:", get_word_type(word2))  # Output: Numeric
print("Word Type:", get_word_type(word3))  # Output: Numeric
print("Word Type:", get_word_type(word4))  # Output: AlphaNumeric
