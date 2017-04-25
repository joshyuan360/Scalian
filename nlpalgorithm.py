import nltk, similarity, math
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

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

def get_composer(input_text):
    composers = ['bach', 'beethoven', 'brahms', 'chopin', 
             'debussy', 'handel', 'haydn', 'liszt',
             'mahler', 'mozart', 'schubert', 'stravinsky',
             'tchaikovsky', 'verdi', 'wagner']

    for composer in composers:
        if composer.lower() in input_text.lower():
            return composer.lower()
    
    return None

def get_relevant_sections(input_text, db):
    cur = db.cursor()

    #lemmatize the input text
    input_text = input_text.lower()
    filtered_input_text = remove_stop_words(input_text)
    lem_input_text = lemmatize_words(filtered_input_text)

    #get composer in question
    composer = get_composer(input_text)
    if composer == None:
        return []

    custom_stop_words = ['\'', '\'s', 's', '.', ',', ';']

    #find all lem_sentences in SQLite that contain at least one word that also exists in the lemmatized input
    table_rows = cur.execute('SELECT ID, sentence, lem_sentence FROM history WHERE name=?', (composer,))
    table_row_list = cur.fetchall()
    for row in table_row_list:
        sentence = row[2].lower()

        counter = 0
        for word in word_tokenize(sentence):
            if word in lem_input_text:
                term_frequency = cur.execute('''SELECT frequency FROM frequencies
                                                WHERE name=? AND word=?''', (composer.lower(), word)).fetchone()
                if term_frequency == None or word in composer or composer in word or word in custom_stop_words:
                    aug_term_frequency = 0
                else:
                    term_frequency = term_frequency[0]
                    aug_term_frequency = 1 + math.log(term_frequency)
                
                counter += aug_term_frequency

        if counter != 0:
            row_id = row[0]
            potential_matches[row_id] = counter
    sorted_matches = sorted(potential_matches.items(), key=lambda x: x[1], reverse=True)

    #re-sort the top 20 matches based on their semantic similarity
    smart_matches = {}
    for key, value in sorted_matches[:20]:
        original_sentence = cur.execute('SELECT sentence FROM history WHERE ID=?', (key,)).fetchone()[0]
        smart_matches[original_sentence] = similarity.symmetric_sentence_similarity(original_sentence, " ".join(filtered_input_text))
    
    sorted_matches = sorted(smart_matches.items(), key=lambda x: x[1], reverse=True)

    #return the top 5 "smart matches"
    result = []
    for key, value in sorted_matches[:5]:
        result.append(key + " " + str(value))


    return result
