#!/usr/bin/python3
#
# Author: Domenico Zambella
# GNU General Public License v3.0


from pandas import read_csv, to_datetime
from bokeh.plotting import figure, save, output_notebook, output_file, ColumnDataSource
from bokeh.models import HoverTool
from bokeh.models.formatters import DatetimeTickFormatter

output_notebook(hide_banner=True)
param = dict(width = 700, height = 350,
             tools = 'ywheel_zoom, xwheel_zoom, ypan, xpan, save, reset'
            )
URL = 'https://raw.githubusercontent.com/pcm-dpc/COVID-19/master/dati-regioni/'

df = read_csv(URL + 'dpc-covid19-ita-regioni.csv',
              usecols = ['data','denominazione_regione','totale_ospedalizzati',
                         'terapia_intensiva','deceduti']
             )
              
# grafici regionali assoluti
              
df['data'] = to_datetime(df['data']).dt.date

regioni = df['denominazione_regione'].copy()
regioni = regioni.drop_duplicates()

# questo loop costruisce i grafici con i valori assoluti
for i,regione in regioni.items():
    p  = figure(x_axis_type='datetime', title = regione, **param)
    p.xaxis.formatter=DatetimeTickFormatter(days=["%d %B"])
    df_x = df[ df['denominazione_regione'] == regione ].copy()
    df_x['deceduti_diff'] = df_x['deceduti'].diff()
    source = ColumnDataSource(df_x)
    for i,c,l in zip(['totale_ospedalizzati','terapia_intensiva','deceduti_diff'],
                     ['green',        'red',                     'black'  ],
                     ['ospedalizzati','terapia intensiva',       'decessi']) :
        p.line(       x='data', y=i, source=source, color=c, legend_label=l )
        q = p.circle( x='data', y=i, source=source, color=c )  
        p.add_tools(HoverTool(renderers=[q], 
                              tooltips=[("data", "@data{%d %B}"), (l, "@"+i)],
                              formatters = { '@data' : 'datetime'},
                              mode = 'mouse',
                              toggleable = False,
                             )
                   )
    p.legend.location = "top_left"
    p.toolbar.logo=None
    output_file('./' + regione + '.html', title=regione)
    save( p) 
    
            
# grafici regionali relativi 
# i grafici vengono scritti nella directory "./rel/"
# la directory deve già esistere 

popolazione = dict({
           'Lombardia':10060574,
           'Lazio':5879082,
           'Campania':5801692,
           "Sicilia":4999891,
           "Veneto":4905854,
           "Emilia-Romagna":4459477,
           "Piemonte":4356406,
           "Puglia":4029053,
           "Toscana":3729641,
           "Calabria":1947131,
           "Sardegna":1639591 ,
           "Liguria":1550640,
           "Marche":1525271,
           "Abruzzo":1311580,
           "Friuli Venezia Giulia":1215220,
           "Umbria":882015,
           "Basilicata":562869,
           "P.A. Trento":538223,
           "P.A. Bolzano":520891,
           "Molise":305617,
           "Valle d'Aosta":125666,
         })

for i,regione in regioni.items():
    p  = figure(x_axis_type='datetime', title = regione, **param, y_range=(-1, 16))
    p.xaxis.formatter=DatetimeTickFormatter(days=["%d %B"])
    df_x = df[ df['denominazione_regione'] == regione ].copy()
    df_x['deceduti_diff'] = df_x['deceduti'].diff()
    df_x['totale_ospedalizzati'] = 10000 * df_x['totale_ospedalizzati'] / popolazione[regione]
    df_x['terapia_intensiva'] = 100000 * df_x['terapia_intensiva'] / popolazione[regione]
    df_x['deceduti_diff'] = 100000 * df_x['deceduti_diff'] / popolazione[regione]
    
    source = ColumnDataSource(df_x)
    for i,c,l in zip(['totale_ospedalizzati','terapia_intensiva','deceduti_diff'],
                     ['green',        'red',                     'black'  ],
                     ['ospedalizzati / 10 mila abitanti','terapia intensiva / 100 mila abitanti',       'decessi / 100 mila abitanti']) :
        p.line(       x='data', y=i, source=source, color=c, legend_label=l )
        q = p.circle( x='data', y=i, source=source, color=c )  
        q = p.circle( x='data', y=i, source=source, color=c )  
        p.add_tools(HoverTool(renderers=[q], 
                              tooltips=[("data", "@data{%d %B}"), (l, "@"+i)],
                              formatters = { '@data' : 'datetime'},
                              mode = 'mouse',
                              toggleable = False,
                             )
                   )
    totale_decessi = round(100000 * df_x['deceduti'].iloc[-1] / popolazione[regione], 1)
    p.title.text = regione + \
    '                              Totale decessi per 100 mila abitati:    {:.1f}'.format(totale_decessi)
    p.legend.location = "top_left"
    p.toolbar.logo=None
    output_file('./rel/' + regione + '.html', title=regione)
    save( p)
