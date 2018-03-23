import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
from Dataset import *


colors = {'background': '#111111','text': '#7FDBFF'}

layout_home_page = html.Div([
    html.H1(children='WELCOM TO MY PLATFORM',style={'textAlign': 'center', 'color': colors['text']}),
    html.Div([dcc.Dropdown(id='subject_plot', options=[{'label': i, 'value': i} for i in Subjects], value='English', placeholder = 'Select subject')], style = {'width': '20%','display': 'inline-block'}),
    html.Div([dcc.Link('TEACHER PAGE', href='/page_teacher'),html.Br(),dcc.Link('STUDENT PAGE', href='/page_student')
              ,html.Br(),dcc.Link('LIST TESTS PAGE', href='/page_list_test'), html.Br(), dcc.Link('ADMIN PAGE', href='/page_admin')],
             style = {'width': '10%','float': 'right','display': 'inline-block'}),
    html.H1(children='----------------------'),
    html.Div(id='graphs')])

layout_admin = html.Div([
    html.Div([dcc.Link('HOME', href='/'),html.Br(), dcc.Dropdown(id='subject_admin', options=[{'label': i, 'value': i} for i in Subjects], value='English', placeholder = 'Select subject'),
              html.Div(id='state_admin'), dcc.Input(id='test_number_admin', type= 'number', placeholder = 'Enter test number')],
             style = {'width': '20%','display': 'inline-block'}),
    dcc.Input(
        id='text_area_answers_admin',
        placeholder='Enter answers...',
        type='text',
        style={'width': '100%'}),
    dcc.Textarea(
        id='text_area_exam_admin',
        placeholder='Enter exam text',
        style={'width': '100%', 'height': 300 }),
    dt.DataTable(
        rows=[{}],
        columns= ['Index', 'Category', 'Answers'],
        id='table_admin'),
        dcc.RadioItems(
            id='complete_confirm_admin',
            options=[{'label': 'I have done', 'value':'I have done'}, {'label':'I have not done', 'value': 'I have not done' }],
            value= 'I have not done',
            style={'display': 'inline-block', 'float': 'right',}),
    html.Button(id='submit_button_admin',type='n-clicks', children='SEND', style = {'display': 'inline-block', 'float': 'right',}),
    html.Div(id='status_admin')
    ])

layout_teacher = html.Div([
    html.Div([dcc.Link('HOME', href='/'),html.Br(),dcc.Link('LIST TESTS PAGE', href='/page_list_test'),html.Br(), dcc.Dropdown(id='subject_teacher', options=[{'label': i, 'value': i} for i in Subjects], value='English', placeholder = 'Select subject'),
              html.Div(id='state_teacher'), dcc.Input(id='test_number_teacher', type= 'number', placeholder = 'Enter test number')],
             style = {'width': '20%','display': 'inline-block'}),
    html.Div([html.Div([dcc.Dropdown(id='algorithm_teacher',options=[{'label':i,'value':i} for i in Algorithm], value='K nearest neighbor')]),
              dcc.Slider(id='K_neighbors_teacher', min=1, max=9, marks={i:'K={}'.format(i) for i in range(1, 10)}, value=1)],
             style={'width': '50%', 'float': 'right', 'display': 'inline-block'}),
    dt.DataTable(
        rows=[{}],
        editable=True,
        columns= ['Index', 'Options', 'Header', 'Category'],
        column_widths= [100, 400, 1100, 200],
        id='table_teacher'),
    html.Div(id='grammal', children = 'Noun Pronoun Adjective_Adverb Conjunction Articles_a_an_the Prepositions Phrasal_verb Verb Model_verb Verb_tenses Passive_voice Conditinal'),
    html.Div(id='grammal1',children='Gerund_infinitive_participle Tag_Question Inversion Relative_clause Direct_indirect_sentence Comparison Subject_verb_agreement Identify_formation_of_words '),
    dcc.RadioItems(
            id='complete_confirm_teacher',
            options=[{'label': 'I have done', 'value':'I have done'}, {'label':'I have not done', 'value': 'I have not done' }],
            value= 'I have not done',
            style={'display': 'inline-block', 'float': 'right',}),
    html.Button(id='submit_button_teacher',type='n-clicks', children='SEND', style = {'display': 'inline-block', 'float': 'right',}),
    html.Div(id='status_teacher')])

layout_student = html.Div(
    [html.Div([dcc.Link('HOME', href='/'),html.Br(),dcc.Link('LIST TESTS PAGE', href='/page_list_test'),html.Br(), dcc.Dropdown(id='subject_student', options=[{'label': i, 'value': i} for i in Subjects], value=None, placeholder = 'Select subject'),
               html.Div(id='state_student'), dcc.Input(id='test_number_student', type= 'number', placeholder = 'Enter test number')],style = {'width': '20%','display': 'inline-block'}),
    html.H1('CHOOSE YOUR ANSWERS'),
    # The firts 25 questions here
    html.Div([dcc.Dropdown(id='input'+str(i), options=[{'label': Option, 'value': Option} for Option in Options], placeholder = "Question " + str(i)) for i in range(1, 26)], style = {'width': '38%','display': 'inline-block'}),
    # The second 25 questions here
    html.Div([dcc.Dropdown(id='input'+str(i), options=[{'label': Option, 'value': Option} for Option in Options], placeholder = "Question " + str(i)) for i in range(26, 51)],style = {'width': '38%','float': 'right','display': 'inline-block'}),

    html.Div([dcc.RadioItems(
            id='complete_confirm_student',
            options=[{'label': 'I have done', 'value':'I have done'}, {'label':'I have not done', 'value': 'I have not done' }],
            value= 'I have not done',
            style={'display': 'inline-block', 'float': 'right',}),
    html.Button(id='submit_button_student',type='n-clicks', children='SEND'),
    html.Div(id='status')],style = {'width': '20%','display': 'inline-block', 'float': 'right'})])

