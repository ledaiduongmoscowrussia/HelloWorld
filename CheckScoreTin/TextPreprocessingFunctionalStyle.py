from nltk.tokenize import sent_tokenize
import pandas as pd
import json
import numpy as np
from FunctionalProgramming import *
from pprint import pprint
def DeleteWhiteSpaceInFrontAndBack(str):
    # This function use to delete white space in front and in back of a list string
    # Input : str = '    In put    '
    # Out put : str = 'In put'
    not_white_space = [i for i in str if i != ' ']
    if len(not_white_space) != 0: str = str[str.find(not_white_space[0]) : str.rfind(not_white_space[-1]) + 1]
    return str

def DeleteListCharacterFromString(str, list_character):
    # Delete specific character from a string
    # Input: str = string, list_character = [ ',', '.' ]
    # Output: str is string with out deleted strings
    for character in list_character: str = str.replace(character, '')
    return str

def FindSingleIndexOfString(str, delimeter, start_index):
    # Find index of string
    # Input: str is string you want to search in, delimeter is what do you want to search,
    # start_index is from where do you want to search
    # Output : index of string you want to search
    return str.find(delimeter, start_index + 1)

def FindListIndexOfString(str, delimeter):
    # Return list of indexs that consist the positions of delimeter, that includes the inatial index 0
    # Input: str is tring, delimeter is what do you want to search
    # Output: list of strings includes inatial value 0, for example delimeter has index 3, output will be [0, 3]
    return list(accumulate(iterate(partial(FindSingleIndexOfString, str, delimeter), 0), ConditionToStopIterationForSearchString))

def GetSubTextsInsighDelimitersToList(doc_str, list_delimiters, get_head = True, get_tail = True):
    list_indexs = sorted(list(set([i for k in [FindListIndexOfString(doc_str, delimeter) for delimeter in list_delimiters] for i in k ])) + [len(doc_str)])
    list_sub_text = [doc_str[list_indexs[i] : list_indexs[i+1]] for i in range(len(list_indexs) - 1)]
    if get_head == False: list_sub_text.pop(0)
    if get_tail == False: list_sub_text.pop(-1)
    return list_sub_text

def ProcessAExercise(Exercises):
    list_questions = GetSubTextsInsighDelimitersToList(Exercises,['Question'])
    header1_header11 = sent_tokenize(list_questions.pop(0).replace('\n', ' '))
    header1 = DeleteWhiteSpaceInFrontAndBack(DeleteListCharacterFromString(header1_header11.pop(0), ['\t'])).lower()
    header11 = header1_header11
    def UniformAQuestion(question, header1, header11):
        list_options = [DeleteWhiteSpaceInFrontAndBack(DeleteListCharacterFromString(option.replace('\n', ' ').replace('/', ' ').replace('-', ' ').replace("’", "'"), ['\t', 'A.', 'B.', 'C.', 'D.', '(', ')', '.', ',', '?', '!', ';'] + list('1234567890'))).lower()
                        for option in GetSubTextsInsighDelimitersToList(question, ['A.', 'B.', 'C.', 'D.'])]
        header2 = DeleteWhiteSpaceInFrontAndBack(DeleteListCharacterFromString(list_options.pop(0).replace('\n', ' '), list('1234567890') +['\t', 'question', ':'])).lower()
        dict_questions = {'header1': header1,'header11': header11,'header2': header2, 'options': list_options}
        return dict_questions
    list_uniformed_questions = [UniformAQuestion(question, header1, header11) for question in list_questions]
    return list_uniformed_questions

def ExtractATestToDictionary(text_exam, Answers, list_delimiters_0, test_number, get_head=True, get_tail=True):
    list_exercises = GetSubTextsInsighDelimitersToList(text_exam, list_delimiters_0, get_head=get_head, get_tail=get_tail)
    list_total_questions = []
    for exercices in list_exercises: list_total_questions = list_total_questions + ProcessAExercise(exercices)
    dict_a_test = {}
    for i, question in list(enumerate(list_total_questions)): dict_a_test['question'+str(i+1)] = question
    dict_a_test['test_number'] = test_number
    dict_a_test['Answers'] = Answers
    return dict_a_test

def ConvertADictionaryToDataFrame(dict_a_test):
    list_all_questions = [dict_a_test['question' + str(i+1)] for i in range(0, 50)]
    index_data_frame = ['question' + str(i+1) for i in range(0, 50)]
    df = pd.DataFrame(list_all_questions, index=index_data_frame)
    return df

def ExtractAnswersFromText(Text):
    options = [x for x in Text if x in ['A', 'B', 'C', 'D']]
    return options
