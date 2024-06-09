import pandas as pd
import logging
import math
from statistics import mean 
import numpy as np
import json
from sklearn.linear_model import LinearRegression
import plotly.graph_objs as go
from scipy import stats
import math
import logging
from dash import Dash, dcc, html, Input, Output, callback
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import io
import base64
import plotly.express as px


def find_opt_slope(angle, hpo, pmax):
    try:
        rad = 9.81 * math.sin(math.radians(angle))
        logging.debug(f"rad: {rad}")
        term1 = -(rad ** 6) * (hpo ** 6)
        #print(term1)
        term2 = -18 * rad ** 3 * hpo ** 5 * pmax ** 2
        #print(term2)
        term3 = -54 * hpo ** 4 * pmax ** 4
        #print(term3)
        sqrt_term = 10.392 * math.sqrt(abs(2 * rad ** 3 * hpo ** 9 * pmax ** 6 + 27 * hpo ** 8 * pmax ** 8))
        #print(sqrt_term+term1+term2+term3)
        logging.debug(f"term1: {term1}, term2: {term2}, term3: {term3}, sqrt_term: {sqrt_term}")
        X = (term1 + term2 + term3 + sqrt_term) ** (1 / 3)
        
        X = X.real if isinstance(X, complex) else X
        logging.debug(f"X: {X}")
        real_part = X.real if X.real < 0 else -X.real
        result = real_part * 2
        opt_slope = -(rad ** 2 / (3 * pmax)) - ((-(rad ** 4) * hpo ** 4 - 12 * rad * hpo ** 3 * pmax ** 2) / (3 * hpo ** 2 * pmax * result)) + (result / (3 * hpo ** 2 * pmax))
        logging.debug(f"opt_slope: {opt_slope}")
        return opt_slope
    except Exception as e:
        logging.error(f"Error in find_opt_slope: {e}")
        return None

def calc_Fo(pmax, slope):
     Fo = 2 * math.sqrt(-pmax * slope)
     return Fo
def calc_Vo(pmax, Fo):
     Vo = 4 * pmax/Fo
     return Vo

dash.register_page(
    __name__,
    path='/csv_input',
    title='Upload excel sheet exported from Vald',
    name='Vald Export')


layout = html.Div([
    html.H1("VALD CSV File Upload"),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        multiple=False
    ),
    html.Button('Submit', id='submit-button', n_clicks=0),
    html.Div(id='upload-status', style={'margin-top': '20px'}),
    html.Div(id='output-data-upload', style={'width': '90%', 'margin': 'auto'}),
    dcc.Store(id='store-data'),
    dcc.Store(id='store-data2'),
    html.P(id='def_90'),
    html.P(id='def_30')
])

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        else:
            return html.Div(['Unsupported file format'])
    except Exception as e:
        return html.Div(['There was an error processing this file.'])
    V  = df['Velocity at Peak Power [m/s] '].tolist()
    F = df['Force at Peak Power [N] '].tolist()
    displacement = df['Displacement at Takeoff [cm] '].tolist()
    hpo = mean(displacement) * .01


    M = float(df['BW [KG]'].min())




    F.sort(reverse=False)
    V.sort(reverse=True)
    Force = np.array(F,dtype=np.complex128)
    print(Force)
    Velocity = np.array(V,dtype=np.complex128)
    print(Velocity)






    slope, Fo, _, _, _ = stats.linregress(Velocity, Force)
    print(slope)
    print(Fo)
    m_slope = slope/M
    print(m_slope)
    Fo_tru = Fo/M
    Vo_tru = (-Fo/slope)

    Pmax = (((Fo * Vo_tru)/4)/M)




    opt_slope_30 = find_opt_slope(30,hpo,Pmax)
    Fo_30 = calc_Fo(Pmax, opt_slope_30)
    Vo_30 = calc_Vo(Pmax,Fo_30)
    opt_slope_90 = find_opt_slope(90,hpo,Pmax)
    Fo_90 = calc_Fo(Pmax,opt_slope_90)
    Vo_90 = calc_Vo(Pmax,Fo_90)
    Force_deficit_90 = Fo_tru / Fo_90 * 100
    Velocity_decificit_90 = Vo_tru/Vo_90 * 100
    Force_deficit_30 = Fo_tru / Fo_30 * 100
    Velocity_decificit_30 = Vo_tru/Vo_30 * 100
    #Define True FVP Profile
    Tru_FVP = go.Scatter(
            x=[(Vo_tru.real), 0],
            y=[0,Fo_tru.real],
            mode='lines',
            name='True FVP')
    # Define the points for the first regression line




    # Plot optimal F-V profile for 30
    Fvp_30 = go.Scatter(
        x=[Vo_30.real, 0],
        y=[0, Fo_30],
        mode='lines',
        name='FVP-30')

    # Define the points for the second regression line
    # Modify these points as needed for your second line

    Fvp_90 = go.Scatter(
        x=[Vo_90.real, 0],
        y=[0, Fo_90],
        mode='lines',
        name='FVP-90')

    layout = go.Layout(title='Force Velcotiy Profiles',
                        xaxis={'title': 'Velcoity'},
                        yaxis={'title': 'Force'}
                        )

    fig = (go.Figure(data=[Tru_FVP, Fvp_30,Fvp_90], layout=layout))


    #return figure, {'F_d_90': Force_deficit_90.real, 'V_d_90' : Velocity_decificit_90.real, 'F_d_30': Force_deficit_30.real, 'V_d_30': Velocity_decificit_30.real}
    
        
    return dcc.Graph(figure=fig, style={'height': '75vh', 'border': '2px solid #000','boxShadow': '2px 2px 10px rgba(0,0,0,0.2)', 'margin-bottom': '30px', 'margin-top': '30px' }), {'F_d_90': Force_deficit_90.real, 'V_d_90' : Velocity_decificit_90.real, 'F_d_30': Force_deficit_30.real, 'V_d_30': Velocity_decificit_30.real}

@callback(
              Output('store-data', 'data'),
              Output('upload-status', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              prevent_initial_call=True)
def store_output(contents, filename):
    if contents is not None:
        return {'contents' : contents, 'filename' : filename}, f"File '{filename}' uploaded successfully!"
    return None

@callback(
    Output('output-data-upload', 'children'),
    Output('store-data2', 'data'),
    Input('submit-button', 'n_clicks'),
    State('store-data', 'data'),
    prevent_initial_call=True
)
def update_output(n_clicks, data):
    if n_clicks > 0 and data is not None:
        contents = data['contents']
        filename = data['filename']
        graph, deficits = parse_contents(contents, filename)
        return graph, deficits
    return None

  
@callback(
    Output('def_90', 'children'),
    Input('store-data2', 'data'),
    prevent_initial_call=True

)
def reccomendation_vertical(data):
    Force_deficit_90 = round(data['F_d_90'],2)
    Velocity_deficit_90 = round(data['V_d_90'],2)
    if Force_deficit_90 < Velocity_deficit_90:
        return f"""You have a Force Deficit for Vertical Movement which is: {Force_deficit_90}% of the optimal maximum Force in the vertical direction.---

        Recommended Exercises Include: Heavy Squats, Heavy Deadlifts"""
    if Velocity_deficit_90 < Force_deficit_90:
        return f"""You have a Velocity Deficit for Vertical Movement which is: {Velocity_deficit_90}% of the optimal maximal Velocity in the vertical direction.---

        Reccomended Exercises Include: Drop Jumps, Box Jumps, Depth Jumps, Countermovement Jumps, Squat Jumps"""
    
@callback(
    Output('def_30', 'children'),
    Input('store-data2', 'data'),
    prevent_initial_call=True

)
def reccomendation_horizontal(data):
    Force_deficit_30 = round(data['F_d_30'], 2)
    Velocity_deficit_30 = round(data['V_d_30'], 2)
    if Force_deficit_30 < Velocity_deficit_30:
        return f"""You have a Force Deficit for Horizontal Movement which is: {Force_deficit_30}% of the optimal maximal force in the horizontal direction.---

        Recommended Exercises Include: Sled Pushes, Weighted Sprints, Heavy Lunges"""
    if Velocity_deficit_30 < Force_deficit_30:
        return f"""You have a Velocity Deficit for Horizontal Movement which is: {Velocity_deficit_30}% of the optimal maximal Velocity in the horizontal direction.---
        
        Recommended Exercises: Include: Sprints, Broad Jumps, SL Broad Jumps"""
    























