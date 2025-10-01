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

        # Act: crawl one level deep
        self.bot.crawl(depth=0)

        # Assert: document index contains the page
        doc_id = 1
        self.assertEqual(self.bot._doc_index[doc_id]["url"], 'https://example.com/')
        self.assertEqual(self.bot._doc_index[doc_id]["title"], "Example Domain")
        self.assertEqual(len(self.bot._doc_index[doc_id]["description"]), 3)


       

if __name__ == "__main__":
    unittest.main()

