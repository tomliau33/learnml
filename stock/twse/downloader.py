import os
import sys
import json
import time
import requests

from datetime import datetime, timedelta

urls = {
  't86': 'https://www.twse.com.tw/fund/T86',
  'mindex': 'https://www.twse.com.tw/exchangeReport/MI_INDEX'
}

params = {
  't86': {
        'response': 'json',
        'selectType': 'ALL'
  },
  'mindex': {
        'response': 'json',
        'type': 'ALL'
  }
}

class Downloader(object):
  def __init__(self, url, params):
    self.url = url
    self.params = params

  def write_output(self, filepath, content):
    with open(filepath, 'w') as f:
      f.write(content)

  def download(self, dates, output_folder, interval=2, fail_interval=15):
    params = self.params.copy()
    count = 0

    for d in dates:
      tm = int(time.time() * 1000)
      params['date'] = d
      params['_'] = str(tm)

      print('Download date {}'.format(d))
      successful = False
      for i in range(5):
        try:
          r = requests.get(self.url, params = params)
          if r.status_code == requests.codes.ok:
            rjson = r.json()
            if rjson["stat"] == "OK":
              self.write_output('{}/{}.json'.format(output_folder, d), r.text)
              print('Download ok, date is {}'.format(d))
              successful = True
              count += 1
              break
            elif rjson["stat"] == "很抱歉，沒有符合條件的資料!":
              print("Not found, date is {}".format(d))
              successful = True
              break
            else:
              print('Download fail, date is {}, stat is "{}"'.format(d, rjson['stat']))
          else:
            print('Download fail, date is {}, status_code is {}'.format(d, r.status_code))
        except Exception as e:
          print('Occur exception, date is {}, exception is {}'.format(d, e))
  
        time.sleep(fail_interval)
  
      if not successful:
        print('Stop at {}'.format(d))
        break

      time.sleep(interval)

    print('Total {}'.format(count))

def get_dates(datestr, output_folder):
  dates = []

  if datestr == 'auto':
    datestr = 'auto-now'

  if datestr == 'today' or datestr == 'now':
    d = datetime.now()
    dates.append('{}{}{}'.format(d.year, str(d.month).zfill(2), str(d.day).zfill(2)))
  elif datestr == 'yesterday':
    d = datetime.now() - timedelta(days=1)
    dates.append('{}{}{}'.format(d.year, str(d.month).zfill(2), str(d.day).zfill(2)))
  elif '-' in datestr:
    sstart, send = datestr.split('-')

    if sstart == 'yesterday':
      start = datetime.now() - timedelta(days=1)
    elif sstart.endswith('ago'):
      start = datetime.now() - timedelta(days=int(sstart[:-3]))
    elif sstart == 'auto':
      filenames = [filename for filename in os.listdir(output_folder) if len(filename) == 13]
      if len(filenames) == 0:
        start = datetime.now()
      else:
        filenames.sort()
        ds = filenames[-1].split('.')[0]
        start = datetime(year=int(ds[:4]), month=int(ds[4:6]), day=int(ds[6:8])) + timedelta(days=1)
        if start > datetime.now():
          print('Already update to date!')
          sys.exit(0)
    else:
      start = datetime(year=int(sstart[:4]), month=int(sstart[4:6]), day=int(sstart[6:8]))

    if send == 'today' or send == 'now':
      end = datetime.now()
    elif send == 'yesterday':
      end = datetime.now() - timedelta(days=1)
    elif send.endswith('ago'):
      end = datetime.now() - timedelta(days=int(send[:-3]))
    else:
      end = datetime(year=int(send[:4]), month=int(send[4:6]), day=int(send[6:8]))

    if start > end:
      print('{} is greater than {}'.format(sstart, send))
      return []

    i = start
    while i <= end:
      dates.append('{}{}{}'.format(i.year, str(i.month).zfill(2), str(i.day).zfill(2)))
      i += timedelta(days=1)

  elif datestr.endswith('ago'):
    d = datetime.now() - timedelta(days=int(datestr[:-3]))
    dates.append('{}{}{}'.format(d.year, str(d.month).zfill(2), str(d.day).zfill(2)))
  elif not os.path.exists(sys.argv[2]):
    dates.append(sys.argv[2])
  else:
    with open(sys.argv[2], 'r') as f:
      for line in f:
        dates.append(line.strip())

  return dates

def main():
  if len(sys.argv) < 4:
    print('Usage: {} [t86|mindex] [dates.txt] [output_folder]'.format(sys.argv[0]))
    sys.exit(0)

  print("Mode is {}".format(sys.argv[1]))
  dates = get_dates(sys.argv[2], sys.argv[3])

  if len(dates) >= 2:
    print("Date is from {} to {}, total {} days".format(dates[0], dates[-1], len(dates)))
  elif len(dates) == 1:
    print("Date is {}".format(dates[0]))
  else:
    print("Date is empty")

  downloader = Downloader(
      urls[sys.argv[1]],
      params[sys.argv[1]]
  )
  downloader.download(dates, sys.argv[3])

if __name__ == '__main__':
    main()

