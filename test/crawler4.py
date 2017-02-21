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


# Since the amount of urls in the list is dynamic
#   we just let the spider go until some last url didn't
#   have new ones on the webpage
while len(urls)>0:
    try:
        br.open(urls[0])
        urls.pop(0)
        for link in br.links():
            newurl =  urlparse.urljoin(link.base_url,link.url)
            #print newurl
            if newurl not in visited and url in newurl:
                visited.append(newurl)
                urls.append(newurl)
                print(newurl)

    except:
        if(len(urls)>0):
            print("error"+ str(urls[0]))
            urls.pop(0)

parser = MyHTMLParser()
print(visited)
for url in visited:
    try:
        usock = urlopen(url)
        data = usock.read()
        usock.close()
        soup = BS(data, "html5lib")
        if(soup.find('title')):
            print soup.find('title').text
    except HTTPError, e:
        print e.code
        print e.msg
