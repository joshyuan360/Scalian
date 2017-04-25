import io, sqlite3
from nltk.tokenize import sent_tokenize, word_tokenize
from nlpalgorithm import remove_stop_words, lemmatize_words

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """

    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None

def create_biography(conn, biography):
    """
    Create a new biography into the history table
    :param conn:
    :param biography:
    :return: biography id
    """
    sql = ''' INSERT INTO history(name,sentence,lem_sentence)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, biography)
    return cur.lastrowid

def generate_columns(FILE_PATH, conn, composer_name):
	with io.open(FILE_PATH, 'rU', encoding='utf-8') as file:
		file_text = file.read()
	file_text_sentences = sent_tokenize(file_text)

	for sentence in file_text_sentences:
		filtered_sentence = remove_stop_words(sentence)
		lem_sentence_array = lemmatize_words(filtered_sentence)
		lem_sentence = ' '.join(lem_sentence_array)

		row = (composer_name, sentence, lem_sentence);
		create_biography(conn, row)

def generate_frequencies(conn, composer_name):
    cur = conn.cursor()
    lem_sentence_list = cur.execute('SELECT lem_sentence FROM history WHERE name=?', (composer_name,)).fetchall()

    for sequence in lem_sentence_list:
        sentence = sequence[0].lower()
        for word in word_tokenize(sentence):
            freq_sequence = cur.execute('SELECT frequency FROM frequencies WHERE name=? AND word=?', (composer_name, word)).fetchone()
            if freq_sequence == None:
                cur.execute('INSERT INTO frequencies(name, word, frequency) VALUES(?,?,?)',
                            (composer_name, word, 1))
            else:
                freq = freq_sequence[0] + 1
                cur.execute('''UPDATE frequencies 
                            SET frequency=? WHERE name=? AND word=?''', (freq, composer_name, word))

def generate_doc_frequencies(conn):
    cur = conn.cursor()
    all_words_list = cur.execute('SELECT word, frequency FROM frequencies').fetchall()
    for sequence in all_words_list:
        word = sequence[0]
        frequency = sequence[1]
        doc_freq_seq = cur.execute('SELECT frequency FROM document_frequency WHERE word=?', (word,)).fetchone()
        if doc_freq_seq == None:
            cur.execute('INSERT INTO document_frequency(word, frequency) VALUES(?,?)',
                         (word, 1))
        else:
            freq = doc_freq_seq[0] + 1
            cur.execute('''UPDATE document_frequency
                           SET frequency=? WHERE word=?''', (freq, word))

def process_file(BIO_PATH, composer_name):
    conn = create_connection('sqlite/history.db')
    with conn:
        generate_columns(BIO_PATH, conn, composer_name)

def process_frequencies(composer_name):
    conn = create_connection('sqlite/history.db')
    with conn:
        generate_frequencies(conn, composer_name)

def process_doc_frequencies():
    conn = create_connection('sqlite/history.db')
    with conn:
        generate_doc_frequencies(conn)

composers = ['bach', 'beethoven', 'brahms', 'chopin', 
             'debussy', 'handel', 'haydn', 'liszt',
             'mahler', 'mozart', 'schubert', 'stravinsky',
             'tchaikovsky', 'verdi', 'wagner']

#for composer in composers:
    #BIO_PATH = 'data/' + composer + '.sb'
    #process_file(BIO_PATH, composer)
    #process_frequencies(composer)
    
process_doc_frequencies()











