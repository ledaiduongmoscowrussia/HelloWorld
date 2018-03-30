from LayoutWebApplication import *
import plotly.graph_objs as go
from dash.dependencies import Input, Output, State
from LayoutListTests import *
from ProcessData import *
from flask import Flask
from Dataset import *



print(dcc.__version__) # 0.6.0 or above is required
server = Flask(__name__)
app = dash.Dash(__name__, server=server)
app.config['suppress_callback_exceptions']=True
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page_content'),
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})])

# Update the homepage
@app.callback(Output('page_content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/page_teacher':
        return layout_teacher
    elif pathname == '/page_student':
        return layout_student
    elif pathname == '/page_list_test':
        return layout_list_test
    elif pathname == '/page_admin':
        return layout_admin
    else:
        return layout_home_page
# You could also return a 404 "URL not found" page here
app.css.append_css({'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'})

# //////////////////////////////////////////////////////////////////CallBack for admin page//////////////////////////////////////////////////////////////////////
# Give user the his or her state to fill number of next test
@app.callback(Output('state_admin', 'children'),[Input('subject_admin', 'value')])
def GetState(subject):
    try:
        obj = GetAdminObject(subject)
        number_done_test_your = obj.GetNumberOfDoneTests()
    except KeyError:
        return 'You need to select subject in above dropdown'
    return 'You are doing test No ' + str(number_done_test_your + 1)

@app.callback(  Output('table_admin', 'rows'),[Input('submit_button_admin', 'n_clicks')],
                state=[State('test_number_admin', 'value'),State('complete_confirm_admin', 'value'),
                       State('text_area_exam_admin', 'value'), State('text_area_answers_admin', 'value'),
                       State('subject_admin', 'value')])
def UpdateDataToDatabase(n_clicks, test_number, complete_confirm, text_exam, text_answers, subject):
    if n_clicks != None:
        obj = GetAdminObject(subject)
        df_result = obj.UpdateDataToDatabase(text_answers, text_exam, test_number, complete_confirm)
        print(df_result)
    return df_result.to_dict('records')

# /////////////////////////////////////////////////////////////////CallBack for home page/////////////////////////////////////////////////////////////////////////
@app.callback(Output('graphs','children'),[Input('subject_plot', 'value'),
                                           Input('range_date_time', 'start_date'),
                                           Input('range_date_time', 'end_date')])
def UpdateDataAndPlotGraphSecond(tab, start_date, end_date):
    day_before = str("'" + str(start_date) + "'")
    day_after = str("'" + str(end_date) + "'")
    ####################################
    df_answer = pd.read_gbq(
        "select  * from CheckScoreTin.{}StudentAnwers where Datetime > TIMESTAMP({}) and Datetime < TIMESTAMP({}) order by id"
        .format(tab, day_before, day_after),
        'artful-journey-197609', dialect='standard')
    test_start = np.min(list(df_answer['id']))
    test_end = np.max(list(df_answer['id']))
    df_answer = df_answer.drop(columns=['id', 'Datetime'])
    ####################################
    df_solution = pd.read_gbq(
        "select  * from  CheckScoreTin.{}TeacherCategories where id >= {} * 2 and id <= {} * 2 and MOD(id, 2) = 0 order by id "
        .format(tab, test_start, test_end),
        'artful-journey-197609', dialect='standard')
    df_solution = df_solution.drop(columns=['id'])
    #####################################
    df_categories = pd.read_gbq(
        "select  * from  CheckScoreTin.{}TeacherCategories where id >= {} * 2 and id <= {} * 2 + 1 and MOD(id, 2) = 1 order by id "
        .format(tab, test_start, test_end),
        'artful-journey-197609', dialect='standard')
    df_categories = df_categories.drop(columns=['id'])
    #####################################
    data_raw1 = sorted(
        [i for i in list(map(partial(Caculation, df_answer, df_solution, df_categories), EnglishCategory)) if
         i != None], key=lambda x: x[1], reverse=True)
    trace1 = {
        'x': [x[0] for x in data_raw1],
        'y': [x[1] for x in data_raw1],
        'name': 'accurate',
        'type': 'bar'
    }
    trace2 = {
        'x': [x[0] for x in data_raw1],
        'y': [x[2] for x in data_raw1],
        'name': 'unfilled',
        'type': 'bar'
    }
    trace3 = {
        'x': [x[0] for x in data_raw1],
        'y': [x[3] for x in data_raw1],
        'name': 'inaccurate',
        'type': 'bar'
    }
    data1 = [trace1, trace2, trace3]
    layout1 = {
        'xaxis': {'title': 'X axis'},
        'yaxis': {'title': 'Y axis'},
        'barmode': 'relative',
        'title': 'Relative Barmode'
    }
    #######################################
    data_raw2 = sorted(
        [i for i in list(map(partial(Caculation, df_answer, df_solution, df_categories), EnglishCategory)) if
         i != None], key=lambda x: x[1], reverse=True)
    trace4 = {
        'x': [x[0] for x in data_raw2],
        'y': [x[4] for x in data_raw2],
        'name': 'accurate',
        'type': 'bar'
    }
    trace5 = {
        'x': [x[0] for x in data_raw2],
        'y': [x[5] for x in data_raw2],
        'name': 'unfilled',
        'type': 'bar'
    }
    trace6 = {
        'x': [x[0] for x in data_raw2],
        'y': [x[6] for x in data_raw2],
        'name': 'inaccurate',
        'type': 'bar'
    }
    data2 = [trace4, trace5, trace6]
    layout2 = {
        'xaxis': {'title': 'X axis'},
        'yaxis': {'title': 'Y axis'},
        'barmode': 'relative',
        'title': 'Relative Barmode'
    }
    #######################################
    graphs = [dcc.Graph(id='g1',figure= {'data': data1, 'layout': layout1 }),
              dcc.Graph(id='g2', figure={'data': data2, 'layout': layout2})]
    return graphs


# //////////////////////////////////////////////////////////////////CallBack for teacher page//////////////////////////////////////////////////////////////////////
# Give user the his or her state to fill number of next test
@app.callback(Output('state_teacher', 'children'),[Input('subject_teacher', 'value')])
def GetState(subject):
    try:
        obj = GetTeacherObject(subject)
        number_done_test_your = obj.GetNumberOfDoneTests(obj.file_raw_data)
    except (KeyError, AttributeError):
        return 'You need to select subject in above dropdown'
    return 'You are doing test No ' + str(number_done_test_your + 1)


@app.callback(Output('table_teacher', 'rows'), [Input('subject_teacher', 'value'), Input('state_teacher', 'children'), Input('K_neighbors_teacher', 'value')])
def CategorizeQuestions(subject, state_teacher, k_neighbors ):
    df_result = pd.DataFrame()
    obj = GetTeacherObject(subject)
    try:
        df_result = obj.CategorizeQuestions(state_teacher, k_neighbors )
    except():
        pass
    return df_result.to_dict('records')


@app.callback(  Output('status_teacher', 'children'),[Input('submit_button_teacher', 'n_clicks'), Input('table_teacher', 'rows')],
                state=[State('subject_teacher', 'value'),State('test_number_teacher', 'value'), State('complete_confirm_teacher', 'value'),])
def UpdateDataToDatabase(n_clicks, rows, subject, test_number, complete_confirm):
    if n_clicks != None:
        obj = GetTeacherObject(subject)
        state = obj.CheckComponentsToGetRawData(test_number, complete_confirm)
        if state is not None: return state
        df = pd.DataFrame(rows)
        Categories = list(df['Category'])
        Answers = list(df['Answers'])
        return obj.UpdateRawDataForObject(Answers, Categories, test_number)
    return 'Status: You can start'


#////////////////////////////////////////////////////////////////////////////////////////CallBacks for student/////////////////////////////////////////////////////

@app.callback(Output('state_student', 'children'),[Input('subject_student', 'value')])
def GetState(subject):
    try:
        obj = GetStudentObject(subject)
        number_done_test_your = obj.GetNumberOfDoneTests(obj.file_raw_data_student)
    except (AttributeError):
        return 'You need to select subject in above dropdown'
    return 'You are doing test No ' + str(number_done_test_your + 1)

@app.callback(  Output('status', 'children'),[Input('submit_button_student', 'n_clicks')],state=[
State('subject_student', 'value'),
State('test_number_student', 'value'),
State('complete_confirm_student', 'value'),
State('input1', 'value'),
State('input2', 'value'),
State('input3', 'value'),
State('input4', 'value'),
State('input5', 'value'),
State('input6', 'value'),
State('input7', 'value'),
State('input8', 'value'),
State('input9', 'value'),
State('input10', 'value'),
State('input11', 'value'),
State('input12', 'value'),
State('input13', 'value'),
State('input14', 'value'),
State('input15', 'value'),
State('input16', 'value'),
State('input17', 'value'),
State('input18', 'value'),
State('input19', 'value'),
State('input20', 'value'),
State('input21', 'value'),
State('input22', 'value'),
State('input23', 'value'),
State('input24', 'value'),
State('input25', 'value'),
State('input26', 'value'),
State('input27', 'value'),
State('input28', 'value'),
State('input29', 'value'),
State('input30', 'value'),
State('input31', 'value'),
State('input32', 'value'),
State('input33', 'value'),
State('input34', 'value'),
State('input35', 'value'),
State('input36', 'value'),
State('input37', 'value'),
State('input38', 'value'),
State('input39', 'value'),
State('input40', 'value'),
State('input41', 'value'),
State('input42', 'value'),
State('input43', 'value'),
State('input44', 'value'),
State('input45', 'value'),
State('input46', 'value'),
State('input47', 'value'),
State('input48', 'value'),
State('input49', 'value'),
State('input50', 'value')])
def update_output(n_clicks, tab, test_number, complete_confirm,
                  input1, input2, input3, input4, input5, input6, input7, input8, input9, input10,
                  input11, input12, input13, input14, input15, input16, input17, input18, input19, input20,
                  input21, input22, input23, input24, input25, input26, input27, input28, input29, input30,
                  input31, input32, input33, input34, input35, input36, input37, input38, input39, input40,
                  input41, input42, input43, input44, input45, input46, input47, input48, input49, input50):
    if n_clicks != None:
        obj = GetStudentObject(tab)
        state = obj.CheckComponentsToGetRawData(test_number, complete_confirm)
        if state is not None: return state
        list_options = [input1, input2, input3, input4, input5, input6, input7, input8, input9, input10,
                        input11, input12, input13, input14, input15, input16, input17, input18, input19, input20,
                        input21, input22, input23, input24, input25, input26, input27, input28, input29, input30,
                        input31, input32, input33, input34, input35, input36, input37, input38, input39, input40,
                        input41, input42, input43, input44, input45, input46, input47, input48, input49, input50]
        return obj.UpdateRawDataForClass(list_options, test_number)
    return 'Status: You can start'
if __name__ == '__main__':
    app.run_server()
