############## MVP Itaú Reviews ##############
import streamlit as st
import numpy as np
import pandas as pd
import requests
import warnings
import json
import datetime
import os
import base64
from io import BytesIO
def ignore_warn(*args, **kwargs):
    pass
warnings.warn = ignore_warn


# Função para transformar df em excel
def to_excel(df):
	output = BytesIO()
	writer = pd.ExcelWriter(output, engine='xlsxwriter')
	df.to_excel(writer, sheet_name='Planilha1',index=False)
	writer.save()
	processed_data = output.getvalue()
	return processed_data
	
# Função para gerar link de download
def get_table_download_link(df):
	val = to_excel(df)
	b64 = base64.b64encode(val)
	return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="extract.xlsx">Download</a>'

st.title('MVP - Reviews de múltiplos apps')
st.write('Este MVP tem como objetivo possibilitar a exportação de dados de reviews múltiplos aplicativos ao mesmo tempo.')
st.write('A ferramenta permite a seleção do período desejado, coleta de todos os aplicativos, por loja ou de forma personalizada, selecionando os aplicativos desejados')
st.write("")

######### Requisição do token #########
url = "https://api-gateway.apps.rmabeta.rankmyapp.com/api/users/authenticate"

payload = json.dumps({
  "name": "",
  "email": "giovanni.zanatta@rankmyapp.com.br",
  "company": "",
  "occupation": "",
  "password": "tool_giovanni"
})
headers = {
  'authority': 'api-gateway.apps.rmabeta.rankmyapp.com',
  'accept': 'application/json',
  'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
  'authorization': 'Bearer null',
  'content-type': 'application/json',
  'origin': 'https://tool.rmabeta.rankmyapp.com',
  'referer': 'https://tool.rmabeta.rankmyapp.com/',
  'sec-ch-ua': '"Chromium";v="106", "Microsoft Edge";v="106", "Not;A=Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-site',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36 Edg/106.0.1370.34'
}

response = requests.request("POST", url, headers=headers, data=payload)

if response.status_code != 200:
    print('Erro na requisição')

token = response.json()['token']

######### appIds e AppNames #########
appNameApple = ['Itaú Cartões (apple)','Cartão Luiza (apple)','Hipercard (apple)','Credicard (apple)','Credicard On (apple)',
								'Samsung Itaucard (apple)','Players Bank (apple)','Banco Itaú (apple)','Personnalité (apple)','íon Itaú (apple)',
								'Rede (apple)','Itaú Empresas (apple)']
appIdApple = ['com.itau.itaucard','com.itau.magalu','com.itau.hipercard','com.itau.credicard','com.odete.credicard',
              'com.odete.samsung','com.odete.playersbank','com.itau.iphone.varejo','com.itau.iphone.personnalite',
              'com.itau.investimentos','br.com.userede.rede','com.itau.empresa']

appNameGoogle = ['Itaú Cartões (google)','Cartão Luiza (google)','Hipercard (google)','Credicard (google)',
                 'Credicard On (google)','Samsung Itaucard (google)','Players Bank (google)','Banco Itaú (google)',
                 'Personnalité (google)','íon Itaú (google)','Rede (google)','Itaú Empresas (google)']
appIdGoogle = ['com.itaucard.activity','com.luizalabs.mlapp','com.hipercard.app','com.credicard.app','com.odete.credicard',
               'com.odete.samsung','com.odete.playersbank','com.itau','com.itau.pers','com.itau.investimentos',
               'br.com.userede','com.itau.empresas']

dfAppApple = pd.DataFrame({'appName':appNameApple, 'appId':appIdApple,'store':'apple'})
dfAppGoogle = pd.DataFrame({'appName':appNameGoogle, 'appId':appIdGoogle,'store':'google'})

dfApps = pd.concat([dfAppApple,dfAppGoogle]).reset_index(drop=True)

# Seleção de datas e apps
startDate = str(st.date_input('Data Inicial'))
endDate = str(st.date_input('Data Final'))

appSelectMode = st.radio('Como deseja selecionar os aplicativos?', ('Todos os apps', 'Por loja', 'Personalizado'))

if appSelectMode == 'Todos os apps':
	dfFilterApps = dfApps
	FilterApps = list(zip(dfApps['appId'],dfApps['store']))

if appSelectMode == 'Por loja':

	selectLoja = st.radio('Selecione a Loja:',('apple','google'))

	if selectLoja == 'apple':

		dfFilterApps = dfApps[dfApps['store'] == 'apple']
		FilterApps = list(zip(dfFilterApps['appId'],dfFilterApps['store']))

	if selectLoja == 'google':

		dfFilterApps = dfApps[dfApps['store'] == 'google']
		FilterApps = list(zip(dfFilterApps['appId'],dfFilterApps['store']))

if appSelectMode == 'Personalizado':

	personApps = st.multiselect("Selecione os apps:", dfApps['appName'].unique())
	dfFilterApps = dfApps[dfApps['appName'].isin(personApps)]
	FilterApps = list(zip(dfFilterApps['appId'],dfFilterApps['store']))

# Visualização dos apps selecionados
st.write(dfFilterApps)

#### Gerar Planilha
btn = st.button('Gerar Planilha')

if btn:

	######### Requisição de dados #########
	list_resquests = []

	for i, j in FilterApps:

		url = 'https://gateway.rankmyapp.com/api/apps/{app}/reviews?country=br&end={endDate}&lang=pt-BR&page=0&start={startDate}&store={store}&timezoneOffset=180&order=date'.format(app=i, startDate=startDate, endDate=endDate, store=j)
		payload={}
		headers = {
		'authority': 'gateway.rankmyapp.com',
		'accept': 'application/json',
		'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
		'authorization': 'Bearer {token}'.format(token=token),
		'origin': 'https://tool.rankmyapp.com/',
		'referer': 'https://tool.rankmyapp.com/',
		'sec-ch-ua': '"Microsoft Edge";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
		'sec-ch-ua-mobile': '?0',
		'sec-ch-ua-platform': '"Windows"',
		'sec-fetch-dest': 'empty',
		'sec-fetch-mode': 'cors',
		'sec-fetch-site': 'same-site',
		'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36 Edg/105.0.1343.53'
		}

		response = requests.request("GET", url, headers=headers, data=payload)

		if response.status_code != 200:
			print('Erro na requisição')
	        
		list_resquests.append(response.json())


	####### Normalização e Tratamento de dados
	dfRevs = pd.DataFrame(list_resquests)

	explodedRev = dfRevs.explode('reviews')
	df_exp_rev = pd.concat([explodedRev.reset_index(drop=True),
		pd.json_normalize(explodedRev['reviews'])], axis=1)

	df_exp_rev = df_exp_rev.merge(dfApps, how='left', left_on=['appId','store'],right_on=['appId','store'])
	df_exp_rev.dropna(subset='store', inplace=True)

	#df_exp_rev['store'].unique() == ['apple']
	if 'apple' in set(df_exp_rev['store']):
		df_exp_rev['lang'] = np.nan
		df_exp_rev['thumbsUp'] = np.nan
		df_exp_rev['criterias'] = np.nan

	# Selecionando colunas necessárias
	cols = ['appId','store','userName','date','score','title','text','category','subcategory','sentiment','lang',
					'replyDate','replyTimeBusinessMinutes','replyText','thumbsUp','version','criterias','appName']

	df_cols = df_exp_rev[cols]

	######### Tratamento do Df #########
	# Separando Data e hora do review
	df_cols['time'] = df_cols['date'].str.split('T').str[1]
	df_cols['time'] = df_cols['time'].str.split('.').str[0]
	df_cols['date'] = df_cols['date'].str.split('T').str[0]

	# Separando Data e hora da resposta
	df_cols['replyTime'] = df_cols['replyDate'].str.split('T').str[1]
	df_cols['replyTime'] = df_cols['replyTime'].str.split('.').str[0]
	df_cols['replyDate'] = df_cols['replyDate'].str.split('T').str[0]

	# Renomeando colunas
	df_cols.rename(columns={'userName':'Username','date':'Date','score':'Rating','title':'Title','text':'Text','store':'Store',
													'category':'Category','subcategory':'Subcategory','sentiment':'Sentiment','lang':'Location',
													'replyDate':'Reply Date','replyText':'Reply Text','thumbsUp':'Thumbs Up','version':'Version',
													'criterias':'Criterias','time':'Review Time','replyTime':'Reply Time','appName':'Name',
													'replyTimeBusinessMinutes':'SLA Business Minutes'}, inplace=True)


	colsOrd = ['appId','Name','Store','Username','Date','Review Time','Rating','Title','Text','Category',
				'Subcategory','Sentiment','Location','Reply Date','Reply Time','SLA Business Minutes',
				'Reply Text','Thumbs Up','Version','Criterias']

	df_cols = df_cols[colsOrd]

	###### Resumo do df
	dfStats = dfFilterApps.merge(df_cols, how='left', left_on='appName',right_on='Name')
	dfStatsFinal = dfStats[['appName','Text']].groupby('appName')['Text'].count().reset_index(name='Volume de Reviews')

	st.subheader('Resumo')
	st.write(dfStatsFinal)
	st.subheader('Prévia da Planilha')
	st.write(df_cols)
	st.write('Clique em Download para baixar o arquivo')
	st.markdown(get_table_download_link(df_cols), unsafe_allow_html=True)











