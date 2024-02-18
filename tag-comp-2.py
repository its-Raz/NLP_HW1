import nltk
from nltk import pos_tag
from nltk.tokenize import word_tokenize

# Download the NLTK data (if not already downloaded)
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Function to tag a word with its part of speech


def tag_word(word):
    pos_tags = pos_tag([word])
    return f"{word}_{pos_tags[0][1]}"

# Function to process the entire line and replace _IDK tags while maintaining the original structure


def process_line(line):
    words = line.split(' ')
    updated_words = [
        tag_word(word[:-4]) if word.endswith('_IDK') else word for word in words]
    return ' '.join(updated_words)

# Function to tag a file and save the output while preserving the format


def tag_file(input_file_path, output_file_path):
    with open(input_file_path, 'r') as input_file:
        with open(output_file_path, 'w') as output_file:
            for input_line in input_file:
                input_line = input_line.strip()
                output_line = process_line(input_line)
                output_file.write(output_line + '\n')


# Example usage
input_file_path = 'data/comp1.wtag_public'  # Replace with your input file path
# Replace with your desired output file path
output_file_path = 'data/comp1test.wtag'

tag_file(input_file_path, output_file_path)
