# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11 12:48:00 2019

@author: Gayatri
"""
import csv

from Model import get_word_props

file = open('Simple Words.csv', 'r', encoding = 'utf-8')
csv_reader = csv.reader(file, delimiter=',')
output_file = open("pilot_analysis_simple.csv", "w", encoding = "utf-8")
output_file.write("word,length,syllables,consonants,vowels,consonantconjuncts,count,senses,synonyms,hypernyms,hyponyms,authors,years,source\n")
	
for row in csv_reader:
	if row[1].strip() != '':
		word = row[1] #root
	else:
		word = row[0]
	data = get_word_props(word)['data']
	print(data)
	if data == None:
		continue
	length = data['length']
	syllables = data['syllables']
	consonants = data['consonants']
	vowels = data['vowels']
	consconjuncts = data['consonantconjuncts']
	count = data['word_count']
	sense_count = data['sense_count']
	synset_dict = data['synsets']
	synonyms = 0
	hypernyms = 0
	hyponyms = 0
	authors = "\""
	years = "\""
	source_category = "\""
	if synset_dict != '':
		for key,values in synset_dict.items():
			synonyms += int(values['synonymcount'])
			hypernyms += int(values['hypernyms'])
			hyponyms += int(values['hyponyms'])
	for author in data['author']:
		authors += author + ","
	authors = authors[:-1] + "\""
	for source in data['source_category']:
		source_category += source + ","
	source_category = source_category[:-1] + "\""
	for year in data['year']:
		years += year + ","
	years = years[:-1] + "\""
	output_file.write(word + "," + str(length) + "," + str(syllables) + "," + str(consonants) + "," + str(vowels) + "," + 
	str(consconjuncts) + "," + str(count) + "," + str(sense_count) + "," + str(synonyms) + "," + str(hypernyms) + "," + 
	str(hyponyms) + "," + authors + "," + years + "," + source_category+"\n")
