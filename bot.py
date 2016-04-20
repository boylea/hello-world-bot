import tweepy # for tweeting
import secrets # shhhh
import requests
import nltk # for sentence parsing
nltk.download('punkt')

def get_next_chunk():
  # open text file
  text_file = open('book.txt', 'r+')
  text_string = text_file.read()
  # separate the text into sentences
  tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
  sentences = tokenizer.tokenize(text_string)
  # tweet the whole sentence if it's short enough
  if len(sentences[0]) <= 140:
    chunk = sentences[0]
  # otherwise just print the first 140 characters
  else:
    chunk = sentences[0][0:140]

  # delete what we just tweeted from the text file
  text_file.seek(0)
  text_file.write(text_string[len(chunk):len(text_string)])
  text_file.truncate()
  text_file.close()
  return chunk

def get_article():
  response = requests.get('http://api.nytimes.com/svc/news/v3/content/nyt/all'
      '/last24hours?api-key=%s&limit=1' % secrets.nyt_api_key)
  data = response.json()
  articles = data['results']
  article = articles[0]
  return article

def improve_headline(headline):
  tokens = nltk.word_tokenize(headline)
  tagged = nltk.pos_tag(tokens)
  # Just replace the last noun in the headline, matching plurality
  for word, pos in reversed(tagged):
    if pos == 'NN' or pos == 'NNP' or pos == 'NNS':
      replacement = 'Puppy'
      break
    elif pos == 'NNPS':
      replacement = 'Puppies'
      break

  better_headline = headline.replace(word, replacement)
  return better_headline

def make_news_tweet():
  article = get_article()
  headline = improve_headline(article['title'])
  tweet = 'BREAKING: {}\n{}'.format(headline, article['url'])
  return tweet

def tweet(message):
  auth = tweepy.OAuthHandler(secrets.consumer_key, secrets.consumer_secret)
  auth.set_access_token(secrets.access_token, secrets.access_token_secret)
  api = tweepy.API(auth)
  auth.secure = True
  print("Posting message {}".format(message))
  api.update_status(status=message)

tweet(make_news_tweet())
