import warnings;warnings.filterwarnings('ignore')
from datetime import datetime
from mongdb import *
from NatureLanguageProcessing import *
from google.cloud import bigquery
import pprint

def GetStudentObject(tab):
    if tab == Subjects[0]: return EnglishStudent()
    elif tab == Subjects[1]: return MathStudent()
    elif tab == Subjects[2]: return PhysicsStudent()

def GetTeacherObject(tab):
    if tab == Subjects[0]: return EnglishTeacher()
    elif tab == Subjects[1]: return MathTeacher()
    elif tab == Subjects[2]: return PhysicsTeacher()


class Person():
    def __init__(self, file_raw_data, tab, number_rows_of_own_one_test ):
        self.tab = tab
        self.file_raw_data = file_raw_data
        self.number_rows_of_own_one_test = number_rows_of_own_one_test

    def CheckComponentsToGetRawData(self, test_number, complete_confirm):
        df_file_raw_data = self.ReadDataFrameFromMySQL(self.file_raw_data)
        check_test_number = str(int(len(df_file_raw_data) / self.number_rows_of_own_one_test) + 1) == test_number
        if check_test_number is False: return 'Status: Test number is wrong, you need to choose your right test number'
        completed = complete_confirm == 'I have done'
        if completed is False: return 'Status: You do not complete your test, click to <I have done> to confirm your completion'
    def GetNumberOfDoneTests(self, file):
        df = pd.read_gbq('select * from CheckScoreTin.' + file + ' order by id',
                         project_id='artful-journey-197609')
        number_done_test_your = int( len(df) / self.number_rows_of_own_one_test)
        return number_done_test_your

    def StreamData(self, dataset_id, table_id, rows):
        bigquery_client = bigquery.Client()
        dataset_ref = bigquery_client.dataset(dataset_id)
        table_ref = dataset_ref.table(table_id)
        # Get the table from the API so that the schema is available.
        table = bigquery_client.get_table(table_ref)
        errors = bigquery_client.create_rows(table, rows)
        if not errors:
            print('Loaded 1 row into {}:{}'.format(dataset_id, table_id))
        else:
            print('Errors:')
            pprint(errors)

    def ReadDataFrameFromMySQL(self, path):
        df = pd.read_gbq('SELECT * FROM CheckScoreTin.' + path + ' ORDER BY id ', 'artful-journey-197609').drop(
            ['id'], axis=1)
        return df

    def WriteDataFrimeToSQLDatabase(self, df, table):
        df.insert(loc=0, column='id', value=range(df.shape[0]))
        df.to_gbq('CheckScoreTin.' + table, 'artful-journey-197609', if_exists='replace')

class Teacher(Person):
    def __init__(self, file_raw_data, tab, number_rows_of_own_one_test, categories_of_subject, number_questions_of_subject):
        self.categories_of_subject = categories_of_subject
        self.number_questions_of_subject = number_questions_of_subject
        Person.__init__(self,file_raw_data= file_raw_data, tab= tab, number_rows_of_own_one_test = number_rows_of_own_one_test)
    def UpdateRawDataForClass(self, Answers, Categories):
        Answers = Answers[0:self.number_questions_of_subject]
        Categories = Categories[0:self.number_questions_of_subject]
        for option in zip(Answers, Categories):
            if option == None or len(option) != 2 :
                return 'Status: Anwers form is wrong, you need to repair your anwers'
            elif option[0] not in Options or option[1] not in self.categories_of_subject:
                return 'Status: Anwers form is wrong, you need to repair your anwers'
        num_test_done = self.GetNumberOfDoneTests(self.file_raw_data)
        self.StreamData('CheckScoreTin', self.file_raw_data, [[num_test_done] + Answers])
        self.StreamData('CheckScoreTin', self.file_raw_data, [[num_test_done + 1] + Categories])
        return 'Status: Your test is sent successfully, if you want to do next test you must click round button in top left conner to reload webpage'

class Student(Person):
    def __init__(self, file_raw_data, tab, number_rows_of_own_one_test, number_questions_of_subject):
        self.number_questions_of_subject = number_questions_of_subject
        Person.__init__(self,file_raw_data= file_raw_data, tab= tab, number_rows_of_own_one_test= number_rows_of_own_one_test)
    def UpdateRawDataForClass(self, list_options, test_number):
        for option in list_options:
            if option != None:
                if option not in Options or len(option) != 1:
                    return 'Status: You need to click round button in top left conner to reload webpage'
        list_options = list_options[0: self.number_questions_of_subject]
        list_options = [datetime.now()] + list_options
        self.StreamData('CheckScoreTin', self.file_raw_data, [[test_number] + list_options])
        return 'Status: Your test is sent successfully, if you want to do next test you must click round button in top left conner to reload webpage'

class EnglishTeacher(Teacher):
    def __init__(self):
        self.tab = 'English teacher'
        self.file_raw_data = 'EnglishTeacherCategories'
        self.number_rows_of_own_one_test = 2
        self.categories_of_subject = EnglishCategory
        self.number_questions_of_subject = 50
        Teacher.__init__(self, file_raw_data= self.file_raw_data,
                         tab= self.tab, number_rows_of_own_one_test=
                         self.number_rows_of_own_one_test,
                         categories_of_subject= self.categories_of_subject,
                         number_questions_of_subject= self.number_questions_of_subject)

    def UpdateRawDataForObject(self, Answers, Categories):
        Categories = [DeleteWhiteSpaceInFrontAndBack(category) for category in Categories]
        Answers = [DeleteWhiteSpaceInFrontAndBack(ans) for ans in Answers]
        if self.UpdateRawDataForClass(Answers, Categories) == 'Status: Anwers form is wrong, you need to repair your anwers':
            return 'Status: Anwers form is wrong, you need to repair your anwers'
        df_feature_to_storage = self.ReadDataFrameFromMySQL('FeatureToStore')
        Categories_to_storage = [Categories[i] for i in list(df_feature_to_storage['Index'])]
        df_feature_to_storage['Lable'] = list(LabelEncoderEnglishCategory.transform(Categories_to_storage))
        df_trainning_data = self.ReadDataFrameFromMySQL('TrainningData')
        df_trainning_data_new = pd.concat([df_trainning_data, df_feature_to_storage.drop(['Index'], axis = 1)], axis=0, ignore_index= True)
        self.WriteDataFrimeToSQLDatabase(df_trainning_data_new, 'TrainningData')
        return 'Status: Your test is sent successfully, if you want to do next test you must click round button in top left conner to reload webpage'

    def CategorizeQuestions(self, state_teacher, k_neighbors):
        test_number = state_teacher[state_teacher.find('test No ') + len('test No '): len(state_teacher)]
        dict = list(ReadDocumentFromColection('DictionariesAllTests', {'test_number': test_number}))[0]
        df_result, df_feature_to_storage, list_unlabeled_questions = self.ConvertDictionaryToDataFrameToStore(dict, dict[
            'Answers'], k_neighbors, 50)
        status = [FillHeader2(dict['question' + str(i)], i) for i in list_unlabeled_questions]
        # Create and megre unlabled data frame
        df_unlabled = pd.DataFrame()
        df_unlabled['Index'] = list_unlabeled_questions
        df_unlabled['Header'] = [dict['question' + str(i)]['header2'] for i in list_unlabeled_questions]
        df_unlabled['Options'] = list(
            map(RepairOption, [dict['question' + str(i)]['options'] for i in list_unlabeled_questions]))
        df_result = pd.concat([df_result.set_index('Index'), df_unlabled.set_index('Index')], axis=1)
        df_result['Index'] = list(range(1, 51))
        self.WriteDataFrimeToSQLDatabase(df_feature_to_storage, 'FeatureToStore')
        return df_result

    def ConvertDictionaryToDataFrameToStore(self, dict, Answers, k_neighbors, length_feature):
        df = ConvertADictionaryToDataFrame(dict)
        # Get Trainning Data and their lables from Database
        df_trainning = self.ReadDataFrameFromMySQL('TrainningData')
        df_trainning['Feature'] = df_trainning['Feature'].apply(ast.literal_eval)
        data_trainning = np.array(
            [UniformFeature(feature, length_feature) for feature in list(df_trainning['Feature'])])
        lables = list(df_trainning['Lable'])
        # PreCategorize test and built feature to storage
        df = FirtsStepCategozineBySeaching(df)
        df = df.reset_index().drop(['index'], axis=1)
        df['Index'] = list(df.index)
        df_unlabled = df[df['Category'] == '0']
        feature_to_storage = [ExtractFeaturesFromOptions(option) for option in list(df_unlabled['options'])]
        df_feature_to_storage = pd.DataFrame()
        df_feature_to_storage['Index'] = df_unlabled['Index']
        df_feature_to_storage['Feature'] = pd.Series(feature_to_storage, name='Feature',
                                                     index=df_feature_to_storage.index)
        df_feature_to_storage['Feature'] = df_feature_to_storage['Feature'].apply(str)
        data_test = np.array([UniformFeature(feature, length_feature) for feature in feature_to_storage])
        # Test new data
        clf = KNeighborsClassifier(n_neighbors=k_neighbors)
        clf.fit(data_trainning, lables)
        numerical_lable = clf.predict(data_test)
        categorical_lable = list(LabelEncoderEnglishCategory.inverse_transform(numerical_lable))
        for lable, index in zip(categorical_lable, list(df_unlabled.index)):
            df.loc[index, 'Category'] = lable
        # Create final dataframe to display
        df_result = pd.DataFrame()
        df_result['Index'] = range(1, 51)
        df_result['Category'] = list(df['Category'])
        df_result['Answers'] = Answers
        return df_result, df_feature_to_storage, [(i + 1) for i in list(df_unlabled['Index'])]


class EnglishStudent(Student):
    def __init__(self):
        self.tab = 'English student'
        self.number_rows_of_own_one_test = 1
        self.number_rows_of_one_test_of_teacher = 2
        self.file_raw_data_student = 'EnglishStudentAnwers'
        self.file_raw_data_teacher = 'EnglishTeacherCategories'
        self.file_preprocessed_data = 'EnglishPreprocessedData'
        self.number_questions_of_subject = 50
        Student.__init__(self, file_raw_data= self.file_raw_data_student, tab= self.tab,
                         number_rows_of_own_one_test= self.number_rows_of_own_one_test,
                         number_questions_of_subject= self.number_questions_of_subject)

class MathTeacher(Teacher):
    def __init__(self):
        self.tab = 'Math teacher'
        self.file_raw_data = 'MathTeacherCategories'
        self.number_rows_of_own_one_test = 2
        self.categories_of_subject = MathCategory
        self.number_questions_of_subject = 50
        Teacher.__init__(self, file_raw_data= self.file_raw_data,
                         tab= self.tab, number_rows_of_own_one_test=
                         self.number_rows_of_own_one_test,
                         categories_of_subject= self.categories_of_subject,
                         number_questions_of_subject= self.number_questions_of_subject)

    def UpdateRawDataForObject(self, list_options, categories):
        if self.UpdateRawDataForClass(list_options, categories) == 'Status: Anwers form is wrong, you need to repair your anwers':
            return 'Status: Anwers form is wrong, you need to repair your anwers'
        return 'Status: Your test is sent successfully, if you want to do next test you must click round button in top left conner to reload webpage'

    def CategorizeQuestions(self, state_teacher, k_neighbors):
        df_result = self.ReadDataFrameFromMySQL('MathIntermediateData')
        return df_result

class MathStudent(Student):
    def __init__(self):
        self.tab = 'Math student'
        self.number_rows_of_own_one_test = 1
        self.number_rows_of_one_test_of_teacher = 2
        self.file_raw_data_student = 'MathStudentAnwers'
        self.file_raw_data_teacher = 'MathTeacherCategories'
        self.file_preprocessed_data = 'MathPreprocessedData'
        self.number_questions_of_subject = 50
        Student.__init__(self, file_raw_data= self.file_raw_data_student, tab= self.tab,
                          number_rows_of_own_one_test= self.number_rows_of_own_one_test,
                         number_questions_of_subject= self.number_questions_of_subject)

class PhysicsTeacher(Teacher):
    def __init__(self):
        self.tab = 'Physics teacher'
        self.file_raw_data = 'PhysicsTeacherCategories'
        self.number_rows_of_own_one_test = 2
        self.categories_of_subject = PhysicsCategory
        self.number_questions_of_subject = 40
        Teacher.__init__(self, file_raw_data= self.file_raw_data,
                         tab= self.tab, number_rows_of_own_one_test=
                         self.number_rows_of_own_one_test,
                         categories_of_subject= self.categories_of_subject,
                         number_questions_of_subject= self.number_questions_of_subject)
    def UpdateRawDataForObject(self, list_options, categories):
        if self.UpdateRawDataForClass(list_options, categories) == 'Status: Anwers form is wrong, you need to repair your anwers':
            return 'Status: Anwers form is wrong, you need to repair your anwers'
        return 'Status: Your test is sent successfully, if you want to do next test you must click round button in top left conner to reload webpage'

    def CategorizeQuestions(self, state_teacher, k_neighbors):
        df_result = self.ReadDataFrameFromMySQL('PhysicsIntermediateData')
        return df_result

class PhysicsStudent(Student):
    def __init__(self):
        self.tab = 'Physics student'
        self.number_rows_of_own_one_test = 1
        self.number_rows_of_one_test_of_teacher = 2
        self.file_raw_data_student = 'PhysicsStudentAnwers'
        self.file_raw_data_teacher = 'PhysicsTeacherCategories'
        self.file_preprocessed_data = 'PhysicsPreprocessedData'
        self.number_questions_of_subject = 40
        Student.__init__(self, file_raw_data= self.file_raw_data_student, tab= self.tab,
                         number_rows_of_own_one_test= self.number_rows_of_own_one_test,
                         number_questions_of_subject= self.number_questions_of_subject)



