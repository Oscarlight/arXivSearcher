"""
python_arXiv_paging_example.py

This sample script illustrates paging of arXiv api 
results.  In order to play nice with the api, we 
recommend that you wait 3 seconds between api calls.

Please see the documentation at 
http://export.arxiv.org/api_help/docs/user-manual.html
for more information, or email the arXiv api 
mailing list at arxiv-api@googlegroups.com.

urllib is included in the standard python library.
feedparser can be downloaded from http://feedparser.org/ .

Author: Julius B. Lucks

This is free software.  Feel free to do what you want
with it, but please play nice with the arXiv API!
"""

import urllib
import time
import feedparser
import pickle

def get_query(search_query, start, max_results):
    return 'search_query=%s&start=%i&max_results=%i'  \
            % (search_query, start, max_results)

def paging(keyword_lst, results_per_iteration, start = 0, total_results = None):
    '''
       paging the keywork list with OR
       get all the results up to this day if total_results is None
       return: a dictionary
    '''
    res_dict = {'id'             : [], 
                'title'          : [],
                'authors'        : [],
                'abstract'       : [],
                'abs_link'       : [],
                'journal_ref'    : [],
                'published_date' : []}

    # Base api query url
    base_url = 'http://export.arxiv.org/api/query?';

    # Search parameters
    search_query = reduce(lambda x, y :  x + '+OR+' + y, keyword_lst).replace(' ', '%20')
    wait_time = 3              

    print 'Searching arXiv for %s' % search_query

    ## find the total results:
    # Opensearch metadata such as totalResults, startIndex, 
    # and itemsPerPage live in the opensearch namespase.
    # Some entry metadata lives in the arXiv namespace.
    # This is a hack to expose both of these namespaces in
    # feedparser v4.1
    feedparser._FeedParserMixin.namespaces['http://a9.com/-/spec/opensearch/1.1/'] = 'opensearch'
    feedparser._FeedParserMixin.namespaces['http://arxiv.org/schemas/atom'] = 'arxiv'
    # perform a GET request using the base_url and query
    response = urllib.urlopen(base_url+get_query(search_query, start, 1)).read()
    # parse the response using feedparser
    feed = feedparser.parse(response)

    # print out feed information
    print 'Feed title: %s' % feed.feed.title
    print 'Feed last updated: %s' % feed.feed.updated
    # print opensearch metadata
    _total_results = feed.feed.opensearch_totalresults
    print 'totalResults for this query: %s' % _total_results

    if total_results is None:
        total_results = int(_total_results)

    for i in range(start,total_results,results_per_iteration):
        
        print "Results %i - %i" % (i,i+results_per_iteration)
        
        query = get_query(search_query, i, results_per_iteration)

        # perform a GET request using the base_url and query
        response = urllib.urlopen(base_url+query).read()
        # parse the response using feedparser
        feed = feedparser.parse(response)

        # Run through each entry, and print out information
        for entry in feed.entries:
            # id
            arxiv_id      = entry.id.split('/abs/')[-1]
            res_dict['id'].append(arxiv_id)
            
            # title
            title         = entry.title
            res_dict['title'].append(title)

            # list of all authors
            authors = ''            
            try:
                authors = ', '.join(author.name for author in entry.authors)
            except AttributeError:
                pass
            res_dict['authors'].append(authors)

            # abstract
            abstract = ''
            try:
                abstract  = entry.summary
            except AttributeError:
                pass
            res_dict['abstract'].append(abstract)

            # link to the abstract page
            abs_link = ''
            for link in entry.links:
                if link.rel == 'alternate':
                    abs_link = link.href
            res_dict['abs_link'].append(abs_link)

            # journal_ref
            journal_ref = ''
            try:
                journal_ref = entry.arxiv_journal_ref
            except AttributeError:
                pass
            res_dict['journal_ref'].append(journal_ref)

            # published date
            published_date = ''
            try:
                published_date = entry.published
            except AttributeError:
                pass
            res_dict['published_date'].append(published_date)

        # Remember to play nice and sleep a bit before you call
        # the api again!
        time.sleep(wait_time)

    return res_dict
    
if __name__ == '__main__':
    keyword_lst = ['all:TFET', 'all:Tunnel FET', 'all:TFETs', 'all:Tunnel FETs']
    data = paging(keyword_lst, 1000, total_results = None)
    with open('papers.p', 'w') as f:
        pickle.dump(data, f)


