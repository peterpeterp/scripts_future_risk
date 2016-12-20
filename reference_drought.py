import sys 
import glob
import numpy as np
from netCDF4 import Dataset,netcdftime,num2date
import pandas as pd

from mpl_toolkits.basemap import Basemap, cm
import mpl_toolkits.basemap
import matplotlib.pylab as plt
from matplotlib import ticker
from matplotlib.ticker import MaxNLocator

sys.path.append('/Users/peterpfleiderer/Documents/Scripts/allgemeine_scripte/')
from plot_functions import *
sys.path.append('/Users/peterpfleiderer/Documents/Projects/WB_DRM/')

iso='CMR'

#################
# CMIP5
#################

rcp='8.5'
all_files=glob.glob('/Users/peterpfleiderer/Documents/Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/CMIP5/RCP'+rcp+'/spei*12m*.nc4')
expo_cmip5={}
#expo_cmip5['periods']={'ref':1985,'2030s':2025,'2040s':2035}
expo_cmip5['periods']={'ref':1985,'2030s':2025,'2050s':2045,'2070s':2065}
for period in expo_cmip5['periods'].keys():
	expo_cmip5[period]={}

expo_cmip5['model_names']=[]

for file in all_files:
	model=file.split('/')[-1].split('_')[1]
	expo_cmip5['model_names'].append(model)

	print file
	nc_in=Dataset(file)

	try:spei=nc_in.variables['SPEI'][:]
	except:spei=nc_in.variables['spei'][:]

	# extract years from time variable
	time=nc_in.variables['time'][:]
	time_unit=nc_in.variables['time'].units
	datevar = []

	try:	# check if there is calendar information
		cal_temps = nc_in.variables['time'].calendar
		datevar.append(num2date(time,units = time_unit,calendar = cal_temps))
	except:
		datevar.append(num2date(time,units = time_unit))

	years=np.array([int(str(date).split("-")[0])\
		for date in datevar[0][:]])
	months=np.array([int(str(date).split("-")[1])\
		for date in datevar[0][:]])

	lat=nc_in.variables['lat'][:]
	lon=nc_in.variables['lon'][:]

	lon=lon.copy()
	step=np.diff(lon,1)[0]
	lon-=step/2
	lon=np.append(lon,np.array(lon[-1]+step))

	lat=lat.copy()
	step=np.diff(lat,1)[0]
	lat-=step/2
	lat=np.append(lat,lat[-1]+step)

	lons, lats = np.meshgrid(lon,lat)

	expo_cmip5[model]={}
	expo_cmip5[model]['lon'], expo_cmip5[model]['lat'] = np.meshgrid(lon,lat)

	for period in expo_cmip5['periods'].keys():
		start_year=expo_cmip5['periods'][period]
		relevant_data_indices=np.where((years>start_year) & (years<=start_year+20))[0]
		tmp=spei[0,:,:].copy()

		for y in range(tmp.shape[0]):
			for x in range(tmp.shape[1]):
				tmp[y,x]=float(len(np.where(spei[relevant_data_indices,y,x].flatten()<=-2)[0]))/len(relevant_data_indices)

		expo_cmip5[period][model]=tmp

for period in expo_cmip5['periods'].keys():
	expo_cmip5[period]['ensemble mean']=expo_cmip5[period][expo_cmip5['ref'].keys()[0]].copy()*0
	for model in expo_cmip5['ref'].keys():
		expo_cmip5[period]['ensemble mean']+=expo_cmip5[period][model]
	expo_cmip5[period]['ensemble mean']/=5

for period in expo_cmip5['periods'].keys():
	if period !='ref':
		expo_cmip5[period]['diff']={}
		for model in expo_cmip5['ref'].keys():
			if model not in ['agreement','diff']:	
				expo_cmip5[period]['diff'][model]=expo_cmip5[period][model]-expo_cmip5['ref'][model]


		expo_cmip5[period]['diff']['agreement']=expo_cmip5[period][expo_cmip5['ref'].keys()[0]].copy()*0
		for model in expo_cmip5['ref'].keys():
			if model not in ['ensemble mean','agreement','diff']:
				print period,model
				expo_cmip5[period]['diff']['agreement'][np.where(np.sign(expo_cmip5[period]['diff'][model])==np.sign(expo_cmip5[period]['diff']['ensemble mean']))]+=1
		expo_cmip5[period]['diff']['agreement'][expo_cmip5[period]['diff']['agreement']>3]=np.nan
		expo_cmip5[period]['diff']['agreement'][np.isnan(expo_cmip5[period]['diff']['agreement'])==False]=0.5


#################
# observational
#################

all_files=glob.glob('/Users/peterpfleiderer/Documents/Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/OBS/CRU/spei12*.nc')
all_files.append(glob.glob('/Users/peterpfleiderer/Documents/Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/OBS/NCEP/SPEI*12m*.nc')[0])
expo_obs={}
expo_obs['periods']={'ref':1985}
for period in expo_obs['periods'].keys():
	expo_obs[period]={}

expo_obs['datasets']=[]

for file in all_files:
	dataset=file.split('/')[-2]
	expo_obs['datasets'].append(dataset)

	nc_in=Dataset(file)

	try:spei=nc_in.variables['SPEI'][:]
	except:spei=nc_in.variables['spei'][:]

	# extract years from time variable
	time=nc_in.variables['time'][:]
	time_unit=nc_in.variables['time'].units
	datevar = []

	try:	# check if there is calendar information
		cal_temps = nc_in.variables['time'].calendar
		datevar.append(num2date(time,units = time_unit,calendar = cal_temps))
	except:
		datevar.append(num2date(time,units = time_unit))

	years=np.array([int(str(date).split("-")[0])\
		for date in datevar[0][:]])
	months=np.array([int(str(date).split("-")[1])\
		for date in datevar[0][:]])

	lat=nc_in.variables['lat'][:]
	lon=nc_in.variables['lon'][:]

	lon=lon.copy()
	step=np.diff(lon,1)[0]
	lon-=step/2
	lon=np.append(lon,np.array(lon[-1]+step))

	lat=lat.copy()
	step=np.diff(lat,1)[0]
	lat-=step/2
	lat=np.append(lat,lat[-1]+step)

	expo_obs[dataset]={}
	expo_obs[dataset]['lon'], expo_obs[dataset]['lat'] = np.meshgrid(lon,lat)

	for period in expo_obs['periods'].keys():
		start_year=expo_obs['periods'][period]
		relevant_data_indices=np.where((years>start_year) & (years<=start_year+20))[0]
		tmp=spei[0,:,:].copy()

		expo_obs[period][dataset+'_extremes']=[]
		for y in range(tmp.shape[0]):
			for x in range(tmp.shape[1]):
				tmp[y,x]=float(len(np.where(spei[relevant_data_indices,y,x].flatten()<=-2)[0]))/len(relevant_data_indices)
				expo_obs[period][dataset+'_extremes'].extend(months[np.where(spei[:,y,x].flatten()<=-2)[0]])

		expo_obs[period][dataset]=tmp


##########
# plot extreme months
##########
fig,axes=plt.subplots(nrows=1,ncols=2,figsize=(7,3))
ax=axes.flatten()[0]
ax.hist(expo_obs['ref']['NCEP_extremes'])
ax.set_xlim([1,12])
ax.set_title('NCEP')

ax=axes.flatten()[1]
ax.hist(expo_obs['ref']['CRU_extremes'])
ax.set_xlim([1,12])
ax.set_title('CRU')

plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_spei_12m_ref_extreme_hist.png')
plt.clf()

###########
# plot reference
###########
fig,axes=plt.subplots(nrows=1,ncols=7,figsize=(7,3))
count=0

for dataset in expo_obs['datasets']:
	Z=expo_obs['ref'][dataset]
	Z[Z==0]=np.nan
	ax,im=plot_map(axes.flatten()[count],expo_obs[dataset]['lon'],expo_obs[dataset]['lat'],Z*100,color_type=plt.cm.YlOrBr,color_range=[0,20],color_label=None,subtitle=dataset,limits=[7.5, 17.5, 0.5, 14.5])
	count+=1

for model in expo_cmip5['model_names']:
	Z=expo_cmip5['ref'][model]
	Z[Z==0]=np.nan
	ax,im=plot_map(axes.flatten()[count],expo_cmip5[model]['lon'],expo_cmip5[model]['lat'],Z*100,color_type=plt.cm.YlOrBr,color_range=[0,20],color_label=None,subtitle='',limits=[7.5, 17.5, 0.5, 14.5])
	ax.set_title('CMIP5\n'+model,fontsize=7)
	count+=1


cbar_ax=fig.add_axes([0,0.17,1,0.3])
cbar_ax.axis('off')
cb=fig.colorbar(im,orientation='horizontal',label='ratio of months affected by SPEI -2 [%]')
tick_locator = ticker.MaxNLocator(nbins=5)
cb.locator = tick_locator
cb.update_ticks()

plt.suptitle('Refernce Period 1986-2005')
#fig.tight_layout()
plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_spei_12m_ref.png')
plt.clf()




########
# huge plot overview
########
model_names=expo_cmip5['model_names'][0:5]
model_names.append('ensemble mean')

fig,axes=plt.subplots(nrows=4,ncols=6,figsize=(10,10))
count=0
for period in ['ref','2030s','2050s','2070s']:
	for model in model_names:
		Z=expo_cmip5[period][model]
		Z[Z==0]=np.nan

		ax,im=plot_map(axes.flatten()[count],lons,lats,Z*100,color_type=plt.cm.YlOrBr,color_range=[0,20],color_label=None,subtitle='')
		if count<6:	ax.set_title(model,fontsize=9)
		if model==model_names[0]:ax.set_ylabel(period,size='large')
		count+=1
# ax=axes.flatten()[count]
# ax.axis('off')
# count+=1 
# for period in ['2015','2035','2055','2075']:
# 	Z=expo[period]['diff']['ensemble mean']
# 	Z[Z==0]=np.nan
# 	ax,im=plot_map(axes.flatten()[count],lons,lats,Z*100,color_type=plt.cm.YlOrBr,color_range=[0,20],color_label=None,subtitle='',grey_area=expo[period]['diff']['agreement'])
# 	if period=='ref':ax.set_ylabel('change',size='large')
# 	count+=1
cbar_ax=fig.add_axes([0,0.06,1,0.1])
cbar_ax.axis('off')
cb=fig.colorbar(im,orientation='horizontal',label='ratio of months affected by SPEI -2 [%]')
tick_locator = ticker.MaxNLocator(nbins=5)
cb.locator = tick_locator
cb.update_ticks()
plt.suptitle('SPEI 12m RCP8.5')
plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_spei_detail_rcp'+rcp+'.png')
plt.clf()


###########
# plot ensemble mean for different time slices
###########
# fig,axes=plt.subplots(nrows=1,ncols=5,figsize=(12,5.5))
# count=0
# for period in ['ref','2015','2035','2055','2075']:
# 	Z=expo[period]['ensemble mean']
# 	Z[Z==0]=np.nan
# 	ax,im=plot_map(axes.flatten()[count],lons,lats,Z*100,color_type=plt.cm.YlOrBr,color_range=[0,20],color_label=None,subtitle=period)
# 	count+=1
# cbar_ax=fig.add_axes([0,0.15,1,0.3])
# cbar_ax.axis('off')
# cb=fig.colorbar(im,orientation='horizontal',label='ratio of months affected by SPEI -2 [%]')
# tick_locator = ticker.MaxNLocator(nbins=5)
# cb.locator = tick_locator
# cb.update_ticks()
# plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_drought_whole_time.png')
# plt.clf()




############
# plot ref 2040s diff
############
# fig,axes=plt.subplots(nrows=1,ncols=3,figsize=(12,5.5))
# Z=expo['ref']['ensemble mean']
# Z[Z==0]=np.nan
# ax,im=plot_map(axes.flatten()[0],lons,lats,Z*100,color_type=plt.cm.YlOrBr,color_range=[0,20],color_label='ere',subtitle='ref')
# Z=expo['2040s']['ensemble mean']
# Z[Z==0]=np.nan
# ax,im=plot_map(axes.flatten()[1],lons,lats,Z*100,color_type=plt.cm.YlOrBr,color_range=[0,20],color_label='ertert',subtitle='2040s')
# Z=expo['2040s']['diff']['ensemble mean']
# Z[Z==0]=np.nan
# ax,im=plot_map(axes.flatten()[2],lons,lats,Z*100,color_type=plt.cm.seismic,color_range=[-20,20],color_label='rel',subtitle='2040s rel',grey_area=expo['2040s']['diff']['agreement'])
# # cbar_ax=fig.add_axes([0,0.15,0.66,0.3])
# # cbar_ax.axis('off')
# # cb=fig.colorbar(im,orientation='horizontal',label='ratio of months affected by SPEI -2')
# # tick_locator = ticker.MaxNLocator(nbins=5)
# # cb.locator = tick_locator
# # cb.update_ticks()
# #plt.suptitle('SPEI  NCEP ',size='large')
# plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_drought.png')
# plt.clf()



