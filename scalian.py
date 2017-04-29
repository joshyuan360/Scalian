import math
import io

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from semantics import symmetric_sentence_similarity
import path

def remove_stop_words(input_string):
    """Returns a list containing all words in input_string
    that are not stop words.
    """
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(input_string)

    result = []
    for word in words:
        if word not in stop_words:
            result.append(word)

    return result

def lemmatize_words(input_list):
    """Performs lemmatization on each word in input_array
    and returns the new list.
    """
    lemmatizer = WordNetLemmatizer()
    
    result = []
    for word in input_list:
        temp_word = lemmatizer.lemmatize(word)
        result.append(temp_word)
    
    return result

def get_original_article(composer_name, db):
    """Returns the original article about composer_name
    from the SQLite database.
    """
    cur = db.cursor()
    paragraphs = cur.execute(
        '''SELECT paragraph FROM source WHERE name=?''', 
        (composer_name,)
    ).fetchall()

    result = []
    for paragraph in paragraphs:
        result.append(paragraph[0])
    return result
    
def get_composer(user_query):
    """Returns the name of the composer that the
    user is requesting info about.
    """
    with io.open(path.PATH + 'data/load.sb', 'rU', encoding='utf-8') as file:
        file_text = file.read()
    lines = file_text.split()

    for line in lines:
        composer = line.split('-')
        for name in composer:
            if name.lower() in user_query.lower():
                return line
    
    return None

def get_relevant_sentences(input_text, db):
    """Given the user's query specified by user_query,
    returns a list of the most relevant sentences available in the database.
    Relevancy is based upon both term-frequency inverse-document-frequency
    and semantic similarity analysis. All words comparisions are processed
    after lemmatization, ignoring stop words.
    """
    cur = db.cursor()

    # lemmatize input text
    input_text = input_text.lower()
    filtered_input_text = remove_stop_words(input_text)
    lem_input_text = lemmatize_words(filtered_input_text)

    # find out which composer user is inquiring about
    composer = get_composer(input_text)
    if composer == None:
        return []

    # retrieve all data from SQLite relating to the composer
    table_row_list = cur.execute(
        '''SELECT ID, sentence, lem_sentence FROM history WHERE name=?''', 
        (composer,)
    ).fetchall()

    potential_matches = {}
    custom_stop_words = ['\'', '\'s', 's', '.', ',', ';', '(', ')', '[', ']']

    for row in table_row_list:
        sentence = row[2].lower()

        counter = 0
        for word in word_tokenize(sentence):
            if word in lem_input_text:
                # number of times <word> appears in the article about <name>
                term_frequency = cur.execute(
                    '''SELECT frequency FROM frequencies WHERE name=? AND word=?''', 
                    (composer.lower(), word)
                ).fetchone()


                if (term_frequency == None 
                        or word in composer or composer in word 
                        or word in custom_stop_words):
                    aug_term_frequency = 0
                else:
                    term_frequency = term_frequency[0]
                    aug_term_frequency = 1 + math.log(term_frequency)
                
                # number of times <word> appears in all articles
                document_frequency = cur.execute(
                    '''SELECT frequency FROM document_frequency WHERE word=?''',
                    (word,)
                ).fetchone()

                if document_frequency == None:
                    document_frequency = 0
                else:
                    document_frequency = document_frequency[0]
                inv_doc_freq = math.log(15.0 / (1 + document_frequency))

                # add the final tf-idf score
                counter += aug_term_frequency * document_frequency

        # if sentence has a non-zero tf-idf score, add to potential_matches
        if counter != 0:
            row_id = row[0]
            potential_matches[row_id] = counter

    # re-sort potential_matches based on their tf-idf score
    sorted_matches = sorted(potential_matches.items(), key=lambda x: x[1], reverse=True)

    # extract the top 20 sentences in potential_matches 
    # and re-sort based on their semantic similarity
    smart_matches = {}
    for key, value in sorted_matches:
        original_sentence = cur.execute(
            '''SELECT sentence FROM history WHERE ID=?''', 
            (key,)
        ).fetchone()[0]

        smart_matches[original_sentence] = symmetric_sentence_similarity(
            original_sentence, ' '.join(filtered_input_text)
        )
    sorted_matches = sorted(smart_matches.items(), key=lambda x: x[1], reverse=True)

    # return the top 5 sentences in smart_matches
    result = []
    for key, value in sorted_matches[:5]:
        result.append(key + ' ' + str(value))

    return result