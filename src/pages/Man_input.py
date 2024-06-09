import dash
from dash import Dash, dcc, html, Input, Output, callback
from dash import dcc, html
from dash.dependencies import Input, Output, State
import numpy as np

from sklearn.linear_model import LinearRegression
import plotly.graph_objs as go
from scipy import stats
import math
import logging

dash.register_page(
    __name__,
    path='/man_input',
    title='Force Velocity Profile',
    name='Manualy Input Force Velocity Profile Data')
logging.basicConfig(level=logging.DEBUG)


def find_opt_slope(angle, hpo, pmax):
    try:
        rad = 9.81 * math.sin(math.radians(angle))
        logging.debug(f"rad: {rad}")
        term1 = -(rad ** 6) * (hpo ** 6)
        term2 = -18 * rad ** 3 * hpo ** 5 * pmax ** 2
        term3 = -54 * hpo ** 4 * pmax ** 4
        sqrt_term = 10.392 * math.sqrt(abs(2 * rad ** 3 * hpo ** 9 * pmax ** 6 + 27 * hpo ** 8 * pmax ** 8))
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


layout = [html.H1(children='Manual Input'),
    html.Div(children="Input hpo"),
    dcc.Input(id="hpo", type='number'),
    html.Div(children="Input Mass(kg)"),
    dcc.Input(id="Mass", type='number'),
    html.Div(children='Input Force Values'),
    dcc.Input(id='f1', type='number', placeholder='Trial 1'),
    dcc.Input(id='f2', type='number', placeholder='Trial 2'),
    dcc.Input(id='f3', type='number', placeholder='Trial 3'),
    dcc.Input(id='f4', type='number', placeholder='Trial 4'),
    dcc.Input(id='f5', type='number', placeholder='Trial 5'),
    html.Div(children='Input Velocity Values'),
    dcc.Input(id='v1', type='number', placeholder='Trial 1'),
    dcc.Input(id='v2', type='number', placeholder='Trial 2'),
    dcc.Input(id='v3', type='number', placeholder='Trial 3'),
    dcc.Input(id='v4', type='number', placeholder='Trial 4'),
    dcc.Input(id='v5', type='number', placeholder='Trial 5'),
    html.Button(id='my_button', n_clicks=0, children="Generate Profile"),
    dcc.Store(id='store-values'),
    dcc.Store(id='store-values2'),
    html.Div(
    dcc.Graph(id='graph-output', figure={}),
    style={'height': '60vh', 'border': '2px solid #000','boxShadow': '2px 2px 10px rgba(0,0,0,0.2)', 'margin-bottom': '20px', 'margin-top': '20px' }),
    html.P(id='deficit_90'),
    html.P(id='deficit_30')
]
              
              
              
              

@callback(
    Output('store-values', 'data'),
    [Input('my_button', 'n_clicks')],
    [State('f1', 'value'), State('f2', 'value'), State('f3', 'value'),
     State('f4', 'value'), State('f5', 'value'),
     State('v1', 'value'), State('v2', 'value'), State('v3', 'value'),
     State('v4', 'value'), State('v5', 'value')],
     prevent_initial_call=True
)
def store_values(n_clicks, f1, f2, f3, f4, f5, v1, v2, v3, v4, v5):
    if n_clicks > 0:
        force_values = np.array([f1, f2, f3, f4, f5])
        velocity_values = np.array([v1, v2, v3, v4, v5])

        # Remove None values if any of the inputs are left empty
        force_values = [f for f in force_values if f is not None]
        velocity_values = [v for v in velocity_values if v is not None]
        force_values = np.sort(force_values)[::-1]
        velocity_values = np.sort(velocity_values)
        print(force_values)
        print(velocity_values)


        return {'force_values': force_values, 'velocity_values': velocity_values}

    return {'force_values': [], 'velocity_values': []}

@callback(
    Output('graph-output', 'figure'), Output('store-values2', 'data'), 
    Input('store-values', 'data'), Input('my_button', 'n_clicks'),
    State('Mass', 'value'), State('hpo', 'value'),
    prevent_initial_call=True
)


def calc_Fo_Vo_Pmax(data,n_clicks,M,hpo):
    if n_clicks == 0 or not data['force_values'] or not data['velocity_values'] or M is None or hpo is None:
        return go.Figure()
    Force = np.array(data['force_values'], dtype=np.complex128)
    Velocity = np.array(data['velocity_values'], dtype=np.complex128)
    print(float(hpo))
    print(M)
    slope, Fo, _, _, _ = stats.linregress(Velocity, Force)
    m_slope = slope/M
    Fo_tru = Fo/M
    print(Fo)
    Vo_tru = (-Fo/slope)
    print(Vo_tru)
    Pmax = (((Fo * Vo_tru)/4)/M)

    print(Pmax)
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
         name='True FVP'
    )


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

    figure = (go.Figure(data=[Tru_FVP, Fvp_30,Fvp_90], layout=layout))

    
    return figure, {'F_d_90': Force_deficit_90.real, 'V_d_90' : Velocity_decificit_90.real, 'F_d_30': Force_deficit_30.real, 'V_d_30': Velocity_decificit_30.real}

@callback(
    Output('deficit_90', 'children'),
    Input('store-values2', 'data'),
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
    Output('deficit_30', 'children'),
    Input('store-values2', 'data'),
    prevent_initial_call=True

)
def reccomendation_horizontal(data):
    Force_deficit_30 = round(data['F_d_30'], 2)
    Velocity_deficit_30 = round(data['V_d_30'], 2)
    if Force_deficit_30 < Velocity_deficit_30:
        return f"""You have a Force Deficit for Horizontal Movement which is: {Force_deficit_30}% of the optimal maximal force in the horizontal direction.---

        Recommended Exercises Include: Sled Pushes, Weighted Sprints, Heavy Lunges"""
    if Velocity_deficit_30 < Force_deficit_30:
        return f"""You have a Velocity Deficit for Horizontal Movement which is: {Velocity_deficit_30}% of the optimal maximal velocity in the horizontal direction.---     
        
        Recommended Exercises Include: Sprints, Broad Jumps, SL Broad Jumps"""
    
    



   






# if __name__ == '__main__':
#     app.run(debug=True)