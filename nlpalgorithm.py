import nltk, io, similarity
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords, wordnet
from nltk.stem import PorterStemmer, WordNetLemmatizer

def remove_stop_words(input_string):
    stop_words = set(stopwords.words("english"))
    words = word_tokenize(input_string)

    temp = []
    for w in words:
        if w not in stop_words:
            temp.append(w)

    return temp

def lemmatize_words(input_array):
    lemmatizer = WordNetLemmatizer()
    
    temp = []
    for word in input_array:
        temp_word = lemmatizer.lemmatize(word)
        temp.append(temp_word)
    
    return temp


potential_matches = {}

def get_relevant_sections(input_text, db):
    cur = db.cursor()

    #lemmatize the input text
    input_text = input_text.lower()
    filtered_input_text = remove_stop_words(input_text)
    lem_input_text = lemmatize_words(filtered_input_text)

    #custom stop words
    myList = ["congress", "president", "shall"]
    table_rows = cur.execute('SELECT ID, sentence, lem_sentence FROM history WHERE name=?', ('Mozart',))
    table_row_list = cur.fetchall()

    for row in table_row_list:
        sentence = row[2].lower()

        counter = 0
        for word in sentence.split():
            if word in lem_input_text:
                counter += 1

        if counter != 0:
            row_id = row[0]
            potential_matches[row_id] = counter

    sorted_matches = sorted(potential_matches.items(), key=lambda x: x[1], reverse=True)

    smart_matches = {}
    for key, value in sorted_matches[:20]:
        original_sentence = table_row_list[key][2]
        smart_matches[key] = similarity.symmetric_sentence_similarity(original_sentence, " ".join(filtered_input_text))
    
    sorted_matches = sorted(smart_matches.items(), key=lambda x: x[1], reverse=True)

    result = []
    for key, value in sorted_matches[:5]:
        result.append(table_row_list[key][1] + " " + str(value))


    return result
