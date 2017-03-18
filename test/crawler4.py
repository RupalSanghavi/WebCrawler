#Christopher Reeves Web Scraping Tutorial
#simple web spider that returns array of urls.
#http://youtube.com/creeveshft
#http://christopherreevesofficial.com
#http://twitter.com/cjreeves2011

import urllib
from bs4 import BeautifulSoup as BS
import urlparse
import mechanize
from HTMLParser import HTMLParser
from urllib2 import urlopen, HTTPError
import re
from nltk.stem import *


class MyHTMLParser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            print "Encountered a start tag:", tag
        def handle_endtag(self, tag):
            print "Encountered an end tag :", tag
        def handle_data(self, data):
            print "Encountered some data  :", data

# Set the startingpoint for the spider and initialize
# the a mechanize browser object
url = "http://lyle.smu.edu/~fmoore"
br = mechanize.Browser()

# create lists for the urls in que and visited urls
urls = [url]
visited = [url]
outgoing = []
graphics = []


# Since the amount of urls in the list is dynamic
#   we just let the spider go until some last url didn't
#   have new ones on the webpage
while len(urls)>0:
    try:
        br.open(urls[0])
        urls.pop(0)
        try:
            for link in br.links():
                newurl =  urlparse.urljoin(link.base_url,link.url)
                #print("** ",newurl)
                if newurl not in visited and url in newurl:
                    visited.append(newurl)
                    urls.append(newurl)
                elif url not in newurl:
                    outgoing.append(newurl)
        except mechanize._mechanize.BrowserStateError:
            print("Cannot crawl: " + str(urls[0]))


    except:
        if(len(urls)>0):
            print("Broken: "+ str(urls[0]))
            visited.append(urls[0])
            urls.pop(0)

parser = MyHTMLParser()
stemmer = PorterStemmer()
docIDs = {}
stemToIDs = {}
stemWordFreq = {}
ID = 0
# print(visited)
for url in visited:
    try:
        usock = urlopen(url)
        data = usock.read()
        usock.close()
        soup = BS(data, "html5lib")
        reg = re.search('([^\s]+(\.(?i)(txt|htm|html))$)',url)
        if(reg):
            docIDs[ID] = url
            ID += 1
            text = soup.findAll(text=True)
            textJoined = ' '.join(text)
            words = re.split('\W+', textJoined, flags=re.IGNORECASE)
            # print("WORDS:")
            # print(words)
            stemmed = [stemmer.stem(word) for word in words]
            # print("After Stemmed: ")
            # print(stemmed)
            for stem in stemmed:
                if(stemWordFreq.get(stem) == None):
                    stemWordFreq[stem] = []
                    stemWordFreq[stem].append(ID)
                else:
                    stemWordFreq[stem].append(ID)
        if(soup.find('title')):
            print("title: ", soup.find('title').text)
        is_graphic = re.search('([^\s]+(\.(?i)(jpg|png|gif|bmp))$)',url)
        if(is_graphic):
            graphics.append(url)
            print(str(url) + " is a graphic. ")
    except HTTPError, e:
        print e.code
        print e.msg
# print("Doc IDs: ")
# for key,val in docIDs.iteritems():
#     print(str(key) + " : " + str(val))
# print("Doc Freqs: ")
# print(stemWordFreq)
# print("word : freq")
# for word in sorted(stemWordFreq, key=lambda word: len(stemWordFreq[word]),reverse=True):
#     print(str(word) + " : " + str(len(stemWordFreq[word])))
print("URLS: ")
print(visited)
print("Outgoing: ")
print(outgoing)
#print(set(visited) - set(outgoing) - set(graphics))
