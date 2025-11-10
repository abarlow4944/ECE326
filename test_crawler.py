import unittest
from crawler import crawler
from bs4 import BeautifulSoup, Tag
import requests

# python -m unittest test_crawler.py

class TestCrawler(unittest.TestCase):
    def setUp(self):
        self.bot = crawler(None, "urls.txt")

    def assert_db_populated(self):
        import sqlite3
        conn = sqlite3.connect("search_engine.db")
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM doc_index;")
        doc_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM inverted_index;")
        link_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM page_rank;")
        rank_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM lexicon;")
        lex_count = cursor.fetchone()[0]

        conn.close()

        self.assertGreater(doc_count, 0, "pages table should not be empty after crawl")
        self.assertGreater(link_count, 0, "links table should not be empty after crawl")
        self.assertGreater(rank_count, 0, "pagerank table should not be empty after crawl")
        self.assertGreater(lex_count, 0, "lexicon table should not be empty after crawl")

    # Lab 3 unit tests
    def display_persistant_data(self):
        print("Doc Index:", self.bot._doc_index)
        print("Lexicon:", self.bot._lexicon)
        print("Inverted Index:", self.bot.get_inverted_index())
        print("Inverted Index:", self.bot.get_resolved_inverted_index())
        print("links:", self.bot.get_links())

    #we implemented basic test to assert that data was actually stored which is the key functionality of lab 3
    def test_crawl_eecg_utoronto_ca(self):
        #use http://www.eecg.toronto.edu/ as test site to depth of 1
        with open("urls.txt", "w") as f:
            f.write("https://www.eecg.toronto.edu/\n")

        #crawl one level deep
        self.bot.crawl(depth=1) 
        self.bot.compute_page_rank()
        self.bot.store_to_database()
        self.assert_db_populated()

    def test_page_rank_mutual_link(self):
        # simulate minimal state
        self.bot._links = {
            0: {1},
            1: {0}
        }
        self.bot._doc_index = {0: "", 1: ""}

        self.bot.compute_page_rank()

        result = self.bot._page_rank

        # structure checks
        self.assertIsInstance(result, dict, "Expected dict page_rank output")
        self.assertEqual(set(result.keys()), {0, 1}, "Expected page rank keys 0 and 1")

        # rank expectations (should be roughly equal for mutual link)
        pr0 = result[0]
        pr1 = result[1]

        # difference threshold relaxed because converges approx, not exact equality
        self.assertAlmostEqual(pr0, pr1, delta=0.05, msg="Mutual links should converge to equal PR values")

    def test_page_rank_dangling_node(self):
        # simulate minimal state with a dangling node
        self.bot._links = {
            0: {1},
            1: set()  # dangling node
        }
        self.bot._doc_index = {0: "", 1: ""}

        self.bot.compute_page_rank()

        result = self.bot._page_rank

        # structure checks
        self.assertIsInstance(result, dict, "Expected dict page_rank output")
        self.assertEqual(set(result.keys()), {0, 1}, "Expected page rank keys 0 and 1")

        pr0 = result[0]
        pr1 = result[1]

        # Check that ranks are reasonable (not zero or negative)
        self.assertGreater(pr0, 0, "Page rank for node 0 should be greater than 0")
        self.assertGreater(pr1, 0, "Page rank for dangling node 1 should be greater than 0")
        self.assertGreater(pr1, pr0, "Dangling node should have higher page rank due to redistribution")

    def test_page_rank_no_links(self):
        # simulate minimal state with no links
        self.bot._links = {
            0: set(),
            1: set()
        }
        self.bot._doc_index = {0: "", 1: ""}

        self.bot.compute_page_rank()

        result = self.bot._page_rank

        # structure checks
        self.assertIsInstance(result, dict, "Expected dict page_rank output")
        self.assertEqual(set(result.keys()), {0, 1}, "Expected page rank keys 0 and 1")

        pr0 = result[0]
        pr1 = result[1]

        # Check that ranks are equal due to no links
        self.assertAlmostEqual(pr0, pr1, delta=0.01, msg="With no links, page ranks should be equal")

    def test_page_rank_single_node(self):
        # simulate minimal state with a single node
        self.bot._links = {
            0: set()
        }
        self.bot._doc_index = {0: ""}

        self.bot.compute_page_rank()

        result = self.bot._page_rank

        # structure checks
        self.assertIsInstance(result, dict, "Expected dict page_rank output")
        self.assertEqual(set(result.keys()), {0}, "Expected page rank key 0")

        pr0 = result[0]

        # Check that rank is 1.0 for single node
        self.assertAlmostEqual(pr0, 1.0, delta=0.01, msg="Single node should have page rank of 1.0")

    def test_page_rank_three_node_cycle(self):
        # simulate minimal state with a three-node cycle
        self.bot._links = {
            0: {1},
            1: {2},
            2: {0}
        }
        self.bot._doc_index = {0: "", 1: "", 2: ""}

        self.bot.compute_page_rank()

        result = self.bot._page_rank

        # structure checks
        self.assertIsInstance(result, dict, "Expected dict page_rank output")
        self.assertEqual(set(result.keys()), {0, 1, 2}, "Expected page rank keys 0, 1, and 2")

        pr0 = result[0]
        pr1 = result[1]
        pr2 = result[2]

        # Check that ranks are roughly equal due to cycle
        self.assertAlmostEqual(pr0, pr1, delta=0.02, msg="Node 0 and 1 should have roughly equal PR values")
        self.assertAlmostEqual(pr1, pr2, delta=0.02, msg="Node 1 and 2 should have roughly equal PR values")
        self.assertAlmostEqual(pr0, pr2, delta=0.02, msg="Node 0 and 2 should have roughly equal PR values")

    def test_page_rank_four_node_chain(self):
        # simulate minimal state with a four-node chain
        self.bot._links = {
            0: {1},
            1: {2},
            2: {3},
            3: set()
        }
        self.bot._doc_index = {0: "", 1: "", 2: "", 3: ""}

        self.bot.compute_page_rank()

        result = self.bot._page_rank

        # structure checks
        self.assertIsInstance(result, dict, "Expected dict page_rank output")
        self.assertEqual(set(result.keys()), {0, 1, 2, 3}, "Expected page rank keys 0, 1, 2, and 3")

        pr0 = result[0]
        pr1 = result[1]
        pr2 = result[2]
        pr3 = result[3]

        # Check that ranks decrease along the chain
        self.assertGreater(pr1, pr0, "Node 1 should have higher PR than Node 0")
        self.assertGreater(pr2, pr1, "Node 2 should have higher PR than Node 1")
        self.assertGreater(pr3, pr2, "Node 3 should have higher PR than Node 2")

    ## Lab 1+2 unit tests
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

