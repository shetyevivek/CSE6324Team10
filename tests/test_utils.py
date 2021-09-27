import os

from ln2sql.parser import Parser
from ln2sql.stopwordFilter import StopwordFilter

BASE_PATH = os.path.dirname(os.path.dirname(__file__))  # Project directory.
STOPWORDS_PATH = os.path.join(BASE_PATH, 'ln2sql/stopwords/')


def test_parser_sort_length():
    input_list = ['len2 len2', 'len1', 'len3 len3 len3']
    expected = ['len3 len3 len3', 'len2 len2', 'len1']
    assert Parser.transformation_sort(input_list) == expected

def test_parser_sort_length_lexical():
    input_list = ['len2 len2', 'len1', 'len3 len3 len3', 'alen3 alen3 alen3']
    expected = ['alen3 alen3 alen3', 'len3 len3 len3', 'len2 len2', 'len1']
    assert Parser.transformation_sort(input_list) == expected

def test_english_stopword_filter():
    stopwordFilter = StopwordFilter()
    stopwordFilter.load(STOPWORDS_PATH + 'english.txt')
    input_sentence = 'The cat drinks milk when the dog enter in the room and his master look the TV of the hostel'
    expected = 'cat drinks milk dog enter room master tv hostel'
    assert stopwordFilter.filter(input_sentence) == expected

def test_french_stopword_filter():
    stopwordFilter = StopwordFilter()
    stopwordFilter.load(STOPWORDS_PATH + 'french.txt')
    input_sentence = "Le chat boit du lait au moment où le chien rentre dans la maison et que son maître regarde la TV de l'hôtel"
    expected = 'chat boit lait chien rentre maison maitre regarde tv hotel'
    assert stopwordFilter.filter(input_sentence) == expected