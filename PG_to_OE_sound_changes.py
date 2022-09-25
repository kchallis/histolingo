import urllib3, re
from  urllib.parse import quote_plus, unquote_plus
from bs4 import BeautifulSoup
from csv import DictReader, DictWriter

https = urllib3.PoolManager()

#there are some 3k pages of lists
def parse_one_list_page(url, term_list):
    response = https.request('GET', url)
    soup = BeautifulSoup(response.data, features="lxml")
    text_of_source_page = str(soup)
    # add stuff to list
    cleaned = re.findall(r'<div\sclass=\"mw-category-group.*<\/div><\/div><\/div>', text_of_source_page, flags=re.DOTALL)
    all_terms = re.findall(r'<li><a\shref=\"\/wiki\/([^\"]*)', cleaned[0], flags=re.DOTALL)
    terms = list(map(lambda x : re.sub(r'=\"\/wiki\/([^\"]*)', r'\1', x), all_terms))
    for term in terms:
        term_list.append(term)

    #this goes to the next page of terms
    next_url_suffix = re.findall(r'pagefrom=[^\"]*', text_of_source_page)
    if len(next_url_suffix) < 1:
        return None
    next_url = 'https://en.wiktionary.org/wiki/Category:Old_English_terms_derived_from_Proto-Germanic&' + next_url_suffix[0]
    return next_url

# This is a list of all the terms
term_list = []
current_url = 'https://en.wiktionary.org/wiki/Category:Old_English_terms_derived_from_Proto-Germanic'
i = 0
while i < len(term_list):
    current_url = parse_one_list_page(current_url, term_list)
    i += 1

#somewhere around here I need to fix it so that it iterates through the other pages

print(parse_one_list_page(current_url, term_list))

# this is the final dictionary
oepg_dict = {}
test_url = 'https://en.wiktionary.org/wiki/acol#Old_English'

#this is the function for scraping the terms from each page
def scrape_one_page(my_term):
    # REGEXES USED IN SEARCHES IN THIS FUNCTION

    # Real spelling used in 420
    # Latinx headword" lang="ang">([^<]*)

    # /IPA/

    # [IPA]

    # |Proto-x *word|

    # Prose of Etymology

    # Declension or Inflection or ?

    # Descendents

    # Related terms

    #This is before I did anything to it.
    my_url = f'https://en.wiktionary.org/wiki/{quote_plus(my_term)}#Old_English'
    response = https.request('GET', my_url)
    soup = BeautifulSoup(response.data, features="lxml")
    messy_text = str(soup)
    # this is if we want the Old English to be the way it is spelled
    # oe = re.sub(r'.*i/(.*)#.*', r'\1', my_url)
    # this is if we want the Old English to be by its IPA (apparently there are multiple IPAs used here?)
    tmp = re.findall(r'\"IPA\">[^<]*', messy_text)
    if len(tmp) == 0:
        return
    oe = re.sub(r"\"IPA\">", "", tmp[0])
    # print(oe)
    #oe = re.sub(r'\[(.*)\]', r'\1', messy_text)
    # print(oe)
    #messy_pg = str(re.findall(r'<p>(.*?)(Reconstruction:Proto-Germanic/(.*?)\")', messy_text))
    messy_pg = re.findall(r"<a href=\"/wiki/Reconstruction:Proto-Germanic/[^\"]*", messy_text)
    pg_list = list(map(lambda x: unquote_plus(re.sub(r"<a href=\"/wiki/Reconstruction:Proto-Germanic/", "", x)), messy_pg))
    #pg = re.sub(r'.*ic\/(.*)\".*', r'\1', messy_pg)
    # print(str(pg))



    for pg in pg_list:
        oepg_dict[oe] = pg

i=1
for term in term_list:
    print(f"page {i} of {len(term_list)}")
    scrape_one_page(term)
    i += 1
scrape_one_page(test_url)

with open("pgoe_words.txt", 'w') as writer:
    for term in oepg_dict.keys():
        writer.write(f"{term}\t{oepg_dict[term]}\n")

print(oepg_dict)
print(term_list)

#Things to do:

#1) fix the terms in the dictionary
#it turns out that the "terms" are not actually the list of terms with sites to scrape.
#this is because whoever wrote this wiki didn't want macrons in the title of the pages
#but we want them in our terms, so we will need to replace the page title terms with
#the one that is scraped from the "Latinx headword" regex.

#2) regexes
#add regexes to the scrape page function
#find out if this would be less hideous if they were called outside the function somewhere at the top
#so they wouldn't clutter the code? I don't know. Ask Piper?
#the regexes should be pretty simple, but a bit time consuming to figure out.
#what is more challenging (to me) will be to make sure that each term can be added to the dictionary.
#the structure of the dict will be {420-term : [list of things of interest]}. Currently, it's {key:term}, not
#{key: [list]} so I have to fix that somehow. Think about how that works...

#3) iterate through all the pages
#right now, the code is only going through a single page. Find out why and make it go through all
#the 3k-some-odd pages.

#4) what if it's not there
#remember to add cases for if the search turns up nothing.

#print(oe)