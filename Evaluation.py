from Main import *
import math
import sys
import time

def load_test(file_path):
	_open=open(file_path)
	_read=_open.read()
	temp = _read.split('.I ')
	files={}
	for i in range(1,len(temp)):
		file_name=""
		doc_index = 0
		while(temp[i][doc_index].isdigit()):
			digit = temp[i][doc_index]
			doc_index+=1
			file_name+=digit
		file_data=temp[i][doc_index:]
		files[i-1]=(file_name,file_data)
	return files

def cumulative_sum(lst):
    total, result = 0, []
    for ele in lst:
        total += ele		
        result.append(total)        
    return result

def NDCG(score_list):
	N = len(score_list)
	DCGK = []
	IDCGK = []
	ideal_score_list = sorted(score_list,reverse=True)
	for i in range(1,N+1):
		DCGK.append(score_list[i-1]/math.log2(i+1))
		IDCGK.append(ideal_score_list[i-1]/math.log2(i+1))
	newDCGK = cumulative_sum(DCGK)
	newIDCGK = cumulative_sum(IDCGK)
	NDCGK = []
	for i in range(N):
		if newIDCGK[i]!=0:
			NDCGK.append(newDCGK[i]/newIDCGK[i])
		else:
			NDCGK.append(0)
	return sum(NDCGK)/N

def score (keyFileName, response,total_queries,total_documents):
	keyFile = open(keyFileName, 'r')
	key = keyFile.readlines()
	key_dict = {}
	response_dict = {}
	all_precisions = []
	all_recalls = []
	all_F1=[]
	all_NDCGK=[]
	missing_responses = []
	for line in key:
		line = line.rstrip(os.linesep)
		line = line.split()
		query=int(line[0])
		abstract = int(line[1])
		score=int(line[2]) 
		if abstract <= total_documents:
			if query in key_dict:
				if not abstract in key_dict[query]:
					key_dict[query].append((abstract,score))
			else:
				key_dict[query] = [(abstract,score)]

	for line in response:
		line = line.rstrip(os.linesep)
		line = line.rstrip(' ')
		query,abstract,score = re.split(' +',line)
		if not (query.isdigit() and abstract.isdigit() and re.search('^[0-9\.-]+$',score)):
			print('Warning: Each line should consist of 3 numbers with a space in between')
			print('This line does not seem to comply:',line)
			exit()
		query = int(query)
		abstract = int(abstract)
		score = float(score)
		if query in response_dict:
			if not abstract in response_dict[query]:
				response_dict[query].append(abstract)
		else:
			response_dict[query] = [abstract]

	for query_id in range(1,total_queries):
		if (query_id in key_dict):
			total_answers =	len(key_dict[query_id])
		else:
			total_answers = 0
		if (query_id in key_dict) and (query_id in response_dict):
			correct = 0
			incorrect = 0
			precisions = []
			recordable_recall = 0
			score_list = []
			for abstract_id in response_dict[query_id]:
				key_ids,key_scores = zip(*key_dict[query_id])
				if abstract_id in key_ids:	
					score_list.append(key_scores[key_ids.index(abstract_id)])
					correct = correct + 1			
					recall = float(correct)/float(total_answers)
					if (correct+incorrect)<=total_answers:
						recordable_recall = recall
					precisions.append(float(correct)/float(correct+incorrect))
				else:
					score_list.append(0)				
					incorrect = incorrect+1
			if len(precisions)>0:
				all_NDCGK.append(NDCG(score_list))
				average_precision = (sum(precisions))/len(precisions)
				all_F1.append((2*average_precision*recordable_recall)/(average_precision+recordable_recall))
			else:
				all_NDCGK.append(0)
				missing_responses.append(query_id)
			all_precisions.append(average_precision)
			all_recalls.append(recordable_recall)
		elif query_id in key_dict:
			all_recalls.append(0)
		
	print('Queries with No responses:'+str(missing_responses))
	MAP = sum(all_precisions)/len(all_precisions)
	Recall = sum(all_recalls)/len(all_recalls)
	F1 = sum(all_F1)/len(all_F1)
	ANDCG = sum(all_NDCGK)/len(all_NDCGK)
	print('Mean Average Precision ------------------------- '+str(MAP))
	print('Average Recall --------------------------------- '+str(Recall))
	print('Average F1 ------------------------------------- ' + str(F1))
	print('Average Normalized Discounted Cumulative Gain -- '+str(ANDCG))
	print('This test took %s seconds' % ( time.time()-start_time))

args = sys.argv
start_time = time.time()
currentfolder = os.getcwd().replace(os.sep,'/')
test_collections = {
	'cran': ['/Test_Collections/Cranfield/cran.all.1400','/Test_Collections/Cranfield/cranQry.txt','/Test_Collections/Cranfield/cranswers.txt'],
	'cisi': ['/Test_Collections/CISI/CISI.ALL','/Test_Collections/CISI/CISI_queries.txt','/Test_Collections/CISI/CISI_answers.txt'],
	'adi': ['/Test_Collections/Adi/ADI.ALL','/Test_Collections/Adi/ADI.Qry','/Test_Collections/Adi/ADI.Rel'],
	'med': ['/Test_Collections/med/MED.ALL','/Test_Collections/med/MED.Qry','/Test_Collections/med/MED.Rel.Old'],
	'cacm': ['/Test_Collections/CACM/cacm.ALL','/Test_Collections/CACM/query.text','/Test_Collections/CACM/qrels.text'],
	'npl': ['/Test_Collections/NPL/docs.txt','/Test_Collections/NPL/query-text','/Test_Collections/NPL/query_rel.txt']
}
if len(args)>1:
	curr_collection = test_collections.get(args[1].lower(),test_collections['cran']) #Default Test is Cranfield
else:
	curr_collection = test_collections['cran']
_file = currentfolder+curr_collection[0]
queries_doc = currentfolder+curr_collection[1]
answers_doc = currentfolder+curr_collection[2]

corpus = load_test(_file)
preprocessed_corpus =[]
for doc in corpus.values():
	data = preprocess(doc[1])
	preprocessed_corpus.append(data)
corpus_term_frecuency = find_corpus_term_frecuency(preprocessed_corpus)
vocabulary = {word:i for i,word in enumerate(corpus_term_frecuency.keys())}
TF_IDF_M = find_TF_IDF(preprocessed_corpus,corpus_term_frecuency,vocabulary)

query_open = open(queries_doc)
query_load = query_open.readlines()
final_query_load={}
for i in range(0,len(query_load),2):
	final_query_load[int(query_load[i])] = query_load[i+1]

final_answer = []
for q in range(1,len(final_query_load)):
	query=resolve_query(final_query_load[q],corpus_term_frecuency,vocabulary,len(preprocessed_corpus),TF_IDF_M)	
	for i in query:
		final_answer.append(str(str(q) + " "+ corpus[i][0])+ " "+ str(query[i]) )



score(answers_doc,final_answer,len(final_query_load),len(preprocessed_corpus))



