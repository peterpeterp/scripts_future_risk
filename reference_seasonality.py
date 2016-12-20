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
in_vars=['pr','tas','spei']

##############
# CMIP5
##############

rcp_str=['RCP26','RCP85']
cmip5={}
for varin in in_vars:
	cmip5[varin]={}
	for rcp in rcp_str:
		cmip5[varin][rcp]={}
		cmip5[varin][rcp]['models']={}

		if varin!='spei':all_files=glob.glob('/Users/peterpfleiderer/Documents/Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/CMIP5/'+rcp+'/*'+varin+'*.csv')
		if varin=='spei':all_files=glob.glob('/Users/peterpfleiderer/Documents/Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/CMIP5/'+rcp+'/spei_*1m*.csv')

		for file in all_files:
			if varin!='spei':model_name=file.split('/')[-1].split('_')[2]
			if varin=='spei':model_name=file.split('/')[-1].split('_')[1]
			cmip5[varin][rcp]['models'][model_name]={}
			tmp=pd.read_csv(file,header=0)[iso]
			cmip5[varin][rcp]['models'][model_name]['values']=np.ma.masked_invalid(tmp)
			if varin=='tas':cmip5[varin][rcp]['models'][model_name]['values']-=273.15

	for rcp in rcp_str:		
		cmip5[varin][rcp]['ensemble_mean']={}
		cmip5[varin][rcp]['ensemble_mean']['values']=cmip5[varin][rcp]['models'][cmip5[varin][rcp]['models'].keys()[0]]['values'].copy()
		for i in range(1,5):
			cmip5[varin][rcp]['ensemble_mean']['values']+=cmip5[varin][rcp]['models'][cmip5[varin][rcp]['models'].keys()[i]]['values']
		cmip5[varin][rcp]['ensemble_mean']['values']/=5

		

cmip5['time']=np.array(pd.read_csv(file,header=0)['time'])
cmip5['year']= np.array([int(tt/100) for tt in cmip5['time']])
cmip5['month']=cmip5['time']-cmip5['year']*100
cmip5['single_year']=cmip5['year'][np.where(cmip5['month']==1)[0]]

for varin in in_vars:
	for rcp in rcp_str:
		cmip5[varin][rcp]['ensemble_mean']['monthly_sorted']={}
		for month in range(1,13):
			cmip5[varin][rcp]['ensemble_mean']['monthly_sorted'][month]=np.ma.masked_invalid(cmip5[varin][rcp]['ensemble_mean']['values'][np.where(cmip5['month']==month)[0]])

		for model in cmip5[varin][rcp]['models'].keys():
			cmip5[varin][rcp]['models'][model]['monthly_sorted']={}
			for month in range(1,13):
				cmip5[varin][rcp]['models'][model]['monthly_sorted'][month]=np.ma.masked_invalid(cmip5[varin][rcp]['models'][model]['values'][np.where(cmip5['month']==month)[0]])



period1=np.where((cmip5['single_year']>1985) & (cmip5['single_year']<=2005))[0]
period2=np.where((cmip5['single_year']>2025) & (cmip5['single_year']<=2045))[0]
period3=np.where((cmip5['single_year']>2035) & (cmip5['single_year']<=2055))[0]

period_str=['Reference','2030s','2040s']
periods=[period1,period2,period3]

for varin in in_vars:
	for rcp in rcp_str:
		cmip5[varin][rcp]['ensemble_mean']['climatology']={}
		for per in range(3):
			cmip5[varin][rcp]['ensemble_mean']['climatology'][period_str[per]]=[]
			for month in range(1,13):
				cmip5[varin][rcp]['ensemble_mean']['climatology'][period_str[per]].append(np.mean(np.ma.masked_invalid(cmip5[varin][rcp]['ensemble_mean']['monthly_sorted'][month])[periods[per]]))

		for model in cmip5[varin][rcp]['models'].keys():
			cmip5[varin][rcp]['models'][model]['climatology']={}
			for per in range(3):
				cmip5[varin][rcp]['models'][model]['climatology'][period_str[per]]=[]
				for month in range(1,13):
					cmip5[varin][rcp]['models'][model]['climatology'][period_str[per]].append(np.mean(np.array(cmip5[varin][rcp]['models'][model]['monthly_sorted'][month])[periods[per]]))

##############
# OBS
##############
in_vars=['pr','tas','spei']

data_str=['NCEP','CRU']
obs={}
for varin in in_vars:
	obs[varin]={}
	for data in data_str:
		obs[varin][data]={}

		if data=='NCEP':
			if varin!='spei':file=glob.glob('/Users/peterpfleiderer/Documents/Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/OBS/'+data+'/*'+varin+'*.csv')[0]
			if varin=='spei':file=glob.glob('/Users/peterpfleiderer/Documents/Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/OBS/'+data+'/SPEI*1m*.csv')[0]
		if data=='CRU':
			if varin=='pr':file=glob.glob('/Users/peterpfleiderer/Documents/Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/OBS/'+data+'/*pre*.csv')[0]
			if varin=='tas':file=glob.glob('/Users/peterpfleiderer/Documents/Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/OBS/'+data+'/*tmp*.csv')[0]
			if varin=='spei':file=glob.glob('/Users/peterpfleiderer/Documents/Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/OBS/'+data+'/spei*01*.csv')[0]

		tmp=np.array(pd.read_csv(file,header=0)[iso])
		obs[varin][data]['values']=np.ma.masked_invalid(tmp)


		obs[varin][data]['time']=np.array(pd.read_csv(file,header=0)['time'])
		obs[varin][data]['year']= np.array([int(tt/100) for tt in obs[varin][data]['time']])
		obs[varin][data]['month']=obs[varin][data]['time']-obs[varin][data]['year']*100
		obs[varin][data]['single_year']=obs[varin][data]['year'][np.where(obs[varin][data]['month']==1)[0]]

for varin in in_vars:
	for data in data_str:
		obs[varin][data]['monthly_sorted']={}
		for month in range(1,13):
			obs[varin][data]['monthly_sorted'][month]=obs[varin][data]['values'][np.where(obs[varin][data]['month']==month)[0]]

			period1=np.where((obs[varin][data]['single_year']>1985) & (obs[varin][data]['single_year']<=2005))[0]
			period2=np.where((obs[varin][data]['single_year']>1951) & (obs[varin][data]['single_year']<=1980))[0]
			period_str=['Reference','Ref2']
			obs[varin][data]['periods']=[period1,period2]

for varin in in_vars:
	for data in data_str:
		obs[varin][data]['climatology']={}
		for per in range(2):
			obs[varin][data]['climatology'][period_str[per]]=[]
			for month in range(1,13):
				obs[varin][data]['climatology'][period_str[per]].append(np.mean(obs[varin][data]['monthly_sorted'][month][obs[varin][data]['periods'][per]]))


##############
# checkout SPEI -2 events
##############
for varin in ['spei']:
	for data in data_str:
		period=np.where((obs[varin][data]['year']>1985) & (obs[varin][data]['year']<=2005))[0]
		relevant_months=obs[varin][data]['values'][period]
		extreme=np.where(relevant_months<=-2)[0]
		obs[varin][data]['extreme_events']={}
		obs[varin][data]['extreme_events']['month']=obs[varin][data]['month'][period][extreme]
		obs[varin][data]['extreme_events']['year']=obs[varin][data]['year'][period][extreme]




fig = plt.figure()
plt.plot(range(1,13),cmip5['pr']['RCP26']['ensemble_mean']['climatology']['Reference'],label='CMIP5')
#plt.plot(range(1,13),obs['pr']['CRU']['climatology']['Reference'],label='CRU')
plt.plot(range(1,13),obs['pr']['NCEP']['climatology']['Reference'],label='NCEP')
plt.legend()
plt.ylabel('precipitation [mm]')
plt.xlim([1,12])
#plt.title(rcp,size='large')
plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/pr_seasonality_.png')

fig = plt.figure()
plt.plot(range(1,13),cmip5['tas']['RCP26']['ensemble_mean']['climatology']['Reference'],label='CMIP5')
plt.plot(range(1,13),obs['tas']['CRU']['climatology']['Reference'],label='CRU')
plt.plot(range(1,13),obs['tas']['NCEP']['climatology']['Reference'],label='NCEP')
plt.legend()
plt.ylabel('temperature [deg C]')
plt.xlim([1,12])
#plt.title(rcp,size='large')
plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/tas_seasonality_.png')

fig = plt.figure()
plt.plot(range(1,13),cmip5['spei']['RCP26']['ensemble_mean']['climatology']['Reference'],label='CMIP5',color='r')
for model in cmip5[varin][rcp]['models'].keys():
	print cmip5['spei']['RCP26']['models'][model]['climatology']['Reference']
	plt.plot(range(1,13),cmip5['spei']['RCP26']['models'][model]['climatology']['Reference'],color='r',linestyle=':')

plt.plot(range(1,13),obs['spei']['CRU']['climatology']['Reference'],label='CRU')
plt.plot(range(1,13),obs['spei']['NCEP']['climatology']['Reference'],label='NCEP')
plt.legend()
plt.ylabel('SPEI')
plt.xlim([1,12])
#plt.title(rcp,size='large')
plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/spei_seasonality_.png')


