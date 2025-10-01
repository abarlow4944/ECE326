import unittest
from crawler import crawler
from bs4 import BeautifulSoup, Tag
import requests

# python -m unittest test_crawler.py
# make a unit test for crawl and the two functions we made (get_resolved_inverted_index and get_inverted_index )

class TestCrawler(unittest.TestCase):
    def setUp(self):
        # urls.txt can be empty for these tests
        self.bot = crawler(None, "urls.txt")

    def test_crawl_example_com(self):
        # use www.example.com as example
        with open("urls.txt", "w") as f:
            f.write("https://example.com/\n")

        # crawl one level deep
        self.bot.crawl(depth=0)

        # check doc_index
        doc_id = 1
        self.assertEqual(self.bot._doc_index[doc_id]["url"], 'https://example.com/', "doc_index does not have the correct URL")
        self.assertEqual(self.bot._doc_index[doc_id]["title"], "Example Domain", "doc_index does not have the correct title")
        self.assertEqual(len(self.bot._doc_index[doc_id]["description"]), 3, "doc_index does not have three lines")

        # check lexicon
        self.assertGreater(len(self.bot._lexicon), 0, "lexicon should not be empty")
        
        # check inverted_index
        self.assertGreater(len(self.bot._inverted_index), 0, "inverted_index should not be empty")

        for word_id, doc_ids in self.bot._inverted_index.items():
            self.assertIn(1, doc_ids, "Correct doc_id not given from word_id")

    # def test_get_resolved_inverted_index:

    #def test_get_inverted_index:



       

if __name__ == "__main__":
    unittest.main()

