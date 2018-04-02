import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd



print(dcc.__version__) # 0.6.0 or above is required
app = dash.Dash()
app.config['suppress_callback_exceptions']=True

def generate_table(subject, max_rows=10):
    df = pd.DataFrame([[1, 2, 3], [2, 3, 4]])
    return html.Table(
        [html.Tr([html.Th(col) for col in df.columns])] +
        [html.Tr([
            html.Td(df.iloc[i][col]) for col in df.columns
        ]) for i in range(min(len(df), max_rows))])

app.layout = html.Div(children=[ html.H4(children='English'), generate_table('English')])

if __name__ == '__main__':
    app.run_server()