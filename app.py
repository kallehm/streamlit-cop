from logging import error
from pandas.core.frame import DataFrame
import streamlit as st
import numpy as np
import pandas as pd
import requests
from requests.exceptions import HTTPError
from requests.models import Response
import json
import matplotlib
from collections import Counter
import time

st.set_page_config(
     page_title="Brottsanalys Polismyndigheten Sverige",
     page_icon="🧊",
     layout="centered",
     initial_sidebar_state="expanded",
)


symbol = st.sidebar.text_input('Stad', value='', help='Sök på stad')
screen = st.sidebar.selectbox("View", ('Sammanfattning', 'Händelser'))

st.title(screen)

if error:
    st.write('')

### Sammanfattning 

if screen == "Sammanfattning":
    antal_api = st.slider('Antal brott för analysen', min_value=1, max_value=200, value=10)
    api_antal = st.write('Graferna visar en sammanställning på',antal_api,'inrapporterade händelser från polisens system.')
    url = f'https://polisen.se/api/events?locationname={symbol}'
    st.markdown(f'Analysen nedan baserar på information från: {symbol.title() or "Sverige"}')
    r = requests.get(url)
    respons_json = r.json()
    st.write(f"""Inhämtning har automatiskt skett på {antal_api} inrapporterade händelser från polisens system. Senaste 
                        inrapporteringen skedde {respons_json[0]['datetime'][:16]} och handlande om: {respons_json[0]['summary']}""")

    chart_data= []
    datum = []
    for i in respons_json[:antal_api]:
        datum.append(i['datetime'])
        chart_data.append(i['type'])
    
    chart_data = pd.DataFrame(chart_data, columns=['Sammanfattning'])
    datum = pd.DataFrame(datum, columns=['Datum'])
    st.write(F"Datum för nedan analys är baserad på tidsramarna: {datum['Datum'].min()} --- {datum['Datum'].max()}")
    chart_data3 = chart_data['Sammanfattning'].value_counts()
    topp_brott = chart_data.value_counts().head(1)
    st.subheader(str(topp_brott).split(' ')[1])
    st.subheader(f"I urvalet som du gjorde förekom det {len(chart_data)} brott i {(len(chart_data3.index))} olika brottskategorier.")



    st.subheader((str(topp_brott).split(' ')[0]))
    st.area_chart(chart_data3)

    chart_data = []
    for i in respons_json[:int(antal_api)]:
        chart_data.append(i['datetime'])

    
    chart_data_tid = pd.DataFrame(chart_data, columns=['Tid'])
    chart_data_tid['Tid'] = pd.to_datetime(chart_data_tid['Tid'])
    days = {0:'Måndag',1:'Tisdag',2:'Onsdag',3:'Torsdag',4:'Fredag',5:'Lördag',6:'Söndag'}
    chart_data_tid['dag'] = chart_data_tid['Tid'].dt.dayofweek
    chart_data_tid['dag'] = chart_data_tid['dag'].apply(lambda x: days[x])
    st.subheader(f"Veckodag baserat på {len(chart_data)} brott")
    st.bar_chart(chart_data_tid['dag'].value_counts())

    chart_data_tid = chart_data_tid['Tid'].dt.hour.value_counts()
    st.subheader(f"Tid på dygnet då brottet inträffade baserat på {len(chart_data)} brott")
    st.bar_chart(chart_data_tid)


    chart_data= []
    
    for i in respons_json[:int(antal_api)]:
        chart_data.append(i['name'])
        
    
    chart_data_namn = pd.DataFrame(chart_data, columns=['namn'])
    st.subheader('Sammanfattning brottsinfo i fallande datum/tids ordning')
    st.write('')
    N = st.slider('Antal brott', min_value=5, max_value=20, value=5)
    for i in chart_data[:N]:
        st.markdown(i)

    gps = []
    for i in respons_json[:antal_api]:
        gps.append(i['location']['gps'])
    df = DataFrame(gps,columns=['data'])
    df[['lat','lon']] = df.data.str.split(",",expand=True,)
    del df['data']
    
    df['lat'] = df['lat'].astype(float)
    df['lon'] = df['lon'].astype(float)

    st.subheader('Städer :pushpin:')
    st.text("""
    Markeringarna visar på städer där brott utifrån dina val 
    har rapporterats in från polisen.se. Ifall du väljer att söka 
    på en speficik stad kommer medelpunkten på staden att visas på kartbilden nedan
    """)
    st.map(df)
    
### Händelser

if screen == 'Händelser':
    antal_api = st.slider('Antal brott för analysen', min_value=10, max_value=300, value=10)
    url = f'https://polisen.se/api/events?locationname={symbol}'
    st.markdown(f'Analysen nedan baserar på information från: {symbol.title() or "Sverige"}')
    r = requests.get(url)
    respons_json = r.json()
    st.write(f"""Inhämtning har automatiskt skett på {antal_api} inrapporterade händelser från polisens system. Senaste 
                        inrapporteringen skedde {respons_json[0]['datetime'][:16]} och handlande om: {respons_json[0]['summary']}""")
    
    chart_data = []
    for i in respons_json[:antal_api]:
        chart_test = {
            'Datum':i['datetime'].split(' ')[0],
            'Tid':i['datetime'].split(' ')[1],
            'Typ':i['type'],
            'Text':i['summary']}

        chart_data.append(chart_test)
    chart_data = pd.DataFrame(chart_data)
    type = chart_data['Typ'].unique()

    option = st.selectbox('Välj brottskategori',(type))

    valavbrott = chart_data[chart_data['Typ'] == option]
    st.text(valavbrott)

    st.subheader(f"Totalt kan {len(valavbrott.index)} brott hittas av de {antal_api} som inhämtas kopplat mot brottskategorin du valt som sträcker sig mellan datumen {chart_data['Datum'].max()} - {chart_data['Datum'].min()} hittats.")

st.write('')
st.write('')
st.write('')
st.write('')
expander = st.beta_expander("FAQ")
expander.write("""Information är hämtad från Polismyndigheten och hämtas kontinuerligt. Syftet är att få sammanställning kring brottsligheten kopplat mot dit egna val""")
