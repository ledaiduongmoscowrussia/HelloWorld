import numpy as np
import pandas as pd
import ast
from nltk import word_tokenize, pos_tag
from Dataset import *
from TextPreprocessing import *
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
import functools
import operator
import itertools

def FirtsStepCategozineBySeaching(df):
    list_conditions = [lambda x: 'pronou' in x or 'pronunciation' in x, lambda x: 'stress' in x,
                       lambda x: 'read' in x and 'following' in x and 'correct' in x and 'answer' in x,
                       lambda x: 'need' in x and 'correct' in x, lambda x: 'word(s)' in x and 'closest' in x and 'meaning' in x,
                       lambda x: 'word(s)' in x and 'opposite' in x and 'meaning' in x,
                       lambda x: 'sentence' in x and ('combine' in x or ('closest' in x and 'meaning' in x)),
                       lambda x: 'response' in x]
    conditions = [df['header1'].apply(condition) for condition in list_conditions]
    choices = ['Pronunciation', 'Stress', 'Reading', 'Error_identification', 'Synonyms', 'Antonyms',
               'Sentence_transformation', 'Direct_indirect_sentence']
    df['Category'] = np.select(conditions, choices)
    return df[['options', 'Category']]

def ExtractFeaturesFromOptions(list_options):
    # Arguments list_options like ['yet', 'still' ,'untill', 'even']
    # Result list_numerical_lable like [19, 19, 19, 11]
    list_pos_tag = [pos_tag(word_tokenize(option)) for option in list_options]
    list_label = [option_and_pos_tag[1] for option in list_pos_tag for option_and_pos_tag in option]
    list_numerical_lable = sorted(list(LabelEncoderPosTag.transform(list_label)), key= int, reverse= True)
    return list_numerical_lable

def ConvertEnglishCategoryToNumber(lable):
    list_lable = [lable]
    list_numerical_lable = LabelEncoderEnglishCategory.transform(list_lable)
    number = list_numerical_lable[0]
    return number

def ConvertNumberToCategoricalData(number):
    list_number = [number]
    list_categorical_lable = LabelEncoderEnglishCategory.inverse_transform(list_number)
    category = list_categorical_lable[0]
    return category

def UniformFeature(feature, standart_length):
    length_intite = len(feature)
    uniformed_feature = np.zeros(standart_length)
    uniformed_feature[0:length_intite] = feature
    return uniformed_feature.tolist()

def ConvertATestToDictionary(text_exam, Answers, test_number):
    try:
        dict = ExtractATestToDictionary(text_exam, Answers, list_delimiters_0,test_number, get_head=False, get_tail=False)

    except KeyError:
        dict = ExtractATestToDictionary(text_exam, Answers, list_delimiters_0,test_number, get_head=True, get_tail=True)
    return dict

def FillHeader2(question, number_question):
    if DeleteListCharacterFromString(question['header2'], [' ']) == '':
        list_indexs = list(map(lambda x: x.find('('+str(number_question)+')'), question['header11']))
        print(list_indexs, number_question)
        index_header2 = list_indexs.index(list(filter(lambda x: x != -1, list_indexs))[0])
        question['header2'] = question['header11'][index_header2]
        return True
    return False
def RepairOption(options):
    a = ''
    for i in options:
        a = a + i + '>  <'
    return a

def CategorizePhysicsTest(Answers, text_exam):
    list_questions = GetSubTextsInsighDelimitersToList(text_exam , list_delimiters_physics, get_head= False, get_tail= False )
    df_result = pd.DataFrame()
    df_result['Index'] = list(range(1, 41))
    df_result['Header'] = list_questions
    df_result['Answers'] = Answers
    conditions = [df_result['Header'].apply(lambda raw_text_question: functools.reduce(operator.or_, map(functools.partial(lambda y, x: x in y, raw_text_question), list_indicator)))
                  for list_indicator in PhysicsIndicatorsList]
    df_result['Category'] = np.select(conditions, PhysicsCategory)
    return df_result.drop(['Header'], axis = 1)


