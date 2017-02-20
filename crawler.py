import HTMLParser
import urllib
from HTMLParser import HTMLParser


urlText = []

#Define HTML Parser
class parseText(HTMLParser):

    def handle_data(self, data):
        if data != '\n':
            urlText.append(data)


#Create instance of HTML parser
lParser = parseText()

thisurl = "http://lyle.smu.edu/~fmoore"
#Feed HTML file into parser
lParser.feed(urllib.urlopen(thisurl).read())
lParser.close()
for item in urlText:
    print (item)
