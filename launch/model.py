import sys

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import confusion_matrix

from data import Data
from etl import Etl

class Model(object):
  def __init__(self, etl):
    self.etl = etl
    self.model = None

  def train(self):
    y = self.etl.training_etldata['answer'].values
    X = self.etl.training_etldata.drop('answer', 1)

    #model = LogisticRegression()
    model = DecisionTreeClassifier()
    #model = RandomForestClassifier()
    model = model.fit(X, y)

    ty = self.etl.testing_etldata['answer'].values
    tX = self.etl.testing_etldata.drop('answer', 1)

    p = model.predict(tX)

    acc = model.score(tX, ty)
    f1 = f1_score(ty, p, average='weighted')
    prec = precision_score(ty, p, average='weighted')
    recall = recall_score(ty, p, average='weighted')
    cm = confusion_matrix(ty, p)

    self.model = model

    if self.etl.data.verbose:
      print ('acc:%f\nf1:%f\nprec:%f\nrecall:%f' % (acc, f1, prec, recall))
      print (str(cm))

  def predict(self, records, history):
    ty = []
    tX = None
    for record in records:
      feature = self.etl._process_one_record(record, history)
      ty.append(feature['answer'])
      feature = feature.drop('answer', 1)
      if tX is None:
        tX = feature
      else:
        tX = tX.append(feature)

    ps = self.model.predict(tX)
    return (ty, ps)
  
  def test(self, data):
    history = [r[1] for r in data[-self.etl.data.reference_days:]]
    (ty, ps) = self.predict(data, history)
    for (y, p, d) in zip(ty, ps, data):
      print ('%d %2d : %2d   (%s : %s) - %s' % (y == p, y, p, self.etl._index_to_rest(y), self.etl._index_to_rest(p), str(d)))

  def predict_one(self, record):
    days = -self.etl.data.reference_days
    data = self.etl.data.training_data[days:].copy()
    data += [record]
    history = [r[1] for r in data[days:]]

    (ty, ps) = self.predict(data, history)

    result = self.etl._index_to_rest(ps[-1])

    return result

def main():
  if len(sys.argv) == 2:
    data = Data(sys.argv[1])
  elif len(sys.argv) == 3:
    data = Data(sys.argv[1], sys.argv[2])
  else:
    data = Data()

  data.fetch_data()
  
  etl = Etl(data)
  etl.do_etl()

  model = Model(etl)
  model.train()
  #model.test(data.testing_data)
  result = model.predict_one(data.testing_data[-1])
  print (result)

if __name__ == "__main__":
    main()

