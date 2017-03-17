import urllib
#from lxml import html
from bs4 import BeautifulSoup
import re
import json
import os
from nltk.corpus import stopwords
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt

dump_file = 'simpsons_dump.json'
count_file = 'bubble_cloud/data/simpsons.csv'
popular_names = ['homer', 'bart', 'marge', 'lisa', 'maggie']

def print_data(data, N):
  for i in range(0, N):
    print '%d) %s' %(i+1, data[i])

def plot_bar(words_n_counts, ylabel, title):
  N = len(words_n_counts)
  y_pos = np.arange(N)
  counts = np.array([item[1] for item in words_n_counts])
  words = tuple([item[0] for item in words_n_counts])
  plt.figure()
  plt.bar(y_pos, counts[0:N], align='center', alpha=0.5)
  plt.xticks(y_pos, words, rotation='vertical')
  plt.ylabel(ylabel)
  plt.title(title)
  plt.autoscale(enable=True, axis='both', tight=None)

# This downloads the html from given url and extracts useful tag content.
def get_all_words(url):
  all_words = []
  try:
    soup = BeautifulSoup(urllib.urlopen(url).read())
    print 'Downloaded %s'%(url)
    data = soup.findAll(attrs={'class' : 'scrolling-script-container'})[0]
    data = data.contents
    for line in data:
      if isinstance(line, basestring):
        words = re.sub("[^\w]", " ",  line).split()
        all_words.extend(words)
  except:
    print 'Skipping %s'%(url)
    pass
  return all_words

####################################
# Download data if does not exist. #
####################################
if os.path.isfile(dump_file):
  # Load existing data.
  with open(dump_file) as fin:
    words_by_episode = json.load(fin)
  print 'loaded shit'
else:
  # Get data.
  base_url = "http://www.springfieldspringfield.co.uk/view_episode_scripts.php?tv-show=the-simpsons&episode=s%.2de%.2d"
  words_by_episode = {}
  for s in range(1, 29):
    for ep in range(1, 32):
      url = base_url %(s, ep)
      key = '%.2d_%.2d'%(s, ep)
      words = get_all_words(url)
      if len(words) > 0:
        words_by_episode[key] = words

  with open(dump_file, 'w') as fout:
    json.dump(words_by_episode, fout)

###########################
# Do fun stuff with data. #
###########################

# Merge words from all episodes.
all_words = []
for key, words in words_by_episode.iteritems():
  # Make all words lower-case.
  words = [word.lower() for word in words]
  all_words.extend(words)

# Get count of words, and make a list of pairs [(word, count)] out of it.
counts = dict(Counter(all_words))
words_n_counts = []
for key, value in counts.iteritems():
  words_n_counts.append((key, value))

# Sort by counts.
words_n_counts = sorted(words_n_counts, reverse=True, key=lambda x:x[1])

# Print top 10 words and their counts.
print_data(words_n_counts, 10)
print 'Of course, these are all stopwords...'
print "Let's remove them now and clean our list"
print '....\n'

# Remove words in the stopword list.
stopwords = set(stopwords.words("english"))
filtered_words_n_counts = [item for item in words_n_counts if item[0] not in stopwords]
print_data(filtered_words_n_counts, 10)
print 'Hey, I spot homer in spot#5!!'
print '....\n'

# Dump stats for use in d3.js visualization.
with open(count_file, 'w') as fout:
  fout.write('name,count\n')
  for item in filtered_words_n_counts[0:100]:
    fout.write('%s,%d\n'%(item[0], item[1]))
fout.close()

# Print popular names stats.
print 'Major characters and their name mentions'
for name in popular_names:
  print '%s: %d'%(name, counts[name])
print '....\n'

# Plot frequencies.
N = 50
print "Let's plot the distribution of the top %d unfiltered words" %(N)
plot_bar(words_n_counts[0:N], 'Counts', 'Unfiltered words and their counts')
print "Let's plot the distribution of the top %d filtered words" %(N)
plot_bar(filtered_words_n_counts[0:N], 'Counts', 'Filtered words and their counts')
plt.show()
print '....\n'

print "D'OH! Sadly it looks like d'oh has been reduced to oh while splitting words as ' is a delimiter"

