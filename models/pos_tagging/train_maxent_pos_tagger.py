import nltk
from nltk.classify import MaxentClassifier
import pickle

# loads Penn Treebank corpus
nltk.download('treebank')
corpus = nltk.corpus.treebank.tagged_sents()


# extracts features for each word in a sentence
def get_word_features(sentence, i):
    word = sentence[i][0]
    features = {
        'word': word,
        'is_first': i == 0,
        'is_last': i == len(sentence) - 1,
        'is_capitalized': word[0].upper() == word[0],
        'is_all_caps': word.upper() == word,
        'is_all_lower': word.lower() == word,
        'prefix-1': word[0],
        'prefix-2': word[:2],
        'prefix-3': word[:3],
        'suffix-1': word[-1],
        'suffix-2': word[-2:],
        'suffix-3': word[-3:],
        'prev_word': '' if i == 0 else sentence[i-1][0],
        'next_word': '' if i == len(sentence)-1 else sentence[i+1][0],
        'has_hyphen': '-' in word,
        'is_numeric': word.isdigit(),
        'capitals_inside': word[1:].lower() != word[1:]
    }
    return features


# extracts features for each sentence in corpus
feature_sets = []
for sentence in corpus:
    for i in range(len(sentence)):
        features = get_word_features(sentence, i)
        label = sentence[i][1]
        feature_sets.append((features, label))

# split data into training and testing sets
split = int(0.8 * len(feature_sets))
train_set = feature_sets[:split]
test_set = feature_sets[split:]

# training MaxEnt model on training data
maxent_classifier = MaxentClassifier.train(train_set, algorithm='iis', trace=0, max_iter=100)

# saves the model
with open('maxent_pos_tagger.pkl', 'wb') as file:
    pickle.dump(maxent_classifier, file)

# loads the model
with open('maxent_pos_tagger.pkl', 'rb') as file:
    maxent_classifier = pickle.load(file)

# evaluate performance
accuracy = nltk.classify.accuracy(maxent_classifier, test_set)
print(f'Accuracy: {accuracy:.4f}')


# finds nouns and adjectives in a sentence
def find_nouns_adjectives(sentence, maxent_classifier):
    features = [get_word_features([(word, '') for word in sentence], i) for i in range(len(sentence))]
    tagged_sentence = [(word, maxent_classifier.classify(f)) for word, f in zip(sentence, features)]
    nouns = [(word, tag) for word, tag in tagged_sentence if tag in ['NN', 'NNS', 'NNP', 'NNPS']]
    adjectives = [(word, tag) for word, tag in tagged_sentence if tag in ['JJ', 'JJR', 'JJS']]
    return nouns, adjectives


# example sentence
sentence = ['Bob', 'is', 'unsure', 'how', 'Anne', 'will', 'pass', 'the', 'course', 'on', 'computers', '.', 'Bob', 'is', 'sad']
nouns, adjectives = find_nouns_adjectives(sentence, maxent_classifier)
print("Nouns:", nouns)
print("Adjectives:", adjectives)
