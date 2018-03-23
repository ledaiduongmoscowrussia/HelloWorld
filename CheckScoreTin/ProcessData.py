import warnings;warnings.filterwarnings('ignore')
from datetime import datetime
from mongdb import *
from NatureLanguageProcessing import *
from SubFunctions import *

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

    def GetNumberOfDoneTests(self, file, number_rows_one_test):
        number_done_test_your = int(len(self.ReadDataFrameFromMySQL(file)) / number_rows_one_test)
        return number_done_test_your

class Subject(SubFunctions):
    def __init__(self, file_preprocessed_data, file_raw_data_student, file_raw_data_teacher,
                 number_rows_of_one_test_of_teacher):
        self.file_preprocessed_data = file_preprocessed_data
        self.file_raw_data_student = file_raw_data_student
        self.file_raw_data_teacher = file_raw_data_teacher
        self.number_rows_of_one_test_of_teacher = number_rows_of_one_test_of_teacher
        SubFunctions.__init__(self)

    def CheckAllNewTests(self):
        df_file_preprocessed_data = self.ReadDataFrameFromMySQL(self.file_preprocessed_data)
        df_file_raw_data_student = self.ReadDataFrameFromMySQL(self.file_raw_data_student)
        df_file_raw_data_teacher = self.ReadDataFrameFromMySQL(self.file_raw_data_teacher)
        number_scaned_tests = len(df_file_preprocessed_data.index)
        number_student_tests = len(df_file_raw_data_student.index)
        number_teacher_tests = int(len(df_file_raw_data_teacher.index) / self.number_rows_of_one_test_of_teacher)
        tests_ready_to_scan = list(range(number_scaned_tests+1, min(number_student_tests, number_teacher_tests) + 1))
        return tests_ready_to_scan

    def ProcessATest(self, categories, anwrers_correct, list_anwers_user):
        df = pd.DataFrame()
        df_result = pd.DataFrame()
        df['Categories'] = categories
        df['AnwersCorrect'] = anwrers_correct
        Datetime = list_anwers_user.pop(0)
        df['AnwersUser'] = list_anwers_user
        df['Score'] = np.where(df.AnwersUser == df.AnwersCorrect, 1, 0)
        df_result['Percentage'] = 100 * df.groupby('Categories').sum()['Score'] / df.groupby('Categories').count()['Score']
        score = 10 * df['Score'].sum() / df['Score'].count()
        filling_up = 10 * len([answer for answer in list_anwers_user if answer != None])/df['Score'].count()
        effectioncy = 10 * score / filling_up
        return [df_result,Datetime, score, effectioncy, filling_up]

    def UpdateATest(self, test_oder):
        categories = list(self.ReadDataFrameFromMySQL(self.file_raw_data_teacher).loc[test_oder * self.number_rows_of_one_test_of_teacher - 1, :])
        anwrers_correct = list(self.ReadDataFrameFromMySQL(self.file_raw_data_teacher).loc[test_oder * self.number_rows_of_one_test_of_teacher - self.number_rows_of_one_test_of_teacher, :])
        list_anwers_user = list(self.ReadDataFrameFromMySQL(self.file_raw_data_student).loc[test_oder - 1, :])
        [df_type, Datetime, score, effectioncy, filling_up] = self.ProcessATest(categories, anwrers_correct, list_anwers_user)
        df_score = pd.DataFrame(data=[[score]], index=['Score'], columns=['Percentage'])
        df_effectioncy = pd.DataFrame(data=[[effectioncy]], index=['Effectioncy'], columns=['Percentage'])
        df_filling_up = pd.DataFrame(data=[[filling_up]], index=['Filling_up'], columns=['Percentage'])
        df_date_time = pd.DataFrame(data=[[Datetime]], index=['Datetime'], columns=['Percentage'])
        df_result = pd.concat([df_date_time, df_score, df_effectioncy, df_filling_up, df_type], axis=0)
        self.AddSeriesToRowOfDataFrameByName(self.file_preprocessed_data, df_result['Percentage'])

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
        self.AddSeriesOrListToRowOfDataFrameByIndexEqualLength(self.file_raw_data, Answers)
        self.AddSeriesOrListToRowOfDataFrameByIndexEqualLength(self.file_raw_data, Categories)
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
        now = datetime.now()
        list_options = [now] + list_options
        self.AddSeriesOrListToRowOfDataFrameByIndexEqualLength(self.file_raw_data, list_options)
        return 'Status: Your test is sent successfully, if you want to do next test you must click round button in top left conner to reload webpage'
    def GetDataForGraphForClass(self, file_preprocessed_data):
        df = self.ReadDataFrameFromMySQL(file_preprocessed_data)
        data = [
            {
                'x': df['Datetime'],
                'y': df['Score'],
                'name': 'Score',
                'marker': {'color': 'rgb(255, 0, 0)'},
            },
            {
                'x': df['Datetime'],
                'y': df['Filling_up'],
                'name': 'Filling_up',
                'marker': {'color': 'rgb(0, 0, 0)'},
            },
            {
                'x': df['Datetime'],
                'y': df['Effectioncy'],
                'name': 'Effectioncy',
                'marker': {'color': 'rgb(0, 213, 255)'},
            }]
        return data

    def GetDataForGraphForClassSecond(self, file_preprocessed_data, categories):
        df = self.ReadDataFrameFromMySQL(file_preprocessed_data)
        def EsarerToSee (x):
            if x == 0: return 2.222222222
            else:return x
        data = [
            {
                'x': list(range(1, df['Datetime'].count() + 1)),
                'y': [EsarerToSee(x) for x in list(df[category])],
                'name': category,
                'type': 'bar',
                'marker': { 'color': 'rgb(0,213,255)'}
            }for category in categories]
        return [[data_i] for data_i in data]

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



class EnglishAdmin(SubFunctions):
    def __init__(self):
        SubFunctions.__init__(self)
    def GetNumberOfDoneTests(self):
        return ReadNumberOfDocuments('DictionariesAllTests')

    def UpdateDataToDatabase(self, text_answers, text_exam, test_number, complete_confirm):
        Answers = ExtractAnswersFromText(text_answers)
        dict = ConvertATestToDictionary(text_exam, Answers, test_number)
        df_result, df_feature_to_storage, list_unlabeled_questions = ConvertDictionaryToDataFrameToStore(dict, Answers, 1, 50)
        if complete_confirm == 'I have done':
            AddDocumentToColection('DictionariesAllTests', dict)
        return df_result


class MathAdmin(SubFunctions):
    def __init__(self):
        SubFunctions.__init__(self)

    def GetNumberOfDoneTests(self):
        return int(len(self.ReadDataFrameFromMySQL('MathTeacherCategories'))/2)

    def UpdateDataToDatabase(self, text_answers, text_exam, test_number, complete_confirm):
        Answers = ExtractAnswersFromText(text_answers)
        dict = ConvertATestToDictionary(text_exam, Answers, test_number)
        df_result = CategorizeQuestionsMath()
        if complete_confirm == 'I have done':
            self.WriteDataFrimeToSQLDatabase(df_result, 'MatIntermediateData')
        return df_result

class PhysicsAdmin(SubFunctions):
    def __init__(self):
        SubFunctions.__init__(self)

    def GetNumberOfDoneTests(self):
        return int(len(self.ReadDataFrameFromMySQL('PhysicsTeacherCategories'))/2)

    def UpdateDataToDatabase(self, text_answers, text_exam, test_number, complete_confirm):
        Answers = ExtractAnswersFromText(text_answers)
        df_result = CategorizePhysicsTest(Answers, text_exam)
        if complete_confirm == 'I have done':
            self.WriteDataFrimeToSQLDatabase(df_result, 'PhysicsIntermediateData')
        return df_result


def GetStudentObject(tab):
    if tab == Subjects[0]: return EnglishStudent()
    elif tab == Subjects[1]: return MathStudent()
    elif tab == Subjects[2]: return PhysicsStudent()

def GetTeacherObject(tab):
    if tab == Subjects[0]: return EnglishTeacher()
    elif tab == Subjects[1]: return MathTeacher()
    elif tab == Subjects[2]: return PhysicsTeacher()

def GetAdminObject(tab):
    if tab == Subjects[0]: return EnglishAdmin()
    elif tab == Subjects[1]: return MathAdmin()
    elif tab == Subjects[2]: return PhysicsAdmin()
