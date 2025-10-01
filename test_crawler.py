import unittest
from crawler import crawler

# python -m unittest test_crawler.py

class TestCrawler(unittest.TestCase):
    def setUp(self):
        # urls.txt can be empty for these tests
        self.bot = crawler(None, "urls.txt")

    def test_word_id(self):
        word_id1 = self.bot.word_id("hello")
        word_id2 = self.bot.word_id("hello")

        self.assertEqual(word_id1, word_id2)
        self.assertEqual(self.bot._lexicon[word_id1], "hello")

    def test_document_id(self):
        doc_id1 = self.bot.document_id("http://google.ca")
        doc_id2 = self.bot.document_id("http://google.ca")
        doc_id3 = self.bot.document_id("http://bing.ca")

        self.assertEqual(doc_id1, doc_id2)
        self.assertEqual(len(self.bot._doc_index), 2)
