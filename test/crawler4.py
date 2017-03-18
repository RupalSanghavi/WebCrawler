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
import robotparser
from nltk.corpus import stopwords


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
duplicates = []
counts = {}
disallowed = []


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
                #print("!! ", link.url)
                if url not in newurl:
                    outgoing.append(newurl)
                # if newurl in visited:
                #     duplicates.append(newurl)
                # usock = urlopen(newurl)
                # data = usock.read()
                # usock.close()
                # soup = BS(data, "html5lib")

                #check if not disallowed
                rp = robotparser.RobotFileParser()
                rp.set_url(url+ "/robots.txt")
                rp.read()
                allowed = rp.can_fetch('*','/'+link.url)
                print(allowed," ",link.url)
                if newurl not in visited and url in newurl and allowed:
                    visited.append(newurl)
                    urls.append(newurl)
                if not allowed:
                    disallowed.append(newurl)
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
        #print("!!",url)
        usock = urlopen(url)
        data = usock.read()
        usock.close()
        soup = BS(data, "html5lib")
        reg = re.search('([^\s]+(\.(?i)(txt|htm|html))$)',url)
        dup = False
        for link in soup.find_all('meta'):
            #if duplicate
            if link.get('content') in counts:
                duplicates.append(url)
                dup = True
            else:
                counts[link.get('content')] = 1
        if(reg and not dup):
            docIDs[ID] = url
            ID += 1
            text = soup.findAll(text=True)
            textJoined = ' '.join(text)
            words = re.split('\W+', textJoined, flags=re.IGNORECASE)
            # print("WORDS:")
            # print(words)
            filtered_words = [word for word in words if word not in
                set(stopwords.words('english'))]

            stemmed = []
            for word in filtered_words:
                if(len(word) > 1):
                    stemmed.append(stemmer.stem(word))
                    #print(word,stemmer.stem(word))

            #stemmed = [stemmer.stem(word) for word in words]
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
print("Doc IDs: ")
for key,val in docIDs.iteritems():
    print(str(key) + " : " + str(val))
print("Documents each word is on: ")
# for word in stemWordFreq:
#     print(word + " " + stemWordFreq[word])
print("word : freq")
for word in sorted(stemWordFreq, key=lambda word: len(stemWordFreq[word]),reverse=True):
    print(str(word) + " : " + str(len(stemWordFreq[word])))
print("URLS: ")
print(visited)
print("Outgoing: ")
print(outgoing)
print("Duplicates: ")
print(duplicates)
print("Disallowed: ")
print(disallowed)
#print(set(visited) - set(outgoing) - set(graphics))
