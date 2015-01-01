'''
Created on 03-Nov-2014

@author: akash
'''
from hw1 import Hw1 
from twitter_crawler import TwitterCrawler
from search import GoogleSearch, SearchError
import requests

class Similarity:
    @staticmethod
    def basic_similarity(q1, q2, count):
        tc = TwitterCrawler()
        tweets = tc.search_query(q1, count)
        text = tc.get_single_string_for_tweets(tweets)
        words1 = Hw1.stopword(Hw1.stemming(Hw1.tokenize(text)))
        
        tweets = tc.search_query(q2, count)
        text = tc.get_single_string_for_tweets(tweets)
        words2 = []
        words2 = Hw1.stopword(Hw1.stemming(Hw1.tokenize(text)))

        print words1
        print len(words1)
        print words2
        print len(words2)
        
        inter = [word for word in words1 if word in words2]
        inter = list(set(inter))
        print len(inter)
        union = list(set(words1 + words2))
        print len(union)
        print float(len(inter)) / len(union)
        return
    
    @staticmethod
    def get_urls_from_google(query):
        url_list = []
        try:
            gs = GoogleSearch(query)
            gs.results_per_page = 100
            results = []
            while len(results) < 5:
                tmp = gs.get_results()
                if not tmp:  # no more results were found
                    break
                results.extend(tmp)
        except SearchError, e:
            print "Search failed: %s" % e
        for res in results:
            url_list.append(res.url)
        return url_list

    @staticmethod
    def download_webpages(query, urls):
        i = 1
        for url in urls:
            print "TESTING ON:"+url
            r = requests.get(url)
            f = open('html_files/'+query+str(i)+".html", 'w')
            f.write(r.text.encode('utf8'))
            i += 1
        return  
                    
    @staticmethod
    def improved_similarity(q1, q2):
        '''
        improved similarity function taken from the 'A Web-based Kernel Function for Measuring the Similarity
        of Short Text Snippets' paper published
        '''
        urls_query_1 = Similarity.get_urls_from_google(q1)
        Similarity.download_webpages(q1, urls_query_1)
        hw1 = Hw1()
#         urls_query_2 = Similarity.get_urls_from_google(q1)
        return
        
def main():
    q = ["Bill Gates", "Microsoft CEO", "Satya Nadella", "US President",
         "Barack Obama", "George Bush", "soccer", "football", "aggies",
         "lnghorns", "kevin sumlin"]
    q1 = q[0]
    q2 = q[1]
#     Similarity.basic_similarity(q1,q2, 1)
#     Similarity.basic_similarity(q1,q2, 3)
#     Similarity.basic_similarity(q1,q2, 50)
    Similarity.improved_similarity(q1, q2)
        
if __name__ == "__main__":
    main()
