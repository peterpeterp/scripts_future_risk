import sys,os,glob
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import pandas as pd

from mpl_toolkits.basemap import Basemap, cm
import mpl_toolkits.basemap
import matplotlib.pylab as plt
from matplotlib import ticker
from matplotlib.ticker import MaxNLocator


iso='MWI'

rcp_str=['RCP2.6','RCP8.5']

pr={}
all_files=glob.glob('/Users/peterpfleiderer/Documents/Projects/WB_DRM/climate_risk_data/'+iso+'/mon_pr_*.csv')


for rcp in rcp_str:
	pr[rcp]={}
	pr[rcp]['models']={}

for file in all_files:
	if file.split('/')[-1].split('_')[3]=='rcp2.6':
		pr['RCP2.6']['models'][file.split('/')[-1].split('_')[2]]=pd.read_csv(file,header=0)['MWI']
	if file.split('/')[-1].split('_')[3]=='rcp8.5':
		pr['RCP8.5']['models'][file.split('/')[-1].split('_')[2]]=pd.read_csv(file,header=0)['MWI']


pr['time']=pd.read_csv(file,header=0)['time']
pr['year']= np.array([int(tt/100) for tt in pr['time']])
pr['month']=pr['time']-pr['year']*100

for rcp in rcp_str:
	pr[rcp]['ensembel_mean']={}
	pr[rcp]['ensembel_mean']['values']=pr[rcp]['models'][pr[rcp]['models'].keys()[0]].copy()
	for i in range(1,5):
		pr[rcp]['ensembel_mean']['values']+=pr[rcp]['models'][pr[rcp]['models'].keys()[i]]
	pr[rcp]['ensembel_mean']['values']/=5


	pr[rcp]['ensembel_mean']['climatology']={}
	for month in range(1,13):
		pr[rcp]['ensembel_mean']['climatology'][month]=pr[rcp]['ensembel_mean']['values'][np.where(pr['month']==month)[0]]

	for model in pr[rcp]['models'].keys():
		pr[rcp]['models'][model]['climatology']={}
		for month in range(1,13):
			pr[rcp]['models'][model]['climatology'][month]=pr[rcp]['models'][model][np.where(pr['month']==month)[0]]

pr['single_year']=pr['year'][np.where(pr['month']==month)[0]]



period1=np.where((pr['single_year']>1985) & (pr['single_year']<=2005))[0]
period2=np.where((pr['single_year']>2025) & (pr['single_year']<=2045))[0]
period3=np.where((pr['single_year']>2035) & (pr['single_year']<=2055))[0]

period_str=['Reference','2030s','2040s']
periods=[period1,period2,period3]
period_colors=['g','b','r']


for rcp in rcp_str:
	pr[rcp]['ensembel_mean']['periods']={}
	for per in range(3):
		pr[rcp]['ensembel_mean']['periods'][period_str[per]]=[]
		for month in range(1,13):
			pr[rcp]['ensembel_mean']['periods'][period_str[per]].append(np.mean(np.array(pr[rcp]['ensembel_mean']['climatology'][month])[periods[per]]))

	for model in pr[rcp]['models'].keys():
		pr[rcp]['models'][model]['periods']={}
		for per in range(3):
			pr[rcp]['models'][model]['periods'][period_str[per]]=[]
			for month in range(1,13):
				pr[rcp]['models'][model]['periods'][period_str[per]].append(np.mean(np.array(pr[rcp]['models'][model]['climatology'][month])[periods[per]]))




for rcp in rcp_str:

	fig = plt.figure()
	for per in range(1,3):
		plt.plot(range(1,13),(np.array(pr[rcp]['ensembel_mean']['periods'][period_str[per]])-np.array(pr[rcp]['ensembel_mean']['periods'][period_str[0]]))/np.array(pr[rcp]['ensembel_mean']['periods'][period_str[0]]),label=period_str[per],color=period_colors[per])
		for model in pr[rcp]['models'].keys():
			plt.plot(range(1,13),(np.array(pr[rcp]['models'][model]['periods'][period_str[per]])-np.array(pr[rcp]['models'][model]['periods'][period_str[0]]))/np.array(pr[rcp]['models'][model]['periods'][period_str[0]]),color=period_colors[per],linestyle=':')

	plt.legend()
	plt.ylabel('rel. change in precipitation [%]')
	plt.xlim([1,12])
	plt.title(rcp,size='large')
	plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/pr_seasonality_rel_change'+rcp+'.png')



	fig = plt.figure()
	for per in range(0,3):
		plt.plot(range(1,13),pr[rcp]['ensembel_mean']['periods'][period_str[per]],label=period_str[per],color=period_colors[per])

		for model in pr[rcp]['models'].keys():
			plt.plot(range(1,13),pr[rcp]['models'][model]['periods'][period_str[per]],color=period_colors[per],linestyle=':')

	plt.legend()
	plt.ylabel('precipitation [mm]')
	plt.xlim([1,12])
	plt.title(rcp,size='large')
	plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/pr_seasonality_absolute'+rcp+'.png')






# iso='MWI'

# rcp_str=['RCP2.6','RCP8.5']
# rcp=0

# pr={}
# all_files=glob.glob('/Users/peterpfleiderer/Documents/Projects/WB_DRM/climate_risk_data/'+iso+'/mon_pr_*'+'rcp2.6'+'*.csv')

# pr['models']={}
# for file in all_files:
# 	pr['models'][file.split('/')[-1].split('_')[2]]=pd.read_csv(file,header=0)['MWI']

# pr['time']=pd.read_csv(file,header=0)['time']
# pr['year']= np.array([int(tt/100) for tt in pr['time']])
# pr['month']=pr['time']-pr['year']*100

# pr['ensembel_mean']=pr['models'][pr['models'].keys()[0]]
# for i in range(1,5):
# 	pr['ensembel_mean']+=pr['models'][pr['models'].keys()[i]]
# pr['ensembel_mean']/=5


# pr['climatology']={}
# for month in range(1,13):
# 	pr['climatology'][month]=pr['ensembel_mean'][np.where(pr['month']==month)[0]]

# pr['climatology']['year']=pr['year'][np.where(pr['month']==month)[0]]



# period1=np.where((pr['climatology']['year']>1985) & (pr['climatology']['year']<=2005))[0]
# period2=np.where((pr['climatology']['year']>2020) & (pr['climatology']['year']<=2040))[0]
# period3=np.where((pr['climatology']['year']>2079) & (pr['climatology']['year']<=2099))[0]

# period_str=['Reference','2030s','2040s']
# periods=[period1,period2,period3]



# pr['periods']={}
# for per in range(3):
# 	pr['periods'][period_str[per]]=[]
# 	for month in range(1,13):
# 		pr['periods'][period_str[per]].append(np.mean(pr['climatology'][month][periods[per]]))

# fig = plt.figure()
# for per in range(1,3):
# 	plt.plot(range(1,13),(np.array(pr['periods'][period_str[per]])-np.array(pr['periods'][period_str[0]]))/np.array(pr['periods'][period_str[0]]),label=period_str[per])

# plt.legend()
# plt.ylabel('rel. change in precipitation [%]')
# plt.xlim([1,12])
# plt.title(rcp_str[rcp],size='large')
# plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/pr_seasonality_rel_change'+rcp_str[rcp]+'.png')



# fig = plt.figure()
# for per in range(0,3):
# 	plt.plot(range(1,13),pr['periods'][period_str[per]],label=period_str[per])

# plt.legend()
# plt.ylabel('precipitation [mm]')
# plt.xlim([1,12])
# plt.title(rcp_str[rcp],size='large')
# plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/pr_seasonality_absolute'+rcp_str[rcp]+'.png')




