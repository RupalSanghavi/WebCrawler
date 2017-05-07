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
import time
import sys

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
toVisit = []
visited = []
outgoing = []
graphics = []
duplicates = []
counts = {}
disallowed = []
maxPages = int(sys.argv[1])
query = ["moore","smu"]
# for i in range(2,len(sys.argv)):
#     query.append(sys.argv[i])
# print(query)
print("MaX: ", maxPages)
count = 0
broken = []

# Since the amount of urls in the list is dynamic
#   we just let the spider go until some last url didn't
#   have new ones on the webpage
while (len(urls)>0) and (count < maxPages):
    try:
        br.open(urls[0])
        count += 1
        urls.pop(0)
        try:
            for link in br.links():
                newurl =  urlparse.urljoin(link.base_url,link.url)
                #print("** ",newurl)
                #print("!! ", link.url)
                if url not in newurl:
                    outgoing.append(newurl)
                    visited.append(newurl)
                    toVisit.append(newurl)
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
                #print(allowed," ",link.url)
                if newurl not in visited and url in newurl and allowed:
                    toVisit.append(newurl)
                    visited.append(newurl)
                    urls.append(newurl)
                if not allowed:
                    disallowed.append(newurl)
                    visited.append(newurl)
        except mechanize._mechanize.BrowserStateError:
            print("Cannot crawl: " + str(urls[0]))
        # print("Delaying...")
        # time.sleep(0.2)
    except:
        if(len(urls)>0):
            broken.append(urls[0])
            print("Broken: "+ str(urls[0]))
            visited.append(urls[0])
            urls.pop(0)


parser = MyHTMLParser()
stemmer = PorterStemmer()
docIDs = {}
stemToIDs = {}
stemWordFreq = {}
removed_more_freq = {}
term_freq = {}
ID = 0
titles = {}
def visible(element):
    if element.parent.name in ['style', 'script', '[document]', 'head', 'title',
    'meta']:
        return False
    elif isinstance(element,bs4.element.Comment):
        return False
    return True

# print(visited)
for url in toVisit:
    if url == "mailto:fmoore@lyle.smu.edu":
        continue
    try:
        #print("!!",url)
        usock = urlopen(url)
        data = usock.read()
        usock.close()
        soup = BS(data, "html5lib")
        reg = re.search('([^\s]+(\.(?i)(txt|htm|html))$)',url)
        dup = False
        for link in soup.find_all('meta'):
            if(filter(visible,link)):
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
            removed_more = []
            for word in filtered_words:
                if(len(word) > 1 and not any(c.isdigit() for c in word)):
                    word = word.lower()
                    removed_more.append(word)
                    stemmed.append(stemmer.stem(word))
                    #print(word,stemmer.stem(word))
            for word in removed_more:
                if(removed_more_freq.get(word) == None):
                    removed_more_freq[word] = []
                    removed_more_freq[word].append(ID)
                    term_freq[word] = {}
                    term_freq[word][url] = 1
                else:
                    removed_more_freq[word].append(ID)
                    if(term_freq[word].get(url) == None):
                        term_freq[word][url] = 1
                    else:
                        term_freq[word][url] = term_freq[word][url] +1
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
            titles[url] = soup.find('title').text
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
print("Stemmed Words: ")
for word in stemmed:
    print word,
print("")
# for word in stemWordFreq:
#     print word, stemWordFreq[word]
count = 1
print("Word : Freq : Documents that word is on")
for word in sorted(removed_more_freq, key=lambda word: len(removed_more_freq[word]),reverse=True):
    print count, str(word),  " : ", str(len(removed_more_freq[word])), " : ",
    removed_more_freq[word]
    count += 1
print("Term Freqs: ")
for word in term_freq:
    print word
    for doc_url in term_freq[word]:
        print doc_url, str(term_freq[word][doc_url])
    print "*************"
# for word in sorted(stemWordFreq, key=lambda word: len(stemWordFreq[word]),reverse=True):
#     print count, str(word),  " : ", str(len(stemWordFreq[word])), " : ",stemWordFreq[word]
#     count += 1
print("Words:")
for word in removed_more:
    print word,
print("")
print("URLS: ")
for url in visited:
    print(url)
print("Titles: ")
for url in titles:
    print url, titles[url]
print("Outgoing: ")
for url in set(outgoing):
    print url
print("Duplicates: ")
for url in duplicates:
    print url
print("Disallowed: ")
print(disallowed)
print("Broken: ")
for url in broken:
    print(url)
print("Graphic Files: ")
print str(len(graphics))
for url in graphics:
    print(url)
#print(set(visited) - set(outgoing) - set(graphics))
