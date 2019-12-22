import pandas as pd

import requests
import json

from IPython.core.display import display, HTML


API_KEY = "AIzaSyBBPmqV4YJXA3gWWA4L9CLoJIm-oqVStk4"

API_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

SUCCESS_MSG_TEMPLATE = """
<p>
    <b>'{claim_text}' </b><br>
    claimed by <i>{claimant}</i> on <i>{claimDate}</i>
</p>
<p>
    Review : <b> {textualRating} </b> <br>
    reviewed by <i> {claimReview_publisher} </i> <br>
    <a href = '{claimReview_url}'> {claimReview_title} </a>
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


def request_api(params):
    params["key"] = API_KEY
    r = requests.get(API_URL, params=params)
    if r.ok:
        return r.json()


def parse_response(response_json):

    claim = response_json["claims"][0]
    claim_text = claim["text"]
    claimant = claim.get("claimant") or "Unknown"
    claimDateTime = claim.get("claimDate")
    claimDate = pd.to_datetime(claimDateTime).date() if claimDateTime else "Unknown Date"
    claimReview = claim["claimReview"][0]
    claimReview_publisher = claimReview["publisher"]["name"]
    claimReview_title = claimReview.get("title") or "Review Article"
    claimReview_url = claimReview["url"]
    textualRating = claimReview["textualRating"]
    reviewDate = claimReview["reviewDate"]

    return SUCCESS_MSG_TEMPLATE.format(
        claim_text=claim_text,
        claimant=claimant,
        claimDate=claimDate,
        claimReview_publisher=claimReview_publisher,
        claimReview_title=claimReview_title,
        claimReview_url=claimReview_url,
        textualRating=textualRating,
        reviewDate=reviewDate,
    )


def factcheckme(query, debug=False):
    params = {"query": query}

    response_json = request_api(params)

    if debug:
        print(response_json)

    if not response_json.get("claims"):
        msg = ERROR_MSG_TEMPLATE.format(query=query)
    else:
        msg = parse_response(response_json)

    display(HTML(msg))
