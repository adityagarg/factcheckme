import os
import logging
import pandas as pd

import requests
import json

# from IPython.core.display import display, HTML

import urllib


API_KEY = os.environ.get("GOOGLE_FACT_CHECK_API_KEY")

API_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

SUCCESS_MSG_TEMPLATE = """
<p>
    <b>'{claim_text}' </b><br>
    claimed by <i>{claimant}</i> on <i>{claimDate}</i>
</p>
<p>
    Review : <b> {textualRating} </b> <br>
    reviewed by <i> {claimReview_publisher} </i> on <i> {claimReview_date} </i><br>
    <a href = '{claimReview_url}' target='_blank'> {claimReview_title} </a>
</p>
"""

GOOGLE_NEWS_URL = """
https://news.google.com/search?q={query}
"""

ERROR_MSG_TEMPLATE = """
<p>
Could not find review for the text. 
Please follow the link below to validate before sharing.
<a href='{google_news_url}'> Search Online </a>
</p>
""".format(
    google_news_url=GOOGLE_NEWS_URL
)

ERROR_MSG_TEMPLATE_TWIML = """
Could not find review for the text. 
Please follow the link below to validate before sharing.
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


def request_api(params):
    params["key"] = API_KEY
    logging.info("params - ", params)
    r = requests.get(API_URL, params=params)
    if r.ok:
        return r.json()


def parse_response(response_json, twiml):

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

    if twiml:
        msg_template = SUCCESS_MSG_TEMPLATE_TWIML
    else:
        msg_template = SUCCESS_MSG_TEMPLATE

    return msg_template.format(
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


def factcheckme(query, twiml=True, debug=False):
    params = {"query": query}

    response_json = request_api(params)

    if debug:
        print(response_json)

    if not response_json.get("claims"):
        if twiml:
            error_message_template = ERROR_MSG_TEMPLATE_TWIML
        else:
            error_message_template = ERROR_MSG_TEMPLATE
        msg = error_message_template.format(query=urllib.parse.quote(query))
    else:
        msg = parse_response(response_json, twiml=twiml)

    # display(HTML(msg))

    return msg
