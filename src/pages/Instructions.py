import dash
from dash import Dash, dcc, html, Input, Output, callback
from dash import dcc, html
from dash.dependencies import Input, Output, State




dash.register_page(
    __name__,
    path='/',
    title='Instructions',
    name='Instructions')


layout = html.Div([
    html.H1('Instructions'),
    html.H2('Instructions for Manually Input'),
    html.Div([
        html.P('''Please input all values into the input boxes. The hpo represents the displacement from the bottom of the squat to toe off. Mass should be inputted in kg. Each trial should include maximal force and maximal 
               velocity and make sure the trials match up with each other. You can put up to 5 trials but there is a minimum of 2 inputs. If you are not using force plates the maximal force and velocity needs to be externally
               calculated, this can be done using JB Morins calculations which I will link at the bottom of this page. It does not mattter in what order you put the trials, the code will automatically sort them. After you insert all 
               the data click submit and the Force Velocity Profile should be displayed ''')
    ]),
    html.H3('Instructions for Vald Export'),
    html.P('''This tool is specifically for vald force plates, it can be altered with different force plates as long as the csv file format is the same. Once you have logged into the Vald hub go to Profiles and select the athlete
            you are testing, next go to the results table. Once at the results table select ForceDecks as the system and squat jump variations as the Test Type. Select the settings icon next to the test type and select these metrics
           for display: Velocity at Peak Power [m/s], Force at Peak Power [N], Displacement at Takeoff [cm], and Athlete Standing Weight [kg]. After this is done go to the testing date and select all the squat jump tests associated
           with the Force Velocity test. Next go to export and export the test metrics, take the exported csv and drag and drop into into the file upload section of Vald Export page, click submit annd the
           Force Velocity Profile should be displayed. Important: if the csv file format is changed this will not work, please do not change the exported format.  '''  ),
    
    html.H4('JB Morin Optimal Force Velocity Profile'),
    html.P(''' The underlying logic of this Webapp is built off the papers submitted by JB Morin. The link to his website is here: https://jbmorin.net/scientific-papers/.''' ),

    html.H5('Contact'),
    html.P('''If you have any questions regarding this toolkit or any issues please send me an email at the email below. I would love to expand this toolkit for different technologies and force plates, if you have any interest in doing 
           so please contact me at the same email below.'''),
    html.Div('Cole Whitelaw'),
    html.Div('Email: whitelawcole@gmail.com')


])