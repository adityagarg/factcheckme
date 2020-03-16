from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse

import fact_check_me.fact_check as fc


APP = Flask(__name__)


OK_BOOMER_IMAGE_URL = (
    "https://www.womensmediacenter.com/assets/site/main/WMC_FBomb_Ok_Boomer_Meme_122019.jpg"
)


DEFAULT_MESSAGE = "Can't help you with that bruh"


@APP.route("/bot", methods=["POST"])
def bot():
    """Fact checks the input query
    
    Returns:
        str: Text response
    """
    incoming_msg = request.values.get("Body", "").lower()
    resp = MessagingResponse()
    msg = resp.message()

    print(len(incoming_msg))

    if len(incoming_msg) > 0:
        msg.body(fc.factcheckme(incoming_msg))
    else:
        msg.body(DEFAULT_MESSAGE)

    return str(resp)


if __name__ == "__main__":
    # APP.run()
    APP.run(debug=True, host='0.0.0.0')
