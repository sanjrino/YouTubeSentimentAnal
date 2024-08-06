import pandas
import pickle
import nltk

# load the csv file
df = pandas.read_csv('name_here.csv')

# load the pos tagging model
with open('name_here.pkl', 'rb') as file:
    model = pickle.load(file)


# extracts features for each word in a sentence
def get_word_features(sentence, i):
    word = sentence[i]
    features = {
        'word': word,
        'is_first': i == 0,  # if the word is a first word
        'is_last': i == len(sentence) - 1,  # if the word is a last word
        'is_capitalized': word[0].upper() == word[0],
        'is_all_caps': word.upper() == word,  # word is in uppercase
        'is_all_lower': word.lower() == word,  # word is in lowercase
        # prefix of the word
        'prefix-1': word[0],
        'prefix-2': word[:2],
        'prefix-3': word[:3],
        # suffix of the word
        'suffix-1': word[-1],
        'suffix-2': word[-2:],
        'suffix-3': word[-3:],
        # extracting previous word
        'prev_word': '' if i == 0 else sentence[i - 1][0],
        # extracting next word
        'next_word': '' if i == len(sentence) - 1 else sentence[i + 1][0],
        'has_hyphen': '-' in word,  # if word has hyphen
        'is_numeric': word.isdigit(),  # if word is in numeric
        'capitals_inside': word[1:].lower() != word[1:]  # if capital letters in word
    }
    return features


# predict POS tags for a sentence
def predict_pos_tags(sentence, input_model):
    features = [get_word_features(sentence, i) for i in range(len(sentence))]
    # if CRF model
    predicted_labels = input_model.predict([features])[0]
    # if MaxEnt model
    # predicted_labels = [input_model.classify(f) for f in features]
    return list(zip(sentence, predicted_labels))


# get the x comments
x = 100
comments = df['Comment'].iloc[1:x]  # excluding the first row (header)

# tokenize comments and predict POS tags
for comment in comments:
    tokens = nltk.word_tokenize(comment)
    pos_tags = predict_pos_tags(tokens, model)

    # extract nouns and adjectives
    nouns = [(word, label) for word, label in pos_tags if label in ['NN', 'NNS', 'NNP', 'NNPS']]
    adjectives = [(word, label) for word, label in pos_tags if label in ['JJ', 'JJR', 'JJS']]

    print(f"Comment: {comment}")
    print(f"Nouns: {nouns}")
    print(f"Adjectives: {adjectives}\n")
