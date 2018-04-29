# 此為建議中餐吃什麼的推薦程式 #

使用方式:
* 將每天的用餐資料記錄在 `data/train_data.csv` 上
* 編輯 `data/test_data.csv`, 填入當日資料, 餐聽隨便寫去過的即可
* 執行 python model.py
* 會在螢幕秀出推薦餐廳

Slack Bot:
* 將 slack bot user 的 token 設定到環境變數 SLACK_BOT_TOKEN
* 執行 python slack_bot.py data/train_data.csv data/test_data.csv
* 詢問機器人"吃什麼", 他會回覆推薦的餐廳

PS: train_data 及 test_data 可以為一個 url

