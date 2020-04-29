# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 13:38:09 2020

@author: ram
"""
#libraries
import pandas as pd
import numpy as np
import os
import requests
import sys
import nltk
import re 
from nltk.tokenize import sent_tokenize,word_tokenize
from nltk.tokenize import RegexpTokenizer
import string


#cik data
cik_list = pd.read_excel('cik_list.xlsx')
cik_list['SECFNAME']= 'https://www.sec.gov/Archives/'+cik_list['SECFNAME']


#stopword data
stop_words = open('StopWords_generic.txt')
stop_word =stop_words.read()
stop_words.close() 
stop_word=stop_word.lower()
stop_word=word_tokenize(stop_word)


#positve&negative words
df=pd.read_excel('LoughranMcDonald_SentimentWordLists_2018.xlsx',sheet_name=['Positive','Negative'],)
negative_words=df['Negative'].values.tolist()
negative_words=[str(w).strip('[]') for w in negative_words]
negative_words=[w.lower().strip('\'') for w in negative_words]

positive_words=df['Positive'].values.tolist()
positive_words=[str(w).strip('[]') for w in positive_words]
positive_words=[w.lower().strip('\'') for w in positive_words]


#constraining & uncertainty
const_words=pd.read_excel('constraining_dictionary.xlsx')
const_words=const_words['Word'].values.tolist()
const_words=[w.lower() for w in const_words]

uncer_words=pd.read_excel('uncertainty_dictionary.xlsx')
uncer_words=uncer_words['Word'].values.tolist()
uncer_words=[w.lower() for w in uncer_words]


#download and store data from given link
def get_data():
    i=0
    for i in range(len(cik_list)):
        url=cik_list.loc[i,'SECFNAME']
        data=requests.get(url)
        text_data=data.text
        x=open('edgar/{}.txt'.format(i),'w')
        x.write(text_data)
        x.close()
    sys.stdout.flush()
        
 
#store the raw data to list 
raw_data=[]
for i in range(len(cik_list)):
    data =open('C:/Users/ram/Desktop/R/blackcoffer/edgar/{}.txt'.format(i))
    raw=data.read()
    raw=raw.lower()
    data.close()
    raw_data.append(raw)
      

#section1:management decision&analysis
    
mda_regex = r"item[^a-zA-Z\n]*\d\s*\.\s*management\'s discussion and analysis.*?^\s*item[^a-zA-Z\n]*\d\s*\.*"

tok_mda = nltk.RegexpTokenizer(mda_regex)

mda_data=[]
for i in range(len(cik_list)):
    data=tok_mda.tokenize(raw_data[i])
    mda_data.append(data)
    
mda_data2=[]
for i in range(len(cik_list)):
    if len(mda_data[i])==2:
        data=mda_data[i][1]
    else:
        data=str(mda_data[i])
    mda_data2.append(data)


#sentences from MDA
mda_sent=[]
for i in range(len(cik_list)):
    sent=sent_tokenize(mda_data2[i])
    mda_sent.append(sent)
    
#words from MDA    
mda_words=[]
for i in range(len(cik_list)):
    words=word_tokenize(mda_data2[i])
    mda_words.append(words)

mda_words_clean=[]
for i in range(len(cik_list)):
    filt=[w for w in mda_words[i] if not w in stop_word]
    mda_words_clean.append(filt) 
    
    
    


#section2:Quantitative and Qualitative disclosure about market risk

qqd_regex = r"item[^a-zA-Z\n]*\d[a-z]?\.?\s*Quantitative and Qualitative Disclosures about " \
            r"Market Risk.*?^\s*item\s*\d\s*"

tok_qqd = nltk.RegexpTokenizer(qqd_regex)

qqd_data=[]
for i in range(len(cik_list)):
    data=tok_qqd.tokenize(raw_data[i])
    qqd_data.append(str(data))
    
    
qqd_words=[]
for i in range(len(cik_list)):
    words=word_tokenize(qqd_data[i])
    qqd_words.append(words)
    
qqd_sent=[]
for i in range(len(cik_list)):
    sent=str(sent_tokenize(qqd_data[i]))
    qqd_sent.append(sent)

    
    


#section3:Risk factors

risk_regex = r"item[^a-zA-Z\n]*\d[a-z]?\.?\s*Risk Factors.*?^\s*item\s*\d\s*"

tok_risk = nltk.RegexpTokenizer(risk_regex)

risk_data=[]
for i in range(len(cik_list)):
    data=tok_risk.tokenize(raw_data[i])
    risk_data.append(str(data))
    
    
risk_words=[]
for i in range(len(cik_list)):
    words=word_tokenize(risk_data[i])
    risk_words.append(words)


 
#words in the whole secn

words_whole=[]  
for i in range(len(raw_data)):
    words=word_tokenize(raw_data[i])
    words_whole.append(words)

for i in range(len(words_whole)):
    words_whole[i]=[w for w in words_whole[i] if w not in stop_word]


words_whole



#functions for score calculators    

def pos_calc(data,pos_words):
    pos_score=[]
    for i in range(len(data)):
        score=0
        for j in range(len(data[i])):
            if data[i][j] in pos_words:
                score+=1
        pos_score.append(score)
    return pos_score 



def neg_calc(data,neg_words):
    neg_score=[]
    for i in range(len(data)):
        score=0
        for j in range(len(data[i])):
            if data[i][j] in neg_words:
                score+=1
        neg_score.append(score)
    return neg_score 




def polarity_calc(a,b):
    polarity_score = (a-b)/((a+b)+0.000001)
    return polarity_score



def avg_sent_len(sent_data):
    avg_len=[]
    for i in range(len(sent_data)):
        total_len=0
        for j in range(len(sent_data[i])):
            total_len=total_len+len(sent_data[i][j].split())
        avg= (total_len/len(sent_data[i]))
        avg_len.append(avg)
    return(avg_len)


def complex_word_count(words_data):
    complex_words=[]
    for i in range(len(words_data)):
        complex_words_count=0
        for j in range(len(words_data[i])):
            v_count=0
            if words_data[i][j].endswith(('es','ed')):
                pass
            else:
                for w in words_data[i][j]:
                    if(w=='a' or w=='e' or w=='i' or w=='o' or w=='u'):
                        v_count +=1
            if v_count >=2:
                complex_words_count+=1
        complex_words.append(complex_words_count)
    return complex_words                
                    
def word_count(words_data):
    total_words=[]
    for i in range(len(words_data)):
        word_count=0
        for j in range(len(words_data[i])):
            if words_data[i][j] in string.punctuation:
                pass
            else:
                word_count +=1
        total_words.append(word_count)
    return total_words

def perc_comp_word(data_words):
    perc=[]
    a=complex_word_count(data_words)
    b=word_count(data_words)
    for i in range(len(data_words)):
        if a[i]>0 and b[i]>0:
            c=a[i]/b[i]
        else:
            c=0
        perc.append(c)
    return perc 
        
def fog_index(a,b):
    fog= (0.4)*(a+b)
    return(fog)  

def uncer_calc(data,uncer_words):
    uncer_score=[]
    for i in range(len(data)):
        score=0
        for j in range(len(data[i])):
            if data[i][j] in uncer_words:
                score+=1
        uncer_score.append(score)
    return uncer_score 


def constr_calc(data,const_words):
    constr_score=[]
    for i in range(len(data)):
        score=0
        for j in range(len(data[i])):
            if data[i][j] in const_words:
                score+=1
        constr_score.append(score)
    return constr_score       
                
                       
                         
                       
                       
                       
                       
                       
                       
                       
                       
#calculationg the score and appending to cik_list  
cik_list['mda_positive_score']=pos_calc(mda_words_clean,positive_words) 

cik_list['mda_negative_score']=neg_calc(mda_words_clean,negative_words)

cik_list['mda_polarity_score']=polarity_calc(cik_list['mda_positive_score'],cik_list['mda_negative_score'])

cik_list['mda_average_sentence_length']=avg_sent_len(mda_sent)

cik_list['mda_percentage_of_complex_words']=perc_comp_word(mda_words_clean)

cik_list['mda_fog_index']=fog_index(cik_list['mda_average_sentence_length'],cik_list['mda_percentage_of_complex_words'])

cik_list['mda_complex_word_count']=complex_word_count(mda_words_clean)

cik_list['mda_word_count']=word_count(mda_words_clean)

cik_list['mda_uncertainty_score']=uncer_calc(mda_words_clean,uncer_words)

cik_list['mda_constraining_score']=constr_calc(mda_words_clean,const_words)

cik_list['mda_positive_word_proportion']=cik_list['mda_positive_score']/cik_list['mda_word_count']

cik_list['mda_negative_word_proportion']=cik_list['mda_negative_score']/cik_list['mda_word_count']

cik_list['mda_uncertainty_word_proportion']=cik_list['mda_uncertainty_score']/cik_list['mda_word_count']

cik_list['mda_constraining_word_proportion']=cik_list['mda_constraining_score']/cik_list['mda_word_count']

cik_list['qqdmr_positive_score'] = pos_calc(qqd_words,positive_words)

cik_list['qqdmr_negative_score'] = neg_calc(qqd_words,negative_words)

cik_list['qqdmr_polarity_score'] = polarity_calc(cik_list['qqdmr_positive_score'],cik_list['qqdmr_negative_score'])

cik_list['qqdmr_average_sentence_length'] =avg_sent_len(qqd_sent)

cik_list['qqdmr_percentage_of_complex_words'] =perc_comp_word(qqd_words)

cik_list['qqdmr_fog_index'] =fog_index(cik_list['qqdmr_average_sentence_length'],cik_list['qqdmr_percentage_of_complex_words'])

cik_list['qqdmr_complex_word_count'] =complex_word_count(qqd_words)

cik_list['qqdmr_word_count'] =word_count(qqd_words)

cik_list['qqdmr_uncertainty_score'] =uncer_calc(qqd_words,uncer_words)

cik_list['qqdmr_constraining_score'] =constr_calc(qqd_words,const_words)

cik_list['qqdmr_positive_word_proportion'] =cik_list['qqdmr_positive_score']/cik_list['qqdmr_word_count']

cik_list['qqdmr_negative_word_proportion'] =cik_list['qqdmr_negative_score']/cik_list['qqdmr_word_count']

cik_list['qqdmr_uncertainty_word_proportion'] =cik_list['qqdmr_uncertainty_score']/cik_list['mda_word_count']

cik_list['qqdmr_constraining_word_proportion'] =cik_list['qqdmr_constraining_score']/cik_list['mda_word_count']

cik_list['rf_positive_score'] =pos_calc(risk_data,positive_words)

cik_list['rf_negative_score'] =neg_calc(risk_data,negative_words)

cik_list['rf_polarity_score'] =polarity_calc(cik_list['rf_positive_score'],cik_list['rf_negative_score'])

cik_list['rf_average_sentence_length'] =avg_sent_len(risk_data)

cik_list['rf_percentage_of_complex_words'] =perc_comp_word(risk_data)

cik_list['rf_fog_index'] =fog_index(cik_list['rf_average_sentence_length'],cik_list['rf_percentage_of_complex_words'])

cik_list['rf_complex_word_count'] =complex_word_count(risk_data)

cik_list['rf_word_count'] =word_count(risk_data)

cik_list['rf_uncertainty_score'] =uncer_calc(risk_data,uncer_words)

cik_list['rf_constraining_score'] =constr_calc(risk_data,const_words)

cik_list['rf_positive_word_proportion'] =cik_list['rf_positive_score']/cik_list['rf_word_count']

cik_list['rf_negative_word_proportion'] =cik_list['rf_negative_score']/cik_list['rf_word_count']

cik_list['rf_uncertainty_word_proportion'] =cik_list['rf_uncertainty_score']/cik_list['rf_word_count']

cik_list['rf_constraining_word_proportion'] =cik_list['rf_constraining_score']/cik_list['rf_word_count']

cik_list['constraining_words_whole_report'] =constr_calc(words_whole,const_words)



#writing output to csv file
cik_list.to_csv('textAnalysisOutput.csv', sep=',', encoding='utf-8')





