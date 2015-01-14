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
from pattern import web
from BeautifulSoup import BeautifulSoup

class Similarity:
    def basic_similarity(self, q1, q2, count):
        '''
            Calculate the Similarity using the Jaccard Coefficient
            Parameters:
            count: number of results to retrieve from twitter
            q1,q2: entities for which similarity is to be performed
        '''
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
    def get_urls_from_bing(query):
        print "Fetching URLs from Bing for Query:"+query
        url_list = []
        url = "http://www.bing.com/search"
        total_url = 0
        count = 0
        while total_url < 5:
            params = dict(q = query, first = count)
            count += 15
            print url
            r = requests.get(url, params = params)
            dom = web.Element(r.text)
            for results in dom.by_tag('li.b_algo'):
                result = results.by_tag('a')
                url_list.append(result[0].attributes.get('href',''))
                total_url += 1        
        print url_list
        return url_list

    @staticmethod
    def download_webpages(query, urls):
        i = 0
        for url in urls:
            print "Downloading Web Page:" + url
            r = requests.get(url)
            f = open('html_files/' + query + str(i) + ".html", 'w')
            bs = BeautifulSoup(r.text)
            plain_text = ''.join(bs.findAll(text=True))
            f.write(plain_text.encode('utf8'))
            f.close()
            i += 1
        return 

    def tfidf(self, query, total_doc):
        '''
            Calculate the tf-idf score of words in each doc and return
            top 50 words among them
        '''
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
        '''
            Calculate the centroid of the vectors for each query given by
            => [sum_of_all(vector(i))/|vector(i)|] / total_vectors
        '''
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
        '''
            dot product of both the centroids of the query terms
        '''
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
        total_pages = 7
        urls_query_1 = Similarity.get_urls_from_bing(q1)
        Similarity.download_webpages(q1, urls_query_1)
        cent1 = Similarity.calculate_centroid(self.tfidf(q1, total_pages))
        
        urls_query_2 = Similarity.get_urls_from_bing(q2)
        Similarity.download_webpages(q2, urls_query_2)
        cent2 = Similarity.calculate_centroid(self.tfidf(q2, total_pages))

        print self.similarity_kernel(cent1, cent2)    
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
