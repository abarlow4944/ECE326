import sqlite3
import os

from difflib import SequenceMatcher
import sqlite3
from difflib import SequenceMatcher

DB_PATH = os.path.join(os.path.dirname(__file__), 'search_engine.db')
#module-level cache dictionaries
_fuzzy_cache = {}
_lexicon = {}
_lexicon_dict = {}
_match_cache = {}
_search_cache = {}
def load_lexicon():
    """Load all entries from the 'lexicon' table in the configured SQLite database.

    Opens a connection to the SQLite database referenced by DB_PATH, sets the
    connection's row factory to sqlite3.Row, and executes a SELECT query to
    retrieve the `word_id` and `word` columns from the `lexicon` table. The
    database connection is closed before returning.

    Returns:
        list[sqlite3.Row]: A list of sqlite3.Row objects (can be accessed by key
        or index). Each row contains the keys 'word_id' and 'word'.

    Raises:
        sqlite3.Error: If an error occurs while connecting to the database or
        executing the query.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT word_id, word FROM lexicon")
    rows = cur.fetchall()
    conn.close()
    return rows

_lexicon = load_lexicon()#load lexicon at module load time

def load_lexicon_dictionary(): 
    """Load the lexicon into a dictionary for faster access."""
    lex_dict = {}
    for row in _lexicon:
        lex_dict[row["word"].lower()] = row
    return lex_dict
_lexicon_dict = load_lexicon_dictionary()

def fuzzy_ratio(a, b):
    """
    Calculate fuzzy string similarity ratio between two strings using SequenceMatcher.
    Results are cached in a dictionary to avoid redundant comparisons.
    
    Args:
        a (str): First string to compare
        b (str): Second string to compare
    
    Returns:
        float: Similarity score between 0 and 1
    """
    
    # Create cache key
    key = (a.lower(), b.lower())
    
    # Check cache first
    if key in _fuzzy_cache:
        return _fuzzy_cache[key]

    # Compute similarity score
    score = SequenceMatcher(None, key[0], key[1]).ratio()
    _fuzzy_cache[key] = score
    return score

'''
def apply_adaptive_threshold(matches):
    """
    Apply an adaptive threshold to a list of matches based on their count.

    Args:
        matches (list): List of match dictionaries with 'score' keys

    Returns:
        list: Filtered list of matches above the adaptive threshold
    """
    count = len(matches)

    if count > 2000:
        threshold = 0.9
    elif count > 500:
        threshold = 0.80
    elif count > 100:
        threshold = 0.75
    else:
        threshold = 0.50

    return [m for m in matches if m["score"] >= threshold]
'''

def lexicon_fuzzy_match(word, base_threshold=0.3):
    """
    Perform matching of the word against the lexicon. if a direct match is found, return only that.
    Otherwise, perform fuzzy matching against all lexicon entries and return the top 5 above threshold.
    uses caching to speed up repeated queries.
    Args:
        word (str): Input word to match (should be lowercased  before calling)
        base_threshold (float): Minimum score threshold for matches
        Returns:
        list: List of match dictionaries with 'word_id', 'word', and 'score' keys
        
    Performance considerations:
    - Exact match is done first for speed this is O(1) with a dict lookup
    - Fuzzy matching is O(N) over the lexicon, but optimized with caching of results
    -We could go further such as including close matches even when an exact match is found, but for now we prioritize speed
    -due to limited compute
    -This is a good trade off between speed and accuracy for most use cases
    -you get fast and good exact matches, and reasonable fuzzy matches when no exact match exists
    -another optimization could be to keep track of common queries and precompute complex searches for them on an indepnent server followed by caching
    -we implemented a simple adaptive threshold for e.g but replaced with a simple fixed threshold for performance of [:3] top 3
    """
    
    
    
    matches = []
    if word in _match_cache:
        return _match_cache[word]
    # 1. Exact match fast path
    if word in _lexicon_dict:
        r = _lexicon_dict[word] # get the row from the dict 
        _match_cache[word] = [{
            "word_id": r["word_id"],    
            "word": r["word"],
            "score": 1.0
        }]
        return [{
            "word_id": r["word_id"],    
            "word": r["word"],
            "score": 1.0
        }]
    

     # 2. Fuzzy matching for all lexicon words
    for r in _lexicon:
        lex_word = r["word"]
        score = fuzzy_ratio(word, lex_word)

        if score >= base_threshold:
            matches.append({
                "word_id": r["word_id"],
                "word": r["word"],   # return original form
                "score": score
            })

    # 3. Sort strongest matches first
    matches.sort(key=lambda x: x["score"], reverse=True)
    _match_cache[word] = matches[:5]
    return matches[:5]  # return top 5 matches only

def search_db(query: str, page: int, per_page: int = 5):
    """
    Fuzzy + PageRank search.
    Uses lexicon_fuzzy_match() to map query tokens to lexicon entries,
    then uses inverted_index → pages, and scores pages using:
       final_score = 0.65 * query_score + 0.35 * page_rank
    """
    if query in _search_cache:
        return _search_cache[query][ (page - 1) * per_page : page * per_page ]

    if not os.path.exists(DB_PATH):
        return []

    #Tokenize the query 
    tokens = query.lower().split()
    if not tokens:
        return []

    #Collect fuzzy lexicon hits for every token ---
    lex_hits = []
    for tok in tokens:
        lex_hits.extend(lexicon_fuzzy_match(tok))

    if not lex_hits:
        return []

    # Deduplicate word_id keeping best fuzzy score
    word_scores = {}  # word_id to max fuzzy score
    for m in lex_hits:
        wid = m["word_id"]
        score = m["score"]
        if wid not in word_scores or score > word_scores[wid]:
            word_scores[wid] = score

    #get top query length words for performance
    query_length = len(tokens)
    top_word_scores = dict(sorted(word_scores.items(), key=lambda item: item[1], reverse=True)[:query_length])
    word_scores = top_word_scores


    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Aggregate page hits from inverted index ---
    page_scores = {}  # doc_id → combined scoring info

    for word_id, q_score in word_scores.items():
        cur.execute("""
            SELECT 
                d.doc_id,
                d.url,
                d.title,
                d.description,
                COALESCE(p.page_rank, 0.0) AS pr
            FROM inverted_index AS ii
            JOIN doc_index d ON d.doc_id = ii.doc_id
            LEFT JOIN page_rank p ON p.doc_id = ii.doc_id
            WHERE ii.word_id = ?
        """, (word_id,))

        for r in cur.fetchall():
            doc_id = r["doc_id"]

            if doc_id not in page_scores:
                page_scores[doc_id] = {
                    "title": r["title"] or r["url"],
                    "url": r["url"],
                    "desc": (r["description"] or "").split("\n")[0][:250],
                    "page_rank": r["pr"],
                    "query_score": 0.0,
                    "hits": 0,
                }

            # Accumulate relevance
            page_scores[doc_id]["query_score"] += q_score
            page_scores[doc_id]["hits"] += 1

    conn.close()

    #Compute final ranking score
    for info in page_scores.values():
        qs = info["query_score"]
        pr = info["page_rank"]
        hits = info["hits"]

        # small boost for pages matching multiple lexicon words
        coverage_boost = 1 + 0.1 * min(hits, 5)

        info["final_score"] = coverage_boost * (0.65 * qs + 0.35 * pr)

    #Sort by final score
    sorted_pages = sorted(
        page_scores.values(),
        key=lambda x: x["final_score"],
        reverse=True
    )
    _search_cache[query] = sorted_pages
    #pagination
    offset = (page - 1) * per_page
    return sorted_pages[offset:offset + per_page]


def search_db_simple(first_word: str, page: int, per_page: int = 5):
    """Return (results, total_count) for first_word, ordered by PageRank desc."""
    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Find word_id in lexicon
    cur.execute("SELECT word_id FROM lexicon WHERE word = ?", (first_word.lower(),))
    row = cur.fetchone()
    if not row:
        conn.close()
        return []
    word_id = row["word_id"]

    # fetch page of results sorted by pagerank
    offset = (page - 1) * per_page
    cur.execute("""
        SELECT d.url,
               d.title,
               d.description,
               COALESCE(p.page_rank, 0.0) AS pr
        FROM inverted_index AS ii
        JOIN doc_index      AS d ON d.doc_id = ii.doc_id
        LEFT JOIN page_rank AS p ON p.doc_id = ii.doc_id
        WHERE ii.word_id = ?
        ORDER BY pr DESC
        LIMIT ? OFFSET ?;
    """, (word_id, per_page, offset))
    rows = cur.fetchall()
    conn.close()

    ## format into list of dictionaries
    results = []
    for r in rows:
        results.append({
            "title": r["title"] or r["url"],
            "url": r["url"],
            "desc": (r["description"] or "").split("\n")[0][:300],
            "page_rank": r["pr"]
        })

    return results

def getAllKnownWords():
    """Return a list of all known words in the database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Find words in lexicon
    cur.execute("SELECT word FROM lexicon")
    rows = cur.fetchall()

    conn.close()

    # format into a list
    result = []

    for r in rows:
        result.append(r["word"])

    return result

#add code that tests fuzzy matching time for goo for first run and then after cache is populated
def test_fuzzy_matching_performance():
    import time
    test_word = "google"
    start_time = time.time()
    lexicon_fuzzy_match(test_word)
    first_run_time = time.time() - start_time
    print(f"First run (no cache) time: {first_run_time:.6f} seconds")

    start_time = time.time()
    lexicon_fuzzy_match(test_word)
    second_run_time = time.time() - start_time
    print(f"Second run (with cache) time: {second_run_time:.6f} seconds")

'''
def test_search_db():
    #test search_db function
    #test speed of search_db
    import time
    start_time = time.time()
    results = search_db("compu", 1,10)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Search DB time: {elapsed_time:.6f} seconds")
    start_time = time.time()
    results = search_db("compu", 1,10)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Search DB time: {elapsed_time:.6f} seconds")
    for r in results:
        print(f"Title: {r['title']}, URL: {r['url']}, Score: {r['final_score']:.4f}")


test_search_db()
'''

def test_search_outputs():
    print("\n=== TESTING search_db ===")
    res1 = search_db("hello world", page=1, per_page=5)
    print("Type:", type(res1))
    print("Length:", len(res1))
    if res1:
        print("First item keys:", list(res1[0].keys()))
    print("Sample result:", res1[:2])

    print("\n=== TESTING search_db_simple ===")
    res2 = search_db_simple("hello", page=1, per_page=5)
    print("Type:", type(res2))
    print("Length:", len(res2))
    if res2:
        print("First item keys:", list(res2[0].keys()))
    print("Sample result:", res2[:2])

    print("\n=== COMPARISON ===")
    print("Same type?:", type(res1) == type(res2))
    print("Same element type?:", bool(res1 and res2 and isinstance(res1[0], dict) and isinstance(res2[0], dict)))
    print("Same keys?:", (set(res1[0].keys()) == set(res2[0].keys())) if (res1 and res2) else "N/A")

test_search_outputs()