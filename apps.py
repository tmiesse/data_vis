import random  
import dash;import requests
import dash_leaflet as dl  
import dash_leaflet.express as dlx  
from dash_extensions.javascript import Namespace
import pathlib as pl; import pandas as pd
from dash import dcc, html
import requests;import json
from dash_extensions.javascript import assign
from dash_extensions.enrich import DashProxy
from rosely import WindRose
import numpy as np;pd.options.plotting.backend = "plotly"

# ---------------------- Functions -----------------------------------------------------------------
def noaa_data(begin,end,station,vdatum='NAVD',interval='6',
                       form='json',t_zone='GMT',unit='metric',product='water_level'):
    if product=='wind':
        api = f'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?begin_date={begin}&end_date={end}&station={station}'\
        f'&product={product}&time_zone={t_zone}&interval={interval}&units={unit}&application=DataAPI_Sample&format={form}'
    else:
        api = f'https://tidesandcurrents.noaa.gov/api/datagetter?begin_date={begin}&end_date={end}&station={station}'\
             f'&product={product}&application=NOS.COOPS.TAC.WL&datum={vdatum}&interval={interval}&time_zone={t_zone}&units={unit}&format={form}'
    data = requests.get(url=api).content.decode()
    return data

def find_columns(data):
    data2 = []
    for f in data.split(' '):
        if f != '':
            data2.append(f)   
    return data2

def gen_windrose(feature,start,end,interval='6'):
    station = feature['properties']['tooltip']
    
    noaa = json.loads(noaa_data(start,end,int(station),product='wind',interval=interval,t_zone='LST'))
    if len(noaa)>1:
        df = pd.DataFrame({'Datetime':[pd.to_datetime(noaa['data'][i]['t']) for i in range(len(noaa['data']))],
                      'Speed':[float(noaa['data'][i]['s']) if noaa['data'][i]['s']!='' else np.nan for i in range(len(noaa['data']))],
                      'Direction':[float(noaa['data'][i]['d']) if noaa['data'][i]['d']!='' else np.nan for i in range(len(noaa['data']))]})
        WR = WindRose(df)
        names = {'Speed':'ws','Direction': 'wd'}
        WR.calc_stats(normed=False, bins=8, variable_names=names)
        WR.wind_df.groupby(['direction','speed']).sum().loc['N']
        fig = WR.plot(output_type='return')
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(l=1, r=1, t=1, b=1),
            height=400,width=450,legend=dict(title='Speed m/s'))
    return fig

# ---------------------- Leaflet Map ---------------------------------------------------------------

root = pl.Path('./data')
shp = pd.read_csv(root / 'CO-OPS' /'CO-OPS.csv')
lons_o,lats_o = shp['X'],shp['Y']
stations = []
for name in shp['StatName']:
    stations.append(name)

points,marks,texts=[],[],[]
for i in range(len(stations)):
    #test = shp[
    #shp.select_dtypes(object)
    #.apply(lambda row: row.str.contains(stations[i]), axis=1)
    #.any(axis=1)]
    text = str(shp['StatName'][i])
    texts.append(text)
    points.append(dict(tooltip=text,name=shp['StatName'][i],
        lat=lats_o[i],lon=lons_o[i]))

time = {'start':[],'end':[],'interval':[]}
time['start']=pd.to_datetime('20200101')
time['end']=pd.to_datetime('20200120')
time['interval']=6
# Create some markers.  
dtypes = ['Wind','Waves']

data = dlx.dicts_to_geojson(points)
icon = assign("""function(feature, latlng){
    const flag = L.icon({
    iconUrl: `https://www.freeiconspng.com/uploads/thunderstorm-icon-29.png`,
    iconSize: [30, 30]});
    return L.marker(latlng, {icon: flag});
}""")

wind = dl.GeoJSON(id="markers",data=dlx.dicts_to_geojson(points),options=dict(pointToLayer=icon))

# ---------------------- App -----------------------------------------------------------------------

chroma = "https://cdnjs.cloudflare.com/ajax/libs/chroma-js/2.1.0/chroma.min.js"
app = DashProxy(external_scripts=[chroma], prevent_initial_callbacks=True)

app.layout = html.Div(children=[
                      html.Div(className='row',
                               children=[
                                  html.Div(className='five columns div-user-controls',
                                    children=[
                                    html.H2('FHRL - Observed Data Analysis'),
                                    html.P('''Visualising NOAA Data'''),
                                    html.P(''''''),
                                    html.P('Start Time'),
                                    dcc.Input(
                                        id='input-1-state',
                                        type='text',
                                        value='2022',
                                        style={
                                            "display": "inline-block",
                                            'justifyContent':'center',
                                            'width':100}),
                                    dcc.Input(
                                        id='input-2-state',
                                        type='text',
                                        value='01',
                                        style={
                                            "display": "inline-block",
                                            'justifyContent':'center',
                                            'width':50}),
                                    dcc.Input(
                                        id='input-3-state',
                                        type='text',
                                        value='01',
                                        style={
                                            "display": "inline-block",
                                            'justifyContent':'center',
                                            'width':50}),
                                    html.P('End Time'),
                                    dcc.Input(
                                        id='input-4-state',
                                        type='text',
                                        value='2022',
                                        style={
                                            "display": "inline-block",
                                            'justifyContent':'center',
                                            'width':100}),
                                    dcc.Input(
                                        id='input-5-state',
                                        type='text',
                                        value='01',
                                        style={
                                            "display": "inline-block",
                                            'justifyContent':'center',
                                            'width':50}),
                                    dcc.Input(
                                        id='input-6-state',
                                        type='text',
                                        value='20',
                                        style={
                                            "display": "inline-block",
                                            'justifyContent':'center',
                                            'width':50}),
                                    html.P(id='output-state'),
                                    html.P("\n"),
                                    html.P("\n"),
                                    html.P('Data interval: 6min (6) or hourly (h)'),
                                    dcc.Input(
                                        id='interval_input',
                                        type='text',
                                        value='6',
                                        style={
                                            "display": "inline-block",
                                            'justifyContent':'center',
                                            'width':40}),
                                    html.Button(
                                        id='submit-button-state',
                                        n_clicks=0,
                                        children='Submit'),                                    
                                    html.Div(className='div-for-dropdown',
                                        children=[
                                        dcc.Dropdown(id='datatype',
                                            options=dtypes,
                                            value=dtypes[0],
                                            style={'backgroundColor': '#1E1E1E'},
                                            className='dataselecter')],
                                        style={'color': '#1E1E1E'}),
                                    html.Div(id='location'),
                                    dcc.Graph(id='windrose',animate=False)],
                                    style={
                                            'margin': "auto",
                                            "display": "inline-block",
                                            'vertical-align': 'right'}
                                    ),
                                  html.Div(className='seven columns div-for-charts bg-grey',
                                    children=[
                                        dl.Map(
                                            center=(38.5, -76),
                                            zoom=8,
                                            children=[
                                            dl.TileLayer(),
                                            wind],
                                            style={
                                            'height': '90vh',
                                            'width' : '90%',
                                            'margin': "auto",
                                            'color': '#1E1E1E',
                                            "display": "inline-block",
                                            'vertical-align': 'left'},
                                            id="map"
                                            )
                                        ]
                                        ),
                                  ])])

# ---------------------- Call Backs ----------------------------------------------------------------

@app.callback(dash.Output('output-state', 'children'),
              dash.Input('submit-button-state', 'n_clicks'),
              dash.State('input-1-state', 'value'),
              dash.State('input-2-state', 'value'),
              dash.State('input-3-state', 'value'),
              dash.State('input-4-state', 'value'),
              dash.State('input-5-state', 'value'),
              dash.State('input-6-state', 'value'),
              dash.State('interval_input', 'value'))
def update_output(n_clicks, input1, input2,input3,input4,input5,input6,interval):
    start = pd.to_datetime(input1+input2+input3)
    end = pd.to_datetime(input4+input5+input6)

    if '6' in interval:
        days = end - start
        if days.days<30:
            time['start'] = start
            time['end'] = end
            time['interval']=interval
            return
        else:
            return 'Need to be within 30 days if using 6min interval'


@app.callback(
    dash.Output('windrose', 'figure'),
    dash.Input('markers', 'click_feature'),
    dash.Input('markers', 'n_clicks'),)
def update_figure(feature,n_clicks):
    if feature is not None:
        start = time['start']
        end = time['end']
        interval = str(time['interval'])
        fig = gen_windrose(feature,start,end,interval=interval)
        return fig


        


# ---------------------- Initialize App ------------------------------------------------------------

if __name__ == '__main__':
    app.run_server(debug=True)
