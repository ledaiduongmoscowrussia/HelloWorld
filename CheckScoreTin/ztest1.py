import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime as dtime
from LayoutWebApplication import layout_home_page
app = dash.Dash()


app.config['suppress_callback_exceptions'] = True
app.layout = layout_home_page



if __name__ == '__main__':
    app.run_server(debug=True)