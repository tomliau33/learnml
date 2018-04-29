import os
import sys
import time
import re
from slackclient import SlackClient
from data import Data
from etl import Etl
from model import Model

class SlackBot(object):
  def __init__(self, slack_token, training_url, testing_url):
    self.slack_client = SlackClient(slack_token)
    self.training_url = training_url
    self.testing_url = testing_url
    self.botid= None
    self.commands = {
      'fillform': (['fill', 'form', '填表'], 'fillform'),
      'wheretoday': (['eat', 'what', 'where', 'predict', '吃什麼', '吃哪裡', '吃哪間'], 'wheretoday')
    }

  def predict(self):
    data = Data(self.training_url, self.testing_url)
    data.fetch_data()
  
    etl = Etl(data)
    etl.do_etl()

    model = Model(etl)
    model.train()
    #model.test(data.testing_data)
    result = model.predict_one(data.testing_data[-1])
    return result

  def parse_messages(self, received_events):
    for event in received_events:
        if event["type"] == "message" and not "subtype" in event:
            print('Receive %s' % event['text'])

            text = event['text']
            user_id, message = self.get_userid_and_message(text)

            if user_id == self.botid:
              return message, event["channel"]
            else:
              return text, event["channel"]

    return None, None

  def get_userid_and_message(self, message_text):
    """
        取得 userid 及 message
    """
    matches = re.search("^<@(|[WU].+?)>(.*)", message_text)
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

  def not_found(self, message):
    return message

  def wheretoday(self, message):
    return "可以考慮吃%s" % (self.predict())

  def fillform(self, message):
    return "若希望小弟推薦餐廳, 請先到 %s 填寫今天的資料" % ('https://somewhere.to.edit.form')

  def ask(self, message):
    for cmd, item in self.commands.items():
      cmd_texts = item[0]
      cmd_funcname = item[1]

      for text in cmd_texts:
        if text in message:
            func = getattr(self, cmd_funcname, "not_found")
            return func(message)

    return None

  def reply_message(self, message, channel):
    """
        針對用戶傳入的 message 回應訊息
    """
    # Default response is help text for the user
    default_response = "可以試著問吃什麼"

    response = None
    response = self.ask(message)

    # Sends the response back to the channel
    self.slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

  def begin(self):
    if self.slack_client.rtm_connect(with_team_state=False):
        print("Begin...")
        self.botid = self.slack_client.api_call("auth.test")["user_id"]
        print("BotId is %s" % self.botid)
        while True:
            text = self.slack_client.rtm_read()
            message, channel = self.parse_messages(text)
            if message:
                self.reply_message(message, channel)
            time.sleep(1)
    else:
        print("failed!")

if __name__ == "__main__":
  if len(sys.argv) < 3:
    print('Usage: %s training_url testing_url' % (sys.argv[0]))
    sys.exit(1)

  training_url = sys.argv[1]
  testing_url = sys.argv[2]

  slack_token = os.environ.get('SLACK_BOT_TOKEN')

  if not slack_token:
    print('Must set SLACK_BOT_TOKEN environment variable!')
    sys.exit(1)

  bot = SlackBot(slack_token, training_url, testing_url)
  bot.begin()

