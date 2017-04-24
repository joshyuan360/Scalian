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

def generate_columns(FILE_PATH, conn):
	with io.open(FILE_PATH, 'rU', encoding='utf-8') as file:
		file_text = file.read()
	file_text_sentences = sent_tokenize(file_text)

	for sentence in file_text_sentences:
		filtered_sentence = remove_stop_words(sentence)
		lem_sentence_array = lemmatize_words(filtered_sentence)
		lem_sentence = ' '.join(lem_sentence_array)

		row = ('Mozart', sentence, lem_sentence);
		create_biography(conn, row)

def process_file(BIO_PATH):
	conn = create_connection('sqlite/history.db')
	with conn:
		generate_columns(BIO_PATH, conn)

if __name__ == '__main__':
	BIO_PATH = 'data/mozart.sb'
	process_file(BIO_PATH)