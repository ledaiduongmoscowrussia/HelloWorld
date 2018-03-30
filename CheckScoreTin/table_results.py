import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd


def generate_table(subject, max_rows=10):
    test_number = len(pd.read_gbq("select  * from  CheckScoreTin.{}StudentAnwers order by id "
                              .format(subject),
                              'artful-journey-197609', dialect='standard'))
    df_solution = pd.read_gbq("select  * from  CheckScoreTin.{}TeacherCategories where id = {} order by id "
                              .format(subject, test_number * 2 - 2),
                              'artful-journey-197609', dialect='standard')
    df_answer = pd.read_gbq("select  * from CheckScoreTin.{}StudentAnwers where id = {} order by id"
                            .format(subject, test_number - 1),
                            'artful-journey-197609', dialect='standard')
    df = pd.concat([df_answer.drop(columns=['id', 'Datetime']), df_solution.drop(columns=['id'])])

    result = [True if len(set(list(df[col]))) == 1 else False for col in df.columns]
    df = df.append(pd.DataFrame([result], columns=df.columns))
    df.insert(loc=0, column='Label', value=['Answers', 'Solution', 'Results'])
    print(df)
    return html.Table(
        [html.Tr([html.Th(col) for col in df.columns])] +
        [html.Tr([
            html.Td(df.iloc[i][col]) for col in df.columns
        ]) for i in range(min(len(df), max_rows))])

layout_table_result = html.Div(children=[ html.H4(children='English'), generate_table('English')])
