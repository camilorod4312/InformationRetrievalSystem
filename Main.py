import math
import os
import re
import nltk
import numpy as np
from nltk.corpus import stopwords
from collections import Counter



def load_corpus(path:str):
	dic={}
	id=0
	for route, _ , archive in os.walk(path, topdown=True):
		for element in archive:
			_read = None
			try:
				_open=open(route+'/'+element)
				_read=_open.read()
				if _read != None:
					dic[id]=(element,_read)
					id+=1
			except:
				pass  
            	     
	return dic
	
def remove_symbols(doc):
	doc = re.sub(r'[^\w]',' ',doc)
	return doc

def get_token_list(doc):
	token_list = nltk.word_tokenize(str(doc))
	return token_list

def remove_stopwords(token_list):
	_stopwords = stopwords.words('english')
	removed_stopwords_list = []
	for word in token_list:
		if word not in _stopwords and len(word)>1:
			removed_stopwords_list.append(word)
	return removed_stopwords_list

def stemmer(token_list):
	porter_stemmer = nltk.stem.PorterStemmer()
	stemmed_token_list = []
	for word in token_list:
		stemmed_token_list.append(porter_stemmer.stem(word))
	return stemmed_token_list

def preprocess(doc):
	doc = doc.lower()
	doc = remove_symbols(doc)
	doc = get_token_list(doc)
	doc = remove_stopwords(doc)
	doc = stemmer(doc)
	return doc

def find_corpus_term_frecuency(preprocessed_corpus):
	ctf = {}
	for i in range(len(preprocessed_corpus)):
		doc = preprocessed_corpus[i]
		for word in doc:
			if word in ctf.keys():
				ctf[word].add(i)
			else:
				ctf[word] = {i}
	for i in ctf:
		ctf[i] = len(ctf[i])
	return ctf

def find_df(word,ctf):
	if word in ctf.keys():
		return ctf[word]
	else:
		return 0


def find_TF_IDF(preprocessed_corpus,ctf,vocabulary):
	doc_id=0
	total_size = len(preprocessed_corpus)
	vocab_size = len(vocabulary)
	TF_IDF_M = np.zeros((total_size,vocab_size))
	for i in range(total_size):
		doc = preprocessed_corpus[i]
		dtf = Counter(doc)
		maxf =1
		if len(dtf)>0:
			maxf = max(dtf.values())		
		for word in dtf:
			tf = dtf.get(word,0)/maxf
			df = find_df(word,ctf)
			idf = math.log10(total_size/df)
			index = vocabulary[word]
			TF_IDF_M[i][index]=tf*idf
	return TF_IDF_M

def cosin_similarity(x,y):
	if not np.any(x) or not np.any(y):
		return 0
	cs = np.dot(x,y)/(np.linalg.norm(x)*np.linalg.norm(y))
	return cs


def query_TF_IDF(preprocessed_query,ctf,vocabulary,total_size):
	vocab_size = len(vocabulary)
	TF_IDF_Q = np.zeros(vocab_size)
	dtf = Counter(preprocessed_query)
	maxf = 1
	if len(dtf)>0:
		maxf = max(dtf.values())
	for word in dtf:
		tf = dtf.get(word,0)/maxf
		df = find_df(word,ctf)
		idf = 0
		if df > 0:
			idf = math.log10((total_size)/(df))
			index = vocabulary[word]
			TF_IDF_Q[index]=tf*idf
	return TF_IDF_Q

def resolve_query(query,ctf,vocabulary,total_size,TF_IDF_M,k=20):
	preprocessed_query = preprocess(query)
	cosines_list = []
	query_vector = query_TF_IDF(preprocessed_query,ctf,vocabulary,total_size)
	for v in TF_IDF_M:
		cs = cosin_similarity(query_vector,v)
		if not re.search('^[0-9\.-]+$',str(cs)):
			cs = 0
		cosines_list.append(cs)
	new_cosines_list = np.array(cosines_list).argsort()[-k:][::-1]
	l = {}
	for a in new_cosines_list:
		cs = cosines_list[a]
		if cs>0:
			l[a] = cs
	return l


def init_all(path):
    corpus = load_corpus(path)
    preprocessed_corpus =[]
    for doc in corpus.values():
	    data = preprocess(doc[1])
	    preprocessed_corpus.append(data)
    corpus_term_frecuency = find_corpus_term_frecuency(preprocessed_corpus)
    vocabulary = {word:i for i,word in enumerate(corpus_term_frecuency.keys())}
    TF_IDF_M = find_TF_IDF(preprocessed_corpus,corpus_term_frecuency,vocabulary)
    return [corpus,preprocessed_corpus,corpus_term_frecuency,vocabulary,TF_IDF_M]
	
