'''
Created on 03-Nov-2014

@author: akash
'''
from __future__ import division
from hw1 import Hw1 
from twitter_crawler import TwitterCrawler
from search import GoogleSearch, SearchError
import requests
from math import log
from collections import defaultdict
from operator import itemgetter
from bs4 import BeautifulSoup
from pygoogle import pygoogle
    
class Similarity:
    def basic_similarity(self, q1, q2, count):
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
        print "Fetching URLs for "+query
        url_list = []
#         try:
#             gs = GoogleSearch(query)
#             gs.results_per_page = 5
#             results = []
#             while len(results) < 5:
#                 tmp = gs.get_results()
#                 if not tmp:  # no more results were found
#                     print "no results found"
#                     break
#                 results.extend(tmp)
#         except SearchError, e:
#             print "Search failed: %s" % e

        g = pygoogle(query)
        g.pages = 2
        print '*Found %s results*'%(g.get_result_count())
        for res in g.get_urls():
            print res
            url_list.append(res.url)
        return url_list

    @staticmethod
    def download_webpages(query, urls):
        print "Downloading web pages"
        i = 0
        for url in urls:
            print "TESTING ON:" + url
            r = requests.get(url)
            f = open('html_files/' + query + str(i) + ".html", 'w')
            f.write(r.text.encode('utf8'))
            f.close()
            i += 1
        return 

    @staticmethod
    def stripHtmlTags(htmlTxt):
        if htmlTxt is None:
            return None
        else:
            return ''.join(BeautifulSoup(htmlTxt).findAll(text=True)) 
    
    def tfidf(self, query, total_doc):
        tf = defaultdict(dict)
        idf = {}  # idf dictionary of terms
        for i in range(total_doc):
            doc_name = 'html_files/' + query + str(i) + ".html"
            line = open(doc_name, 'r').read()
            r_id = doc_name
#             line = Similarity.stripHtmlTags(BeautifulSoup(line).body_tag.string)
#             print line
            line = Hw1.tokenize(line)
            line = Hw1.stopword(line)
#                 line = Hw1.stemming(line)
            for word in line:
                if word in tf[r_id].keys():
                    tf[r_id][word] += 1
                else:
                    tf[r_id][word] = 1
                    # if show up first time in a document, count idf++
                    if word in idf.keys():
                        idf[word] += 1
                    else:
                        idf[word] = 1
        print "done with tfidf"
        for key, value in idf.iteritems():
            idf[key] = (1 + log(total_doc / value))  # idf defination:number of document/ number of document has the key
                  
        for key, value in tf.iteritems():
            sum_tfidf = 0
            for word, tfreq in value.iteritems():
                tf[key][word] = tfreq * idf[word]
                sum_tfidf += (tfreq * idf[word]) ** 2
            sum_tfidf = sum_tfidf ** 0.5 
            # normalize the tfidf vector to unit length
            for word, tfidf in value.iteritems():
                tf[key][word] = tf[key][word] / sum_tfidf
        
        for doc,dic in tf.iteritems():
            tf[doc]=sorted(dic.iteritems(), key=itemgetter(1),reverse=1)[0:50] #they shown up in pairs, so keep 20.
            print tf[doc]
            for a,b in tf[doc]:
                print "for "+doc+":" + a 

        return tf
    
    @staticmethod
    def calculate_centroid(tf):
        centroid = {}
        sum = 0
        for key,value in tf.iteritems():
            for (word, tfreq) in value:
                if word in centroid.keys():
                    centroid[word] += 1
                else:
                    centroid[word] = 1
        
        for word in centroid.keys():
            centroid[word] = centroid[word] / len(tf)
            sum += centroid[word] ** 2
            
        for word in centroid.keys():
            centroid[word] = centroid[word]/sum
        
        return centroid
            
    @staticmethod
    def similarity_kernel(cent1, cent2):
        val = 0
        intersect = [key for key in cent1.keys() if key in cent2.keys()]
        for word in intersect:
            val += cent1[word]* cent2[word]
        return val;
         
    def improved_similarity(self, q1, q2):
        '''
        improved similarity function taken from the 'A Web-based Kernel Function 
        for Measuring the Similarity of Short Text Snippets' paper
        '''
        urls_query_1 = Similarity.get_urls_from_google(q1)
#         Similarity.download_webpages(q1, urls_query_1)
#         cent1 = Similarity.calculate_centroid(self.tfidf(q1, len(urls_query_1)))
        
        urls_query_2 = Similarity.get_urls_from_google(q2)
#         Similarity.download_webpages(q2, urls_query_2)
#         cent2 = Similarity.calculate_centroid(self.tfidf(q2, len(urls_query_2)))

#         print self.similarity_kernel(cent1, cent2)    
        return
        
def main():
    q = ["Bill Gates", "Microsoft CEO", "Satya Nadella", "US President",
         "Barack Obama", "George Bush", "soccer", "football", "aggies",
         "lnghorns", "kevin sumlin"]
    q1 = q[0]
    q2 = q[2]
    sim_fun = Similarity()
#     sim_fun.basic_similarity(q1,q2, 1)
#     sim_fun.basic_similarity(q1,q2, 3)
#     sim_fun.basic_similarity(q1,q2, 50)
    sim_fun.improved_similarity(q1, q2)
        
if __name__ == "__main__":
    main()
