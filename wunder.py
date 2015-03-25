"""
Script to scrape weather data from wunderground.com for a given city and year range. 
Input city should be wunderground.com's id for it (ex: CYUL for Montreal, KNYC for NYC).

Usage: python wunder.py <city> <start year> <end year> 

TODO: astronomy/moon stuff, hourly stuff, amount of daylight
"""

import sys
import urllib2
from bs4 import BeautifulSoup

def is_leap(year): return year % 400 == 0 or year % 4 == 0

def extract_value(elem): 
  span = elem.find("span")
  if span:
    val = span.find("span", class_="wx-value").get_text()
  else:
    val = elem.get_text()
  val = val.strip()
  try:
    fval = float(val)
    return val
  except ValueError:
    return ''

# All the information we'll be getting  
metadata = ("Mean Temperature", 
            "Max Temperature", 
            "Min Temperature", 
            "Heating Degree Days", 
            "Month to date heating degree days",
            "Since 1 July heating degree days",
            "Cooling Degree Days",
            "Month to date cooling degree days",
            "Year to date cooling degree days",
            "Dew Point",
            "Average Humidity",
            "Maximum Humidity",
            "Minimum Humidity", 
            "Precipitation",
            "Month to date precipitation",
            "Year to date precipitation",
            "Snow",
            "Month to date snowfall",
            "Since 1 July snowfall",
            "Snow Depth",
            "Sea Level Pressure",
            "Wind Speed",
            "Max Wind Speed",
            "Max Gust Speed",
            "Visibility",
            "Events")

# Get parameters 
try:
  city = sys.argv[1]
  try:
    start = int(sys.argv[2])
    end = int(sys.argv[3])
  except ValueError:
    print "Start and end years must be integer-valued"
    raise IndexError
except IndexError:
  print "Usage: python wunder.py <city> <start year> <end year>"
  sys.exit(1)

fname = "_".join([city, str(start), str(end), "weather.csv"])

print "Saving data for", city, "from", start, "to", end, "in", fname 

f = open(fname, 'w')

# First write metadata to first line of file
metadata_info = []
for name in metadata:
  name = name.lower().replace(' ', '_')
  metadata_info.append(name + "_actual")
  metadata_info.append(name + "_average")
  metadata_info.append(name + "_record")
f.write('date' + ',' + ','.join(metadata_info) + '\n')
 
# Iterate through year, month, and day
for year in range(start, end):
  for month in range(1, 13):
    for day in range(1, 32):
 
      # Check if this year is a leap year
      leap = is_leap(year)
 
      # If february leap year, ignore days after 29th
      if (leap and month == 2 and day > 29):
        continue
      elif (month == 2 and day > 28):
        continue
      elif (month in [4, 6, 9, 10] and day > 30):
        continue
 
      # Open wunderground.com url
      url = "http://www.wunderground.com/history/airport/KNYC/" + str(year) + "/" + str(month) + "/" + str(day) + "/DailyHistory.html"
      page = urllib2.urlopen(url)

      print url
 
      soup = BeautifulSoup(page)

      csv = ['NA'] * (len(metadata) * 3)

      # Get historical data 
      trs = soup.find(id="historyTable").find("tbody").find_all("tr")
      for tr in trs:
        spans = tr.find_all("span")

        # If there are no spans, must be a header row - skip
        if len(spans) == 0 or spans is None:
          continue 

        tds = tr.find_all("td")
        name = tds[0].find("span").get_text().strip()
        name = name.lower().replace(' ', '_') + '_actual'

        # Don't bother getting non-standard stuff
        if name not in metadata_info:
          continue
        else:
          index = metadata_info.index(name)

        actual = extract_value(tds[1]) or 'NA'
        try:
          average = extract_value(tds[2]) or 'NA'
        except IndexError:
          average = 'NA'
        try:
          record = extract_value(tds[3]) or 'NA'
        except IndexError:
          record = 'NA'

        csv[index] = actual 
        csv[index + 1] = average
        csv[index + 2] = record 

      line = str(year) + '-' + str(month) + '-' + str(day) + ',' + ','.join(csv) + '\n'
      f.write(line)

# Done!
f.close()
