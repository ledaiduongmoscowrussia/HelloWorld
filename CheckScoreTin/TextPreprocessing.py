from nltk.tokenize import sent_tokenize
import pandas as pd
import json
import numpy as np

def DeleteWhiteSpace(str):
    for i in str:
        if i == ' ': str = str[1:]
        else: break
    str = str[::-1]
    for i in str:
        if i == ' ': str = str[1:]
        else: break
    str = str[::-1]
    return str
def DeleteListCharacterFromString(str, list_character):
    for character in list_character:
        str = str.replace(character, '')
    return str
def GetSubTextsInsighDelimitersToList(doc_str, list_delimiters,jump_value = 1,
                                get_head = True, get_tail = True):
    def GetListIndexOfDelimiters(doc_str, list_delimiters):
        def SearchForADelimiter(delimiter):
            list_index = []
            poiter = 0
            while (True):
                poiter = doc_str.find(delimiter, poiter + jump_value)
                if poiter != -1:
                    list_index.append(poiter)
                else:
                    break
            return list_index
        list_index = []
        for delimiter in list_delimiters:
            list_index = list_index + SearchForADelimiter(delimiter)
        list_index.append(0)
        list_index.append(len(doc_str))
        list_index.sort()
        return list_index
    list_index = GetListIndexOfDelimiters(doc_str, list_delimiters)
    list_index_forwards = list_index.copy()
    list_index_forwards.pop(0)
    list_index.pop(-1)
    list_sub_text = []
    for index, index_forward in zip(list_index, list_index_forwards):
        list_sub_text.append(doc_str[index:index_forward])
    if get_head == False:
        list_sub_text.pop(0)
    if get_tail == False:
        list_sub_text.pop(-1)
    return list_sub_text
def ProcessAExercise(Exercises):
    list_questions = GetSubTextsInsighDelimitersToList(Exercises,['Question'])
    header1 = DeleteWhiteSpace(DeleteListCharacterFromString(sent_tokenize(list_questions.pop(0).replace('\n', ' '), language='english')[0], ['\t'])).lower()
    def UniformAQuestion(question, header1):
        list_options = [DeleteWhiteSpace(DeleteListCharacterFromString(option.replace('\n', ' ').replace('/', ' ').replace('-', ' ').replace("’", "'"),
                                                                       ['\t', 'A.', 'B.', 'C.', 'D.', '(', ')', '.', ',', '?', '!', ';'] + list('1234567890'))).lower()
                        for option in GetSubTextsInsighDelimitersToList(question, ['A.', 'B.', 'C.', 'D.'])]
        header2 = DeleteWhiteSpace(DeleteListCharacterFromString(list_options.pop(0).replace('\n', ' '), list('1234567890') +['\t', 'question', ':'])).lower()
        dict_questions = {'header1': header1,
                         'header2': header2,
                         'options': list_options}
        return dict_questions
    list_uniformed_questions = []
    for question in list_questions:
        list_uniformed_questions.append(UniformAQuestion(question, header1))
    return list_uniformed_questions
def ExtractATestToDictionary(doc, list_delimiters_0, get_head=True, get_tail=True):
    list_exercises = GetSubTextsInsighDelimitersToList(doc, list_delimiters_0, get_head=get_head, get_tail=get_tail)
    list_total_questions = []
    for exercices in list_exercises:
        list_total_questions = list_total_questions + ProcessAExercise(exercices)
    dict_a_test = {}
    for i, question in list(enumerate(list_total_questions)):
        dict_a_test['question'+str(i+1)] = question
    return dict_a_test
def ConvertADictionaryToDataFrame(dict_a_test):
    list_all_questions = [dict_a_test['question' + str(i+1)] for i in range(0, 50)]
    index_data_frame = ['question' + str(i+1) for i in range(0, 50)]
    df = pd.DataFrame(list_all_questions, index=index_data_frame)
    return df
def ExtractAnswersFromText(Text):
    options = [x for x in Text if x in ['A', 'B', 'C', 'D']]
    return options
