import os
import numpy as np
import pandas as pd
import urllib.request
import datetime

# CSV format:
# Timestamp,日期,成員,備註,餐廳名,天氣,溫度,濕度,備註
# 05/03/2018 14:04:07,05/03/2018,"Abby, Tom, Jason, Lee, Kitty",,麥當勞,晴,27,69,
DEFAULT_TRAINDATA='data/train_data.csv'
DEFAULT_TESTDATA='data/test_data.csv'

class Data(object):
  def __init__(self, train_ds=DEFAULT_TRAINDATA, test_ds=DEFAULT_TESTDATA, reference_days=3, verbose=False):
    self.train_ds = train_ds
    self.test_ds = test_ds
    self.reference_days = reference_days
    self.verbose = verbose

    self.training_data = []
    self.testing_data = []

    self.member_set = []
    self.restaurant_set = []
    self.weather_set = []

    if os.path.isdir('history') == False:
        os.mkdir('history')

    if os.path.isdir('tmp') == False:
        os.mkdir('tmp')

  def _load_csv(self, csvpath, is_update_config=True):
    df = pd.read_csv(csvpath)

    # 找出所有成員
    member_set = set()
    for member in df['成員'].values:
      users = member.split(', ')
      for u in users:
        member_set.add(u)

    # 找出所有餐廳
    restaurant_set = set()
    for r in df['餐廳名'].values:
      restaurant_set.add(r)

    # 找出所有天氣
    weather_set = set()
    for r in df['天氣'].values:
      weather_set.add(r)

    if is_update_config:
      self.member_set = list(member_set)
      self.restaurant_set = list(restaurant_set)
      self.weather_set = list(weather_set)

    # 產生訓練資料
    data = []
    records = zip(df['成員'].values, df['餐廳名'].values, df['天氣'], df['溫度'])
    for (member, restaurant, weather, temperature) in records:
        users = member.split(', ')
        data.append([users, restaurant, weather, temperature])
  
    return data

  def _download_csv(self, url, is_update_config=True):
    response = urllib.request.urlopen(url)
    csv = response.read()

    if is_update_config:
      csvfilename = datetime.datetime.today().strftime('history/%Y%m%d.csv')
    else:
      csvfilename = datetime.datetime.today().strftime('history/test_%Y%m%d.csv')

    with open(csvfilename, 'wb') as f:
      f.write(csv)

    return self._load_csv(csvfilename, is_update_config)

  def fetch_data(self):
    if self.train_ds.startswith('http'):
      self.training_data = self._download_csv(self.train_ds)
    else:
      self.training_data = self._load_csv(self.train_ds)

    if self.test_ds.startswith('http'):
      self.testing_data = self._download_csv(self.test_ds, False)
    else:
      self.testing_data = self._load_csv(self.test_ds, False)

    if self.verbose:
      print("Training data:")
      for r in self.training_data:
        print(str(r))

      print("Testing data:")
      for r in self.testing_data:
        print(str(r))

def main():
  data = Data()
  data.fetch_data()

if __name__ == "__main__":
    main()

