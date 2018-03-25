import warnings;warnings.filterwarnings('ignore')
from datetime import datetime
from mongdb import *
from NatureLanguageProcessing import *
from google.cloud import bigquery
import pprint

class Person(SubFunctions):
    def __init__(self, file_raw_data, tab, number_rows_of_own_one_test ):
        SubFunctions.__init__(self)
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
        return len(df)

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
    def UpdateRawDataForClass(self, list_options):
        for option in list_options:
            if option != None:
                if option not in Options or len(option) != 1:
                    return 'Status: You need to click round button in top left conner to reload webpage'
        list_options = list_options[0: self.number_questions_of_subject]
        list_options = [datetime.now()] + list_options
        num_test_done = self.GetNumberOfDoneTests(self.file_raw_data)
        self.StreamData('CheckScoreTin', self.file_raw_data, [[num_test_done] + list_options])
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
        df_result, df_feature_to_storage, list_unlabeled_questions = ConvertDictionaryToDataFrameToStore(dict, dict[
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


class EnglishStudent(Student, Subject):
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
        Subject.__init__(self, file_preprocessed_data=self.file_preprocessed_data,
                         file_raw_data_student= self.file_raw_data_student,
                         file_raw_data_teacher= self.file_raw_data_teacher,
                         number_rows_of_one_test_of_teacher= self.number_rows_of_one_test_of_teacher)
    def UpdateAllTest(self):
        tests_ready_to_scan = self.CheckAllNewTests()
        if len(tests_ready_to_scan) > 0:
            for test in tests_ready_to_scan:
                self.UpdateATest(test)

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

class MathStudent(Student, Subject):
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
        Subject.__init__(self, file_preprocessed_data=self.file_preprocessed_data,
                         file_raw_data_student= self.file_raw_data_student,
                         file_raw_data_teacher= self.file_raw_data_teacher,
                         number_rows_of_one_test_of_teacher= self.number_rows_of_one_test_of_teacher)
    def UpdateAllTest(self):
        tests_ready_to_scan = self.CheckAllNewTests()
        if len(tests_ready_to_scan) > 0:
            for test in tests_ready_to_scan:
                self.UpdateATest(test)

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

class PhysicsStudent(Student, Subject):
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
        Subject.__init__(self, file_preprocessed_data=self.file_preprocessed_data,
                         file_raw_data_student= self.file_raw_data_student,
                         file_raw_data_teacher= self.file_raw_data_teacher,
                         number_rows_of_one_test_of_teacher= self.number_rows_of_one_test_of_teacher)
    def UpdateAllTest(self):
        tests_ready_to_scan = self.CheckAllNewTests()
        if len(tests_ready_to_scan) > 0:
            for test in tests_ready_to_scan:
                self.UpdateATest(test)



