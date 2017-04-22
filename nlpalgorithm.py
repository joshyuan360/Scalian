import nltk
import io
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import PorterStemmer, WordNetLemmatizer

#for testing only
#legal_text = "the government forces all citizens to plant trees every year"
#input_text = "every person must grow plants annually"

#filtered_legal_text = []
#filtered_input_text = []
#lemmatized_legal_text = []
#lemmatized_input_text = []
DEPLOY = '/var/www/ScaliaBot/ScaliaBot/data/'
DEPLOY = 'data/'
# begin removal of all stop words
def remove_stop_words(input_string):
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(input_string)

    temp = []
    for w in words:
        if w not in stop_words:
            temp.append(w)

    return temp

#filtered_legal_text = remove_stop_words(legal_text)
#filtered_input_text = remove_stop_words(input_text)
# end removal of all stop words

# begin lemmatization of all words
def lemmatize_words(input_array):
    lemmatizer = WordNetLemmatizer()
    
    temp = []
    for word in input_array:
        temp_word = lemmatizer.lemmatize(word)
        temp.append(temp_word)
    
    return temp

#lemmatized_legal_text = lemmatize_words(filtered_legal_text)
#lemmatized_input_text = lemmatize_words(filtered_input_text)
# end lemmatization of all words

def stemmify_words(input_array):
    ps = PorterStemmer()

    temp = []
    for word in input_array:
        temp_word = ps.stem(word)
        temp.append(temp_word)
    
    return temp

# returns true if the sentences contain at least 3 similar words
def numerical_similarity():
    score = 0.0
    for word1 in lemmatized_legal_text:
        w1 = wordnet.synsets(word1)
        for word2 in lemmatized_input_text:
            w2 = wordnet.synsets(word2)
            if w1 and w2:
                sm = w1[0].wup_similarity(w2[0])
                if sm > 0.5:
                    score += sm
                    #print w1[0].lemmas()[0].name(), w2[0].lemmas()[0].name()
                    #print(w1[0].wup_similarity(w2[0]))

    return score

def sentence_file():
    with io.open(DEPLOY + 'law.sb', 'rU', encoding='utf-8') as myfile:
        file_text = myfile.read()

    file_text_sentences = sent_tokenize(file_text)
    text_file = open(DEPLOY + "sentence_law.sb", "w")
    
    index = 0
    removeLeftSpace = [')', ',', '.', ';', ':']
    removeRightSpace = ['(']
    for sentence in file_text_sentences:
        words = word_tokenize(sentence)
        new_string = ' '.join(words) + '\n'

        for char in removeLeftSpace:
            new_string = new_string.replace(' ' + char, char)
        for char in removeRightSpace:
            new_string = new_string.replace(char + ' ', char)

        #new_string = new_string.replace('( ', '(').replace(' )', ')').replace(' ,', ',').replace(' .', '.').replace(' ;', ';')

        text_file.write(new_string.encode('utf-8') + '\n')
        
        index += 1


    text_file.close()


def lem_file():
    with io.open(DEPLOY + 'law.sb', 'rU', encoding='utf-8') as myfile:
        file_text = myfile.read()

    file_text_sentences = sent_tokenize(file_text)
    text_file = open(DEPLOY + "lem_law.sb", "w")
    
    index = 0
    for sentence in file_text_sentences:
        filtered_sentence = remove_stop_words(sentence)
        lem_sentence = lemmatize_words(filtered_sentence)
        new_string = ' '.join(lem_sentence) + '\n'
        if index < 3:
            print new_string
        text_file.write(new_string.encode('utf-8') + '\n')    
        index += 1
    text_file.close()

potential_matches = {}
#part of speech tagging - NLP with Python
def get_relevant_sections(input_text):
    # !!! CHANGE FILE PATH FOR DEPLOYMENT !!!
    with io.open(DEPLOY + 'lem_law.sb', 'rU', encoding='utf-8') as myfile:
        legal_text = myfile.read()
    #legal_text = legal_text.replace(';', '.')
    legal_text_sentences = legal_text.splitlines()
    #print legal_text_sentences 
    #temporary
    #legal_text_sentences = ["apples grow on trees.", " oranges exist on Mars"]
    #input_text = "Voters must be able to vote in any primary election"
    input_text = input_text.lower()
    filtered_input_text = remove_stop_words(input_text)
    lem_input_text = lemmatize_words(filtered_input_text)
    #stem_input_text = stemmify_words(filtered_input_text)
    #print lem_input_text
    
    myList = ["congress", "president", "shall"]
    print lem_input_text
    index = 0
    for sentence in legal_text_sentences:
        sentence = sentence.lower()
        #filtered_sentence = remove_stop_words(sentence)
        #print filtered_sentence
        #lem_sentence = lemmatize_words(filtered_sentence)
        #print lem_sentence

        counter = 0

        for word in lem_input_text:
            if word in sentence:
                counter += sentence.count(word)

        if counter != 0:
            potential_matches[index] = counter
        index += 1

    sorted_matches = sorted(potential_matches.items(), key=lambda x: x[1], reverse=True)
    with io.open(DEPLOY + 'sentence_law.sb', 'rU', encoding='utf-8') as myfile:
       original_text = myfile.read()
    original_text_sentences = original_text.splitlines()

    result = []
    for key, value in sorted_matches[:3]:
        result.append(original_text_sentences[key])
        #print legal_text_sentences[num]
        #print('\n')

    return result

