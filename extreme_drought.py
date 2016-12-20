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

iso='MWI'
rcp='8.5'

all_files=glob.glob('/Users/peterpfleiderer/Documents/Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/spei*'+rcp+'*')

expo={}
#expo['periods']={'ref':1985,'2015':2005,'2035':2025,'2055':2045,'2075':2065}
expo['periods']={'ref':1985,'2030s':2025,'2040s':2035}
for period in expo['periods'].keys():
	expo[period]={}

expo['model_names']=[]

for file in all_files:
	model=file.split('/')[-1].split('_')[1]
	expo['model_names'].append(model)

	nc_in=Dataset(file)

	spei=nc_in.variables['SPEI'][:]

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

	for period in expo['periods'].keys():
		start_year=expo['periods'][period]
		relevant_data_indices=np.where((years>start_year) & (years<=start_year+20))[0]
		tmp=spei[0,:,:].copy()

		for y in range(tmp.shape[0]):
			for x in range(tmp.shape[1]):
				tmp[y,x]=float(len(np.where(spei[relevant_data_indices,y,x].flatten()<=-2)[0]))/len(relevant_data_indices)

		expo[period][model]=tmp

for period in expo['periods'].keys():
	expo[period]['ensemble mean']=expo[period][expo['ref'].keys()[0]].copy()*0
	for model in expo['ref'].keys():
		expo[period]['ensemble mean']+=expo[period][model]
	expo[period]['ensemble mean']/=5

for period in expo['periods'].keys():
	if period !='ref':
		expo[period]['diff']={}
		for model in expo['ref'].keys():
			if model not in ['agreement','diff']:	
				expo[period]['diff'][model]=expo[period][model]-expo['ref'][model]


		expo[period]['diff']['agreement']=expo[period][expo['ref'].keys()[0]].copy()*0
		for model in expo['ref'].keys():
			if model not in ['ensemble mean','agreement','diff']:
				print period,model
				expo[period]['diff']['agreement'][np.where(np.sign(expo[period]['diff'][model])==np.sign(expo[period]['diff']['ensemble mean']))]+=1
		expo[period]['diff']['agreement'][expo[period]['diff']['agreement']>3]=np.nan
		expo[period]['diff']['agreement'][np.isnan(expo[period]['diff']['agreement'])==False]=0.5


###########
# plot explanatory
###########

fig,axes=plt.subplots(nrows=4,ncols=5,figsize=(7,6))
count=0
for period in ['ref','2040s']:
	for model in expo['model_names']:
		Z=expo[period][model]
		Z[Z==0]=np.nan
		if model==expo['model_names'][4]:color_label=''
		if model!=expo['model_names'][4]:color_label=None
		ax,im=plot_map(axes.flatten()[count],lons,lats,Z*100,color_type=plt.cm.YlOrBr,color_range=[0,20],color_label=color_label,subtitle='')
		if period=='ref':ax.set_title(model,size='small')
		if model==expo['model_names'][0]:ax.set_ylabel(period,size='large')
		count+=1
for model in expo['model_names']:
	Z=expo[period]['diff'][model]
	Z[Z==0]=np.nan
	if model==expo['model_names'][4]:color_label=''
	if model!=expo['model_names'][4]:color_label=None
	ax,im=plot_map(axes.flatten()[count],lons,lats,Z*100,color_type=plt.cm.seismic,color_range=[-10,10],color_label=color_label,subtitle='')
	if model==expo['model_names'][0]:ax.set_ylabel('difference',size='large')
	count+=1

ax=axes.flatten()[count]
ax.axis('off')
count+=1 

Z=expo[period]['diff']['ensemble mean']
Z[Z==0]=np.nan
ax,im=plot_map(axes.flatten()[count],lons,lats,Z*100,color_type=plt.cm.seismic,color_range=[-10,10],color_label=None,subtitle='')
ax.set_ylabel('ensemble mean',size='large')
count+=1

ax=axes.flatten()[count]
ax.axis('off')
count+=1 

Z=expo[period]['diff']['ensemble mean']
Z[Z==0]=np.nan
ax,im=plot_map(axes.flatten()[count],lons,lats,Z*100,color_type=plt.cm.seismic,color_range=[-10,10],color_label='',subtitle='',grey_area=expo[period]['diff']['agreement'])
count+=1

ax=axes.flatten()[count]
ax.axis('off')
count+=1 

# cbar_ax=fig.add_axes([0,0.15,1,0.3])
# cbar_ax.axis('off')
# cb=fig.colorbar(im,orientation='horizontal',label='ratio of months affected by SPEI -2 [%]')
# tick_locator = ticker.MaxNLocator(nbins=5)
# cb.locator = tick_locator
# cb.update_ticks()
fig.tight_layout()
plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_spei_model_rcp'+rcp+'.png')
plt.clf()




########
# huge plot overview
########
# fig,axes=plt.subplots(nrows=7,ncols=5,figsize=(10,14))
# count=0
# for model in model_names:
# 	for period in ['ref','2015','2035','2055','2075']:
# 		Z=expo[period][model]
# 		Z[Z==0]=np.nan
# 		if count<6:	subtitle=period
# 		else:		subtitle=''
# 		ax,im=plot_map(axes.flatten()[count],lons,lats,Z*100,color_type=plt.cm.YlOrBr,color_range=[0,20],color_label=None,subtitle=subtitle)
# 		if period=='ref':ax.set_ylabel(model,size='large')
# 		count+=1
# ax=axes.flatten()[count]
# ax.axis('off')
# count+=1 
# for period in ['2015','2035','2055','2075']:
# 	Z=expo[period]['diff']['ensemble mean']
# 	Z[Z==0]=np.nan
# 	ax,im=plot_map(axes.flatten()[count],lons,lats,Z*100,color_type=plt.cm.YlOrBr,color_range=[0,20],color_label=None,subtitle='',grey_area=expo[period]['diff']['agreement'])
# 	if period=='ref':ax.set_ylabel('change',size='large')
# 	count+=1
# cbar_ax=fig.add_axes([0,0.06,1,0.1])
# cbar_ax.axis('off')
# cb=fig.colorbar(im,orientation='horizontal',label='ratio of months affected by SPEI -2 [%]')
# tick_locator = ticker.MaxNLocator(nbins=5)
# cb.locator = tick_locator
# cb.update_ticks()
# plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_drought_detail_rcp'+rcp+'.png')
# plt.clf()


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



