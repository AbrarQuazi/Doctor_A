import logging
from random import randint
from flask import Flask, render_template
from flask_ask import Ask, statement, question, session
import infermedica_api
import requests
import json
api = infermedica_api.API(app_id='b31c571d', app_key='240b0fc2f38307e25a7b5ab82199e961')
"""
print('Parse simple text:')
response = api.parse('i have a huge headache and couoghing today')
#print(response)
ids = []
length = len(response.mentions)
for i in range (0, length):
	if (response.mentions[i].choice_id == "present"):
		ids.append(response.mentions[i].id)
print ids[0]
print len(ids)

request = infermedica_api.Diagnosis(sex='male', age=35)

for i in range (0,len(ids)):
	request.add_symptom(ids[i],'present')

request = api.diagnosis(request)
print "hello" 
question = request.question.text
print type(question.encode('utf-8'))
print(request.question.items[0]['choices'])
print request.question.items[0]['choices'][0]['label']
print(request.conditions)
request.add_symptom(request.question.items[0]['id'], request.question.items[0]['choices'][1]['id'])
print(request.conditions)
print request.question.items[0]['id']
print(request.conditions[0]['name'])
print type(request.conditions[0]['name'])
"""
ids = []
request = infermedica_api.Diagnosis(sex='male', age=0)
app = Flask(__name__)

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)
chosen_gender = "none"
chosen_age = 0
total = 1
@ask.launch
def new_prediction():
	return question("Hello! My name is Doctor Alexa. Today I will be trying to diagnose your symptoms. In order to get a better idea of what is going on, I will be asking you some questions. Are you ready?")

@ask.intent("YesIntent")
def gender_question():
	return question("What is your gender?").reprompt("Could you please tell me your gender?")

@ask.intent("GenderIntent")
def age_question(gender):
	global chosen_gender 
	chosen_gender = gender
	return question("What is your age?").reprompt("Could you please tell me your age?")

@ask.intent("AgeIntent", convert={'age':int})
def symptom_question(age):
	global request
	request = infermedica_api.Diagnosis(sex=chosen_gender, age=age)
	request = api.diagnosis(request)
	return question("Please tell me about your symptoms?").reprompt("Could you please tell me your symptoms?")

@ask.intent("SymptomIntent", convert={'symptoms':str})
def process_symptom(symptoms):
	response = api.parse(symptoms)
	length = len(response.mentions)
	global request
	for i in range (0, length):
		if (response.mentions[i].choice_id == "present"):
			ids.append(response.mentions[i].id)

	for i in range (0,len(ids)):
		request.add_symptom(ids[i],'present')
	request = api.diagnosis(request)
	question1 = request.question.text.encode('utf-8')
	
	
	question_choices = " "
	if (len(request.question.items) == 1):
		question1 = question1 +" Please select the number with the best corresponding answer."
		for i in range (0, len(request.question.items[0]['choices'])):
			number = i + 1
			str_num = str(number)
			question_choices += str_num + " " + request.question.items[0]['choices'][i]['label'].encode('utf-8') + " , "
		question_choices += "."	
	else:
		question1 = question1 +" "+ request.question.items[0]['name'].encode('utf-8')+"? Please select the number with the best corresponding answer."
		for i in range (0, len(request.question.items[0]['choices'])):
			number = i + 1
			str_num = str(number)
			question_choices += str_num + " " + request.question.items[0]['choices'][i]['label'].encode('utf-8') + " , "
		question_choices += "."	
	
	print question_choices 
	print request.question
	return question(question1 + question_choices).reprompt("Could you please tell me your answer?")
@ask.intent("AnswerIntent", convert={'choice_number':int})
def diagnose(choice_number):
	global request
	request.add_symptom(request.question.items[0]['id'], request.question.items[0]['choices'][choice_number - 1]['id'])
	request = api.diagnosis(request)
	#result = request.conditions[0]['name'].encode('utf-8') + " probability is " + str(request.conditions[0]['probability'])
	question2 = request.question.text.encode('utf-8')
	
	
	question_choices = " "
	global total
	total += 1
	if (total >= 4):
		probability = request.conditions[0]['probability'] * 100
		condition_id = request.conditions[0]['id']
		result = "There is a " + str(probability) + " percent chance that you have " + request.conditions[0]['name'].encode('utf-8') + ". Please check up with your doctor for a more accurate diagnosis." 
		del request
		total = 1
		return statement(result).simple_card("Diagnosis Card",result)
	if (len(request.question.items) == 1):
		question2 = question2 +" Please select the number with the best corresponding answer."
		for i in range (0, len(request.question.items[0]['choices'])):
			number = i + 1
			str_num = str(number)
			question_choices += str_num + " " + request.question.items[0]['choices'][i]['label'].encode('utf-8') + " , "
		question_choices += "."	
	else:
		question2 = question2 +" "+ request.question.items[0]['name'].encode('utf-8')+"? Please select the number with the best corresponding answer."
		for i in range (0, len(request.question.items[0]['choices'])):
			number = i + 1
			str_num = str(number)
			question_choices += str_num + " " + request.question.items[0]['choices'][i]['label'].encode('utf-8') + " , "
		question_choices += "."	
	
	return question(question2 + question_choices).reprompt("Could you please tell me your answer?")

@ask.intent("AMAZON.StopIntent")
def stop():
	return statement("Stopping")




if __name__ == "__main__":
	app.run(debug=True)