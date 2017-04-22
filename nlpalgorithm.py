import nltk

from nltk.tokenize import sent_tokenize, word_tokenize, PunktSentenceTokenizer
from nltk.corpus import stopwords, state_union, wordnet
from nltk.stem import PorterStemmer, WordNetLemmatizer



#for testing only
#legal_text = "the government forces all citizens to plant trees every year"
#input_text = "every person must grow plants annually"

#filtered_legal_text = []
#filtered_input_text = []
#lemmatized_legal_text = []
#lemmatized_input_text = []

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

potential_matches = []
#part of speech tagging - NLP with Python
def get_relevant_sections(input_text):
    # !!! CHANGE FILE PATH FOR DEPLOYMENT !!!
    with open('text.sb', 'r') as myfile:
        legal_text = myfile.read().replace('\n', ' ').replace(';', '.')
    legal_text_sentences = sent_tokenize(legal_text)
    
    #temporary
    #legal_text_sentences = ["apples grow on trees.", " oranges exist on Mars"]
    #input_text = "Voters must be able to vote in any primary election"

    filtered_input_text = remove_stop_words(input_text)
    lem_input_text = lemmatize_words(filtered_input_text)
    #stem_input_text = stemmify_words(filtered_input_text)
    #print lem_input_text
    
    myList = ["Congress", "President"]

    index = 0
    for sentence in legal_text_sentences:
        filtered_sentence = remove_stop_words(sentence)
        #print filtered_sentence
        lem_sentence = lemmatize_words(filtered_sentence)
        #print lem_sentence

        counter = 0
        for word in lem_sentence:
            if word in lem_input_text:
                if word in myList:
                    counter += 1
                elif len(word) < 4:
                    counter += 3
                else:
                    counter += 10
        if counter >= 25:
            potential_matches.append(index)
        index += 1

    result = []
    for num in potential_matches:
        result.append(legal_text_sentences[num])
        #print legal_text_sentences[num]
        #print('\n')

    return result

answer = get_relevant_sections("powers not delegated to the United States by the Constitution")
for text in answer:
    print text













