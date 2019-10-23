from difflib import SequenceMatcher

from flask import Flask, request
from pymessenger.bot import Bot

# CONFIG
ACCESS_TOKEN = '' # Page Access Token
VERIFY_TOKEN = 'mytoken'

similarity_treshold = 0.2

welcome = "Hi! I'm Arthur, the customer support chatbot. How can I help you?"

questions = (
    "The app if freezing after I click run button",
    "I don't know how to proceed with the invoice",
    "I get an error when I try to install the app",
    "It crash after I have updated it",
    "I cannot login in to the app",
    "I'm not able to download it"
            )

answers = (
        "You need to clean up the cache. Please go to ...",
        "Please go to Setting, next Subscriptions and there is the Billing section",
        "Could you plese send the log files placed in ... to ...",
        "Please restart your PC",
        "Use the forgot password button to setup a new password",
        "Probably you have an ad blocker plugin installed and it blocks the popup with the download link"
            )


app = Flask(__name__)
bot = Bot(ACCESS_TOKEN)

@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        token_sent = request.args.get("hub.verify_token")
        return verify_fb_token(token_sent)
    else:
        output = request.get_json()
        for event in output['entry']:
            if 'messaging' in event:
                messaging = event['messaging']
                for message in messaging:
                    if message.get('message'):
                        recipient_id = message['sender']['id']
                        msg_content = message['message'].get('text')
                        if msg_content:
                            response_sent_text = get_message(msg_content)
                            send_message(recipient_id, response_sent_text)
                return "Message Processed"

def verify_fb_token(token_sent):
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'

def get_message(msg):
    return get_highest_similarity(msg)

def send_message(recipient_id, response):
    bot.send_text_message(recipient_id, response)
    return "success"

def get_highest_similarity(customer_question):
    max_similarity = 0
    highest_prob_index = 0
    for question_id in range(len(questions)):
        similarity = SequenceMatcher(None,customer_question,questions[question_id]).ratio()
        #print(similarity)
        if similarity > max_similarity:
            highest_index = question_id
            max_similarity = similarity
    if max_similarity > similarity_treshold:
        return answers[highest_index]
    else:
        return "The issues has been saved. We will contact you soon."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
