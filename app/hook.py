import os
import re
import threading
from collections import Counter
from functools import wraps

from jieba import cut
from pypinyin import lazy_pinyin, Style

from app.extensions import db, is_redis_on, save, log
from app.models import Post
from app.utils import print_blanks


def search_index(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        result = func(*args, **kwargs)
        threading.Thread(target=_search_index).start()
        return result

    return decorator


def load_stopwords(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def get_pinyin_and_initials(word):
    pinyin = "".join(lazy_pinyin(word))
    initials = "".join(lazy_pinyin(word, style=Style.FIRST_LETTER))
    return pinyin, initials


@print_blanks
def _search_index():
    from app import app

    if not is_redis_on():
        return
    with app.app_context():

        keyword_to_post_id = {}

        posts = db.session.query(Post).all()
        stopwords = load_stopwords(
            os.path.abspath(
                os.path.join(os.path.realpath(__file__), "../stop_words.txt")
            )
        )

        for post in posts:
            words = cut(post.title + post.content, cut_all=False)

            filtered_words = [
                w
                for w in words
                if w.strip()
                and w not in stopwords
                and re.match(r"[\u4e00-\u9fa5a-zA-Z0-9]+", w)
            ]
            words_count = Counter(filtered_words).most_common(10)

            for w, _ in words_count:
                if w in stopwords or not w.strip():
                    continue

                pinyin, initials = get_pinyin_and_initials(w)

                for keyword in [w, pinyin, initials]:
                    if keyword not in keyword_to_post_id:
                        keyword_to_post_id[keyword] = []
                    keyword_to_post_id[keyword].append(post.id)

        log("INFO", "更新搜索索引")
        print(keyword_to_post_id)
        save("search_cache", keyword_to_post_id, 99999)
        return keyword_to_post_id
