"""
    Neozot
"""

from zoterodb import ZoteroDB
from feedprovider import ArxivFeedProvider

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

# from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel as similarity


def main():
    datadir = "data/"

    zotdb = ZoteroDB(datadir)
    library = zotdb.get_library()
    display_items(library)
    
    arxiv = ArxivFeedProvider()
    feed = arxiv.get_feed_summary()
    display_items(feed)

    # Build a summary of each item, only if it has abstract
    items_summary = build_summary(library)
    print("Created summary for {}/{} documents.".format(
        len(items_summary), len(library)))
    
    feed_summary = build_summary(feed)
    print("Created summary for {}/{} feed items.".format(
        len(feed_summary), len(feed)))

    # Create feature builder
    encoder = TfidfVectorizer(
        input='content',
        strip_accents='unicode',
        lowercase=True,
        analyzer='word',
        stop_words='english',
        max_df=0.25,
        min_df=10,
        norm='l2',
        use_idf=True
    )

    items_embedding = encoder.fit_transform(items_summary.values())
    feed_embedding = encoder.transform(feed_summary.values())

    feed_similarity = similarity(items_embedding, feed_embedding)

    # Get top K pairs
    # Ref: https://stackoverflow.com/a/57105712
    K = 10
    top_K = np.c_[
                np.unravel_index(
                    np.argpartition(feed_similarity.ravel(),-K)[-K:],
                    feed_similarity.shape
                )]

    # Index to id mapping for library
    ids_library = list(items_summary.keys())
    # For feed, the key itself can be index, but just creating the map
    ids_feed = list(feed_summary.keys())

    for i, j in top_K:
        item_id = ids_library[i]
        feed_id = ids_feed[j]

        print(library[item_id])
        print(feed[feed_id])
        print("Score: ", feed_similarity[i, j], i, j)
        print("----")



def display_items(library):
    for i, (id, info) in enumerate(library.items()):
        buffer = "{:4d}\n".format(i)
        buffer += "        id              : {}\n".format(id)
        for k, v in info.items():
            buffer += "        {:16s}: {}\n".format(k, v)
        print(buffer)


def build_summary(library):
    summary = {}
    for id, info in library.items():
        _title = info.get('title', None)
        _abstract = info.get('abstractNote', None)
        if _title and _abstract:
            summary[id] = _title + '; ' + _abstract

    return summary


if __name__=="__main__":
    main()
