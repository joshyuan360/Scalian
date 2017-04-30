"""Search queries processed through this script
using term-frequency inverse-document-frequency
and semantic analysis with Python's NLTK.

Joshua Yuan
"""

import math
import io

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from semantics import symmetric_sentence_similarity
import path

def remove_stop_words(input_string):
    """Stop word removal
    :param input_string: original string
    :return: list of words in input_string that are not stop words
    """
    stop_words = set(stopwords.words('english'))
    words = word_tokenize(input_string)
    result = [word for word in words if word not in stop_words]

    return result

def lemmatize_words(input_list):
    """Word lemmatization
    :param input_list: list of words
    :return: list of lemmatized words
    """
    lemmatizer = WordNetLemmatizer()
    result = [lemmatizer.lemmatize(word) for word in input_list]
    
    return result

def get_original_article(composer_name, db):
    """Returns the original article about composer_name
    from the SQLite database.
    :param composer_name: name of composer
    :param db: SQLite connection object
    :return: string containing article about composer_name
    """
    cur = db.cursor()
    paragraphs = cur.execute(
        '''SELECT paragraph FROM source WHERE name=?''', 
        (composer_name,)
    ).fetchall()

    result = [paragraph[0] for paragraph in paragraphs]
    
    return result
    
def get_composer(user_query, db):
    """Returns the name of the composer that the
    user is requesting info about.
    :param user_query: text entered in search bar
    :param db: SQLite connection object
    :return: name of composer the user is inquiring about
    """
    cur = db.cursor()
    composers = cur.execute(
        '''SELECT DISTINCT name FROM source''',
    ).fetchall()

    composers = [composer[0] for composer in composers]

    for composer in composers:
        for name in composer.split('-'):
            if name.lower() in user_query.lower():
                return composer
    
    return None

def get_tf_idf(composer, word, db):
    """Returns the term-frequency inverse-document-frequency
    of the word <word> in the article about <composer>.
    A word has a high tf_idf score if it appears frequently
    in the article about <composer> but not in other articles.
    """
    cur = db.cursor()
    # number of times <word> appears in the article about <name>
    term_frequency = cur.execute(
        '''SELECT frequency FROM frequencies WHERE name=? AND word=?''', 
        (composer.lower(), word)
    ).fetchone()

    custom_stop_words = ['\'', '\'s', 's', '.', ',', ';', '(', ')', '[', ']']

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

    return aug_term_frequency * inv_doc_freq

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
    composer = get_composer(input_text, db)
    if composer == None:
        return []

    # retrieve all data from SQLite relating to the composer
    table_row_list = cur.execute(
        '''SELECT ID, sentence, lem_sentence FROM history WHERE name=?''', 
        (composer,)
    ).fetchall()

    potential_matches = {}

    for row in table_row_list:
        sentence = row[2].lower()

        counter = 0
        for word in word_tokenize(sentence):
            if word in lem_input_text:
                tf_idf = get_tf_idf(composer, word, db)
                counter += tf_idf

        # if sentence has a non-zero tf-idf score, add to potential_matches
        if counter != 0:
            row_id = row[0]
            potential_matches[row_id] = counter

    # re-sort potential_matches based on their tf-idf score
    sorted_matches = sorted(potential_matches.items(), 
                            key=lambda x: x[1], 
                            reverse=True)

    # extract the top 20 sentences in potential_matches
    # and re-sort based on their semantic similarity
    smart_matches = {}
    for key, value in sorted_matches[:20]:
        original_sentence = cur.execute(
            '''SELECT sentence FROM history WHERE ID=?''', 
            (key,)
        ).fetchone()[0]

        smart_matches[original_sentence] = symmetric_sentence_similarity(
            original_sentence, ' '.join(filtered_input_text)
        )
    sorted_matches = sorted(smart_matches.items(), 
                            key=lambda x: x[1], 
                            reverse=True)

    # return the top 5 sentences in smart_matches
    result = []
    for key, value in sorted_matches[:5]:
        result.append(key)

    return result