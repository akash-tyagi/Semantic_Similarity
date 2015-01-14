'''
Created on 29-Dec-2014

@author: akash
'''
from mrjob.job import MRJob
import re
import simplejson as json
from operator import itemgetter

class CountWords(MRJob):
    '''
    To fing the top 10 most frequent word
    '''
    def mapper_get_words(self, _, line):
        # yield each word in the line
        text=json.loads(line)['text']
        for word in re.findall(r'\w+',text.lower()):
            yield (word.lower(), 1)

    def combiner_count_words(self, word, counts):
        # optimization: sum the words we've seen so far
        yield (word, sum(counts))

    def reducer_count_words(self, word, counts):
        # send all (num_occurrences, word) pairs to the same reducer.
        # num_occurrences is so we can easily use Python's max() function.
        yield None, (word, sum(counts))

    # discard the key; it is just None
    def reducer_find_max_word(self, _, word_count_pairs):
        list = sorted(word_count_pairs, key=itemgetter(1),reverse=True)[:10]
        for a in list:
            print a
        yield "max words:", list
    
    def steps(self):
        return [
            self.mr(mapper=self.mapper_get_words,
                    combiner=self.combiner_count_words,
                    reducer=self.reducer_count_words),
            self.mr(reducer=self.reducer_find_max_word)
        ]


if __name__ == '__main__':
    CountWords.run()