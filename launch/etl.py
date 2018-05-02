from collections import deque
from sklearn.preprocessing import label_binarize
from sklearn import preprocessing
import numpy as np
import pandas as pd
from data import Data

class Etl(object):
  def __init__(self, data):
    self.data = data

    self.all_members = []
    self.all_restaurants = []
    self.all_weathers = []
    self.counts = []
    self.le_of_restaurants = preprocessing.LabelEncoder()

    self._initialize(data.training_data)

  def _initialize(self, data):
    members = set()
    restaurants = set()
    weathers = set()
    counts = list()
    
    for record in data:
      # 檢查餐廳是否在選項內
      if record[1] not in self.data.restaurant_set:
        raise Exception('Unknown restaurant %s' % (record[1]))
      restaurants.add(record[1])

      # 檢查天氣是否在選項內
      if record[2] not in self.data.weather_set:
        raise Exception('Unknown weather %s' % (record[2]))
      weathers.add(record[2])

      # 檢查成員是否在選項內
      for member in record[0]:
        if member not in self.data.member_set:
          raise Exception('Unknown member %s' % (member))
        members.add(member)

    for n in range(1, len(members)+1):
      counts.append('count%d' % n)

    self.all_members = list(members)
    self.all_restaurants = list(restaurants)
    self.all_weathers = list(weathers)
    self.all_counts = counts

    self.le_of_restaurants.fit(self.all_restaurants)
    
  def _rest_to_index(self, rest):
    ''' 餐廳名稱轉編號
    '''
    return self.le_of_restaurants.transform([rest])[0]

  def _index_to_rest(self, idx):
    ''' 編號轉餐廳名稱
    '''
    return self.le_of_restaurants.inverse_transform([idx])[0]

  def _generate_member_features(self, members):
    r = label_binarize(members, classes=self.all_members)
    return pd.DataFrame([np.max(r, axis=0)], columns=self.all_members)

  def _generate_weather_features(self, weather):
    r = label_binarize(weather, classes=self.all_weathers)
    return pd.DataFrame([np.max(r, axis=0)], columns=self.all_weathers)

  def _generate_count_features(self, count):
    r = label_binarize(count, classes=self.all_counts)
    return pd.DataFrame([np.max(r, axis=0)], columns=self.all_counts)

  def _generate_restaurant_features(self, history):
    all = []
    idx = 0
    for rest in history:
      x = label_binarize([rest], classes=self.all_restaurants)

      # generate column name
      idx += 1
      cols = []
      for c in self.all_restaurants:
        cols.append('%s_%d' % (c, idx))
      
      all.append(pd.DataFrame(x, columns=cols))
      
    return pd.concat(all, axis=1)

  def _process_one_record(self, record, history):
    (member, restaurant, weather, temperature) = record
    
    member_features = self._generate_member_features(member)
    restauratn_features = self._generate_restaurant_features(history)
    weather_features = self._generate_weather_features([weather])
    count_features = self._generate_count_features(['count%d' % len(member)])
    
    others = pd.DataFrame(
        [[temperature, self._rest_to_index(restaurant)]], 
        columns=['temperature', 'answer']
    )

    return pd.concat([member_features, restauratn_features, weather_features, count_features, others], axis=1)

  def _data_to_features(self, data):
    history = deque([0] * self.data.reference_days)
    features = self._process_one_record(data[0], history)
    
    for record in data[1:]:
      f = self._process_one_record(record, history)
      features = features.append(f)
      history.popleft()
      history.append(record[1])
  
    if self.data.verbose:
      print ("Total records: %d" % len(features))

    return features

  def do_etl(self):
    self.training_etldata = self._data_to_features(self.data.training_data)
    self.testing_etldata = self._data_to_features(self.data.testing_data)

    self.training_etldata.to_csv("tmp/training.csv")
    self.testing_etldata.to_csv("tmp/testing.csv")


def main():
  data = Data()
  data.fetch_data()
  
  etl = Etl(data)
  etl.do_etl()

if __name__ == "__main__":
    main()

