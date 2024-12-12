# title = self.UnbiasedNewsGenerator.generate_unbiased_news(
#     title_generator.generate_elegant_title(ag.get_titles(), max_length=75)
# )
title = title
# Description generation
description = self.UnbiasedNewsGenerator.generate_unbiased_news(
    description_summarizer.generate_flowing_description(
        ag.get_descriptions(), max_sentences=5
    )
)


# Select relevant images
logging.info(f"Selecting images for article: {title}")
# Insert the article into the database
logging.info(f"Inserting article into database: {title}")
Article_Insert.article_insert(
    title,
    description,
    url,
    imgs,
    ag,
)
similar_articles = google_search_article_links(title)

# Iterate through similar articles with a progress bar
for similar_article in tqdm(
    similar_articles,
    desc=f"Processing similar articles for {title}",
    unit="similar article",
):
    ag.get_article(similar_article)
