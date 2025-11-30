import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'search_engine.db')

def search_db(first_word: str, page: int, per_page: int = 5):
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