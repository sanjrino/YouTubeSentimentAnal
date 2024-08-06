import nltk
import sklearn_crfsuite
from sklearn_crfsuite import metrics
import pickle

# loads Penn Treebank corpus
nltk.download('treebank')
corpus = nltk.corpus.treebank.tagged_sents()

# extracts features for each word in a sentence
def get_word_features(sentence, i):
    word = sentence[i][0]
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
        'prev_word': '' if i == 0 else sentence[i-1][0],
        # extracting next word
        'next_word': '' if i == len(sentence)-1 else sentence[i+1][0],
        'has_hyphen': '-' in word,  # if word has hyphen
        'is_numeric': word.isdigit(),  # if word is in numeric
        'capitals_inside': word[1:].lower() != word[1:]  # if capital letters in word
    }
    return features

# extracts features for each sentence in corpus
X = []  # features
y = []  # labels
for sentence in corpus:
    X_sentence = []
    y_sentence = []
    for i in range(len(sentence)):
        X_sentence.append(get_word_features(sentence, i))
        y_sentence.append(sentence[i][1])
    X.append(X_sentence)
    y.append(y_sentence)

# split data into training and testing sets
split = int(0.8 * len(X))
X_train = X[:split]
y_train = y[:split]
X_test = X[split:]
y_test = y[split:]

# training CRF model on training data
crf = sklearn_crfsuite.CRF(
    algorithm='lbfgs',
    c1=0.1,
    c2=0.1,
    max_iterations=100,
    all_possible_transitions=True
)
crf.fit(X_train, y_train)

# saves the model
with open('crf_pos_tagger.pkl', 'wb') as file:
    pickle.dump(crf, file)

# evaluate performance
y_pred = crf.predict(X_test)
accuracy = metrics.flat_accuracy_score(y_test, y_pred)
print(f'Accuracy: {accuracy:.4f}')

# finds nouns and adjectives in a sentence
def find_nouns_adjectives(sentence, crf_model):
    features = [get_word_features([(word, '') for word in sentence], i) for i in range(len(sentence))]
    predicted_labels = crf_model.predict([features])[0]
    nouns = [(word, label) for word, label in zip(sentence, predicted_labels) if label in ['NN', 'NNS', 'NNP', 'NNPS']]
    adjectives = [(word, label) for word, label in zip(sentence, predicted_labels) if label in ['JJ', 'JJR', 'JJS']]
    return nouns, adjectives

# example sentence
sentence = ['Bob', 'is', 'unsure', 'how', 'Anne', 'will', 'pass', 'the', 'course', 'on', 'computers']
nouns, adjectives = find_nouns_adjectives(sentence, crf)
print("Nouns:", nouns)
print("Adjectives:", adjectives)
