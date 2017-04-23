import io
from nltk.tokenize import sent_tokenize, word_tokenize
from nlpalgorithm import remove_stop_words, lemmatize_words
DEPLOY = "data/"

FILE_NAME = "mozart.sb"

def sentence_file():
    with io.open(DEPLOY + FILE_NAME, 'rU', encoding='utf-8') as myfile:
        file_text = myfile.read()

    file_text_sentences = sent_tokenize(file_text)
    text_file = open(DEPLOY + "sentence_" + FILE_NAME, "w")
    
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
    with io.open(DEPLOY + FILE_NAME, 'rU', encoding='utf-8') as myfile:
        file_text = myfile.read()

    file_text_sentences = sent_tokenize(file_text)
    text_file = open(DEPLOY + "lem_" + FILE_NAME, "w")
    
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


FILE_NAME = "mozart.sb"
sentence_file()
lem_file()




