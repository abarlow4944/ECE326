# ECE326 Lab 1

## Front-End
The code for the front-end is in a file called `index.tpl`, which is located in the `views` directory. To run the server, run `python app.py`

## Back-End
Refer to `crawler.py` for back-end starter code, `test_crawler.py` for unit tests.

The following data structures were made in `crawler.py`:
* **self._doc_index:** This data structure is a dictionary where the key is a document index, and the value is a dictionary that holds the corresponding URL, title, and description (first three lines of text in the page).
  * __{doc_id: {"url": url, "title": title, "description": first 3 lines (desc)}}__
* **self._lexicon:** This data structure is a dictionary where the key is a word id and the value is the corresponding word.
  * __{word_id: word}__
* **self._inverted_index:** This data structure is a dictionary where the key is a word id and the value is a set of document ids that the word can be found in.
  * __{word_id: set(doc_ids)}__
 
These data structures are populated in the `crawl()` function. The lexicon data structure is populated in the `word_id()` function, which is indirectly called by `crawl()`. You can find the new code that was added to the `crawler.py` starter code by looking for the `# **NEW** ADDITIONS` comments.

Two functions were also added to the file:
* __get_inverted_index():__ This is a getter function that returns the `inverted index` data structure.
* __get_resolved_inverted_index():__ This function returns a human-readable version of `inverted index` by returning a dictionary where the key is a word, and the value is a set of URLs that represent pages that the word can be found in.
  * __key: word, value: set of urls__

Test cases can be found in the `test_crawler.py` file:
* __setUp:__ This is called before every test and it creates a new crawler object each time to isolate the tests
* __test_crawl_example_com:__ This runs crawler on a single page, www.example.com. It checks to make sure that `doc_index`, `lexicon`, and `inverted_index` are populated properly by checking that everything corresponds to the correct doc_id and that the URL/title/description/words are extracted correctly from the page.
 __test_get_inverted_index_returns_correct_structure:__ This verifies that the `get_inverted_index()` function correctly returns the crawler’s internal inverted index structure. It checks that the output is a dictionary and that its content matches the crawler’s stored data.  
* __test_get_resolved_inverted_index_translates_ids:__ This ensures that `get_resolved_inverted_index()` correctly converts word IDs and document IDs into human-readable words and URLs. It confirms that each word maps to the set of URLs where it appears.  
* __test_get_resolved_inverted_index_multiple_docs:__ This tests that `get_resolved_inverted_index()` correctly handles multiple documents. It ensures that words appearing in multiple pages map to multiple URLs, and words appearing in only one page map to a single URL.  
* __test_crawl_handles_no_urls:__ This ensures that the crawler behaves correctly when given an empty URL file. It verifies that `doc_index`, `lexicon`, and `inverted_index` remain empty and that the program does not crash or raise an error.  
To run the test cases, run `python -m unittest test_crawler.py`
