import unittest
from crawler import crawler
from bs4 import BeautifulSoup, Tag
import requests

# python -m unittest test_crawler.py
# make a unit test for crawl and the two functions we made (get_resolved_inverted_index and get_inverted_index )

class TestCrawler(unittest.TestCase):
    def setUp(self):
        self.bot = crawler(None, "urls.txt")

    def display_persistant_data(self):
        print("Doc Index:", self.bot._doc_index)
        print("Lexicon:", self.bot._lexicon)
        print("Inverted Index:", self.bot.get_inverted_index())
        print("Inverted Index:", self.bot.get_resolved_inverted_index())
        print("links:", self.bot.get_links())
    def test_crawl_eecg_utoronto_ca(self):
        #use http://www.eecg.toronto.edu/ as test site to dept of 1
        with open("urls.txt", "w") as f:
            f.write("https://www.eecg.toronto.edu/\n")

        #crawl one level deep
        self.bot.crawl(depth=1) 
        self.display_persistant_data()
        self.bot.compute_page_rank()
        self.bot.store_to_database()
    '''
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

        # check that the doc_ids in inverted_index are correct
        for word_id, doc_ids in self.bot._inverted_index.items():
            self.assertIn(1, doc_ids, "Correct doc_id not given from word_id")
        self.display_persistant_data()

    def test_get_inverted_index_returns_correct_structure(self):
        # simulate minimal state
        self.bot._inverted_index = {1: {1, 2}, 2: {1}}
        result = self.bot.get_inverted_index()
        self.assertIsInstance(result, dict, "Expected dict output")
        self.assertEqual(result, {1: {1, 2}, 2: {1}}, "Returned index mismatch")

    def test_get_resolved_inverted_index_translates_ids(self):
        # Fake data
        self.bot._lexicon = {1: "example", 2: "domain"}
        self.bot._doc_index = {1: {"url": "https://example.com/"}}
        self.bot._inverted_index = {1: {1}, 2: {1}}

        resolved = self.bot.get_resolved_inverted_index()
        self.assertIn("example", resolved, "Missing resolved key")
        self.assertEqual(resolved["example"], {"https://example.com/"})
        self.assertIn("domain", resolved)
        self.assertEqual(resolved["domain"], {"https://example.com/"})

    def test_get_resolved_inverted_index_multiple_docs(self):
        self.bot._lexicon = {1: "example", 2: "domain"}
        self.bot._doc_index = {
            1: {"url": "https://example.com/"},
            2: {"url": "https://another.com/"}
        }
        self.bot._inverted_index = {
            1: {1, 2},  # "example" appears in both
            2: {1}      # "domain" only in doc 1
        }

        resolved = self.bot.get_resolved_inverted_index()
        self.assertEqual(
            resolved["example"],
            {"https://example.com/", "https://another.com/"},
            "Word 'example' should resolve to both URLs"
        )
        self.assertEqual(
            resolved["domain"],
            {"https://example.com/"},
            "Word 'domain' should only resolve to first URL"
        )

    def test_crawl_handles_no_urls(self):
        
        with open("empty.txt", "w") as f:

            f.write("")
        self.bot = crawler(None, "empty.txt")
        self.bot.crawl(depth=0)
        self.assertEqual(len(self.bot._doc_index), 0, "doc_index should be empty")
        self.assertEqual(len(self.bot._lexicon), 0, "lexicon should be empty")
        self.assertEqual(len(self.bot._inverted_index), 0, "inverted_index should be empty")
    '''



if __name__ == "__main__":
    unittest.main()

