'''
Created on 29-Dec-2014

@author: akash
'''
from mrjob.job import MRJob
import re
import simplejson as json
from operator import itemgetter
from dns.name import empty

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
        list = []
        i = 0
        for word in word_count_pairs:
            print word[0],word[1]
            list.append(('a',i))
            i +=1
            if i > 10:
                break
        print list
        if list: 
            yield list.sort(key=lambda tup: tup[1])

    def steps(self):
        return [
            self.mr(mapper=self.mapper_get_words,
                    combiner=self.combiner_count_words,
                    reducer=self.reducer_count_words),
            self.mr(reducer=self.reducer_find_max_word)
        ]


if __name__ == '__main__':
    CountWords.run()