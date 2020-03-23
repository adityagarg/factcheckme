import os
import logging
import urllib
import pandas as pd

import requests


GOOGLE_API_KEY = os.environ.get("GOOGLE_FACT_CHECK_API_KEY")

NEWS_API_KEY = os.environ.get("NEWS_API_KEY")

GOOGLE_API_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

NEWS_API_URL = "http://newsapi.org/v2/everything"

GOOGLE_NEWS_URL = """
https://news.google.com/search?q={query}
"""

ERROR_MSG_TEMPLATE_TWIML = """
Could not find a review or specific news article related to the claim. 
Please follow the link below to browse articles before sharing.
{google_news_url}
""".format(
    google_news_url=GOOGLE_NEWS_URL
)

SUCCESS_MSG_TEMPLATE_TWIML = """
*'{claim_text}'*
claimed by _{claimant}_ on _{claimDate}_

Review : *{textualRating}*
reviewed by _{claimReview_publisher}_ on _{claimReview_date}_

"{claimReview_title}"
{claimReview_url}
"""

NEWS_MSG_TEMPLATE_TWIML = """
Could not find a review for the text. However, the following news article seems relevant to the claim: 

*'{article_headline}'*
by _{article_source_name}_ published on _{article_published_at_date}_
{article_url}

To find further articles related to the claim, you may visit the link below:
{google_new_url}
"""


def request_fact_check_api(query):
    params = {"query": query, "key": GOOGLE_API_KEY}
    logging.info("params : {} ".format(params))
    r = requests.get(GOOGLE_API_URL, params=params)
    if r.ok:
        return r.json()


def request_news_api(query):
    params = {"q": query, "sortBy": "relevancy", "apiKey": NEWS_API_KEY}
    r = requests.get(NEWS_API_URL, params=params)
    logging.info("News API request status - {}".format(r))
    if r.ok:
        return r.json()


def parse_fact_check_response(response_json):

    claim = response_json["claims"][0]
    claim_text = claim["text"]
    claimant = claim.get("claimant") or "Unknown"
    claimDateTime = claim.get("claimDate")
    claimDate = pd.to_datetime(claimDateTime).date() if claimDateTime else "Unknown Date"
    claimReview = claim["claimReview"][0]
    claimReview_publisher = claimReview["publisher"]["name"]
    claimReview_title = claimReview.get("title") or "Review Article"
    claimReview_datetime = claimReview.get("reviewDate")
    claimReview_date = (
        pd.to_datetime(claimReview_datetime).date() if claimReview_datetime else "Unknown Date"
    )
    claimReview_url = claimReview.get("url")
    textualRating = claimReview.get("textualRating")
    reviewDate = claimReview.get("reviewDate")

    return SUCCESS_MSG_TEMPLATE_TWIML.format(
        claim_text=claim_text,
        claimant=claimant,
        claimDate=claimDate,
        claimReview_publisher=claimReview_publisher,
        claimReview_title=claimReview_title,
        claimReview_url=claimReview_url,
        textualRating=textualRating,
        reviewDate=reviewDate,
        claimReview_date=claimReview_date,
    )


def parse_news_response(response_json):

    print(response_json)

    if response_json["totalResults"] > 0:

        article = response_json["articles"][0]
        article_source_name = article["source"]["name"]
        article_title = article.get("title")
        article_url = article.get("url")
        article_datetime = article.get("publishedAt")
        article_date = pd.to_datetime(article_datetime).date() if article_datetime else ""

        return NEWS_MSG_TEMPLATE_TWIML.format(
            article_headline=article_title,
            article_source_name=article_source_name,
            article_published_at_date=article_date,
            article_url=article_url,
            google_new_url=GOOGLE_NEWS_URL,
        )

    else:
        return ERROR_MSG_TEMPLATE_TWIML


def factcheckme(query):
    response_json = request_fact_check_api(query)

    review_found = False

    if response_json:
        if response_json.get("claims"):
            review_found = True

    if review_found:
        msg = parse_fact_check_response(response_json)
    else:
        news_json = request_news_api(query)
        msg = parse_news_response(news_json).format(query=urllib.parse.quote(query))

    return msg
