"""Script loads content into the SQLite database,
preprocessing raw text for faster search results.

Joshua Yuan
"""

import io

import sqlite3
from nltk.tokenize import sent_tokenize, word_tokenize

from scalian import remove_stop_words, lemmatize_words

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None

def load_history_table(conn, composer_name):
    cur = conn.cursor()

    with io.open('data/' + composer_name + '.sb', 'rU', encoding='utf-8') as file:
        file_text = file.read()
    file_text_sentences = sent_tokenize(file_text)

    for sentence in file_text_sentences:
        filtered_sentence = remove_stop_words(sentence)
        lem_sentence_array = lemmatize_words(filtered_sentence)
        lem_sentence = ' '.join(lem_sentence_array)

        cur.execute(
            '''INSERT INTO history(name,sentence,lem_sentence)
               VALUES(?,?,?)''', 
            (composer_name, sentence, lem_sentence)
        )

def load_source_table(conn, composer_name):
    cur = conn.cursor()

    with io.open('data/' + composer_name + '.sb', 'rU', encoding='utf-8') as file:
        file_text = file.read()
    file_text_paragraphs = file_text.split('\n')
    
    for paragraph in file_text_paragraphs:
        cur.execute(
            '''INSERT INTO source(name, paragraph)
               VALUES(?,?)''', 
            (composer_name, paragraph)
        )

def load_frequency_table(conn, composer_name):
    cur = conn.cursor()

    lem_sentence_list = cur.execute(
        '''SELECT lem_sentence FROM history 
           WHERE name=?''', 
        (composer_name,)
    ).fetchall()

    for sequence in lem_sentence_list:
        sentence = sequence[0].lower()
        for word in word_tokenize(sentence):
            freq_sequence = cur.execute(
                '''SELECT frequency FROM frequencies 
                   WHERE name=? AND word=?''', 
                (composer_name, word)
            ).fetchone()

            if freq_sequence == None:
                cur.execute(
                    '''INSERT INTO frequencies(name, word, frequency) 
                       VALUES(?,?,?)''',
                    (composer_name, word, 1)
                )
            else:
                freq = freq_sequence[0] + 1
                cur.execute(
                    '''UPDATE frequencies 
                       SET frequency=? WHERE name=? AND word=?''', 
                    (freq, composer_name, word)
                )

def load_doc_frequencies_table(conn):
    cur = conn.cursor()
    
    all_words_list = cur.execute(
        '''SELECT word, frequency FROM frequencies'''
    ).fetchall()
    
    for sequence in all_words_list:
        word = sequence[0]
        frequency = sequence[1]
        doc_freq_seq = cur.execute(
            '''SELECT frequency FROM document_frequency 
               WHERE word=?''', 
            (word,)
        ).fetchone()
        
        if doc_freq_seq == None:
            cur.execute(
                '''INSERT INTO document_frequency(word, frequency) 
                   VALUES(?,?)''',
                (word, 1)
            )
        else:
            freq = doc_freq_seq[0] + 1
            cur.execute(
                '''UPDATE document_frequency 
                   SET frequency=? WHERE word=?''', 
                (freq, word)
            )

if __name__ == '__main__':
    with io.open('data/load.sb', 'rU', encoding='utf-8') as file:
       file_text = file.read()
    file_names = file_text.split()

    conn = create_connection('sqlite/history.db')
    with conn:
        for name in file_names:
            load_history_table(conn, name)
        for name in file_names:
            load_source_table(conn, name)
        for name in file_names:
            load_frequency_table(conn, name)
        load_doc_frequencies_table(conn)