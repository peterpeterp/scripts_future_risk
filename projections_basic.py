import sys 
import glob
import numpy as np
import dimarray as da 
from netCDF4 import Dataset,netcdftime,num2date
import pandas as pd

from mpl_toolkits.basemap import Basemap, cm
import mpl_toolkits.basemap
import matplotlib.pylab as plt
from matplotlib import ticker
from matplotlib.ticker import MaxNLocator

sys.path.append('/Users/peterpfleiderer/Documents/Scripts/allgemeine_scripte/')
from country_average import *
from plot_functions import *
sys.path.append('/Users/peterpfleiderer/Documents/Projects/WB_DRM/')



iso='GHA'
GHA={'tas':{'RCP2.6':{'models':{}},'RCP8.5':{'models':{}}}, 'pr':{'RCP2.6':{'models':{}},'RCP8.5':{'models':{}}},'support':{}}
GHA['support']['model_names']=[]
GHA['support']['periods']={'ref':1985,'2030s':2025,'2040s':2035}

for var in ['tas','pr']:
	all_files=glob.glob('Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/CMIP5/*/mon_'+var+'*.nc4')
	for file in all_files:
		print file
		rcp=file.split('/')[-2]
		model=file.split('_')[-4]
		if model not in GHA['support']['model_names']: GHA['support']['model_names'].append(model)
		nc_in=Dataset(file)

		if len(GHA['support'].keys())==2:
			GHA['support']['lon']=nc_in.variables['lon'][:]
			GHA['support']['lat']=nc_in.variables['lat'][:]
			# time handling
			time=nc_in.variables['time'][:]
			time_unit=nc_in.variables['time'].units
			datevar = []
			try:
				cal_temps = nc_in.variables['time'].calendar
				datevar.append(num2date(time,units = time_unit,calendar = cal_temps))
			except:
				datevar.append(num2date(time,units = time_unit))
			GHA['support']['year']=np.array([int(str(date).split("-")[0])\
							for date in datevar[0][:]])	

		GHA[var][rcp]['models'][model]=np.ma.masked_invalid(nc_in.variables[var][:,:,:])

	# ensemble mean
	for rcp in ['RCP2.6','RCP8.5']:
		GHA[var][rcp]['ensemble_mean']=GHA[var][rcp]['models'][GHA[var][rcp]['models'].keys()[0]].copy()*0
		for model in GHA['support']['model_names']:
			GHA[var][rcp]['ensemble_mean']+=GHA[var][rcp]['models'][model]
		GHA[var][rcp]['ensemble_mean']/=5

	# period mean
	for rcp in ['RCP2.6','RCP8.5']:
		GHA[var][rcp]['period_means']={}
		for period in GHA['support']['periods']:
			start_year=GHA['support']['periods'][period]
			relevant_time_indices=np.where((GHA['support']['year']>start_year) & (GHA['support']['year']<=start_year+20))[0]

			GHA[var][rcp]['period_means'][period]={'models':{}}
			GHA[var][rcp]['period_means'][period]['ensemble_mean']=np.mean(GHA[var][rcp]['ensemble_mean'][relevant_time_indices,:,:],axis=0)
			for model in GHA['support']['model_names']:
				GHA[var][rcp]['period_means'][period]['models'][model]=np.mean(GHA[var][rcp]['models'][model][relevant_time_indices,:,:],axis=0)

	# period diff
	for rcp in ['RCP2.6','RCP8.5']:
		GHA[var][rcp]['period_diff']={}
		for period in GHA['support']['periods']:
			if period!='ref':
				GHA[var][rcp]['period_diff'][period]={'models':{}}
				GHA[var][rcp]['period_diff'][period]['ensemble_mean']=GHA[var][rcp]['period_means'][period]['ensemble_mean']-GHA[var][rcp]['period_means']['ref']['ensemble_mean']
				for model in GHA['support']['model_names']:
					GHA[var][rcp]['period_diff'][period]['models'][model]=GHA[var][rcp]['period_means'][period]['models'][model]-GHA[var][rcp]['period_means']['ref']['models'][model]

	# period relative diff
	for rcp in ['RCP2.6','RCP8.5']:
		GHA[var][rcp]['period_rel_diff']={}
		for period in GHA['support']['periods']:
			if period!='ref':
				GHA[var][rcp]['period_rel_diff'][period]={'models':{}}
				GHA[var][rcp]['period_rel_diff'][period]['ensemble_mean']=(GHA[var][rcp]['period_means'][period]['ensemble_mean']-GHA[var][rcp]['period_means']['ref']['ensemble_mean'])/GHA[var][rcp]['period_means']['ref']['ensemble_mean']
				for model in GHA['support']['model_names']:
					GHA[var][rcp]['period_rel_diff'][period]['models'][model]=(GHA[var][rcp]['period_means'][period]['models'][model]-GHA[var][rcp]['period_means']['ref']['models'][model])/GHA[var][rcp]['period_means']['ref']['models'][model]

	# model agremment
	for rcp in ['RCP2.6','RCP8.5']:
		GHA[var][rcp]['agreement']={}
		for period in GHA['support']['periods']:
			if period!='ref':
				GHA[var][rcp]['agreement'][period]=GHA[var][rcp]['period_means'][period]['ensemble_mean'].copy()*0
				for model in GHA['support']['model_names']:
					GHA[var][rcp]['agreement'][period][np.where(np.sign(GHA[var][rcp]['period_diff'][period]['models'][model])==np.sign(GHA[var][rcp]['period_diff'][period]['ensemble_mean']))]+=1
				GHA[var][rcp]['agreement'][period][GHA[var][rcp]['agreement'][period]>3]=np.nan
				GHA[var][rcp]['agreement'][period][np.isnan(GHA[var][rcp]['agreement'][period])==False]=0.5
				GHA[var][rcp]['agreement'][period][np.ma.getmask(GHA[var][rcp]['period_means'][period]['ensemble_mean'])]=np.nan






###############
# plot results
###############
lon=GHA['support']['lon'].copy()
step=np.diff(lon,1)[0]
lon-=step/2
lon=np.append(lon,np.array(lon[-1]+step))

lat=GHA['support']['lat'].copy()
step=np.diff(lat,1)[0]
lat-=step/2
lat=np.append(lat,lat[-1]+step)

lons, lats = np.meshgrid(lon,lat)

rcp_names=['low warming','high warming']
rcp_str=['RCP2.6','RCP8.5']

# temperature ensemble mean overview
var='tas'
fig,axes=plt.subplots(nrows=2,ncols=2,figsize=(7,6))
count=0
for rcp in range(2):
	for period in ['2030s','2040s']:
		Z=GHA[var][rcp_str[rcp]]['period_diff'][period]['ensemble_mean']
		Z[Z==0]=np.nan
		print rcp,period,np.mean(np.ma.masked_invalid(Z)),np.min(np.ma.masked_invalid(Z)),np.max(np.ma.masked_invalid(Z))
		ax,im=plot_map(axes.flatten()[count],lons,lats,Z,color_type=plt.cm.YlOrBr,color_range=[0.75,2],color_label=None,subtitle='',grey_area=GHA[var][rcp_str[rcp]]['agreement'][period])
		if period=='2030s':	ax.set_ylabel(rcp_names[rcp])
		if rcp==0:	ax.set_title(period)
		count+=1

cbar_ax=fig.add_axes([0.8,0.1,0.1,0.8])
cbar_ax.axis('off')
cb=fig.colorbar(im,orientation='vertical',label='Temperature [K]')
tick_locator = ticker.MaxNLocator(nbins=5)
cb.locator = tick_locator
cb.update_ticks()
fig.tight_layout()
plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_'+var+'.png')


# precipitation ensemble mean overview
var='pr'
fig,axes=plt.subplots(nrows=2,ncols=2,figsize=(7,6))
count=0
for rcp in range(2):
	for period in ['2030s','2040s']:
		Z=GHA[var][rcp_str[rcp]]['period_rel_diff'][period]['ensemble_mean']*100
		Z[Z==0]=np.nan
		ax,im=plot_map(axes.flatten()[count],lons,lats,Z,color_type=plt.cm.RdYlBu,color_range=[-10,10],color_label=None,subtitle='',grey_area=GHA[var][rcp_str[rcp]]['agreement'][period])
		if period=='2030s':	ax.set_ylabel(rcp_names[rcp])
		if rcp==0:	ax.set_title(period)
		count+=1

cbar_ax=fig.add_axes([0.8,0.1,0.1,0.8])
cbar_ax.axis('off')
cb=fig.colorbar(im,orientation='vertical',label='Precipitation [%]')
tick_locator = ticker.MaxNLocator(nbins=5)
cb.locator = tick_locator
cb.update_ticks()
fig.tight_layout()
plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_'+var+'.png')

# precipitation ensemble mean overview absolute
var='pr'
fig,axes=plt.subplots(nrows=2,ncols=2,figsize=(7,6))
count=0
for rcp in range(2):
	for period in ['2030s','2040s']:
		Z=GHA[var][rcp_str[rcp]]['period_diff'][period]['ensemble_mean']*12
		Z[Z==0]=np.nan
		ax,im=plot_map(axes.flatten()[count],lons,lats,Z,color_type=plt.cm.RdYlBu,color_range=[-100,100],color_label=None,subtitle='',grey_area=GHA[var][rcp_str[rcp]]['agreement'][period])
		if period=='2030s':	ax.set_ylabel(rcp_names[rcp])
		if rcp==0:	ax.set_title(period)
		count+=1

cbar_ax=fig.add_axes([0.8,0.2,0.1,0.6])
cbar_ax.axis('off')
cb=fig.colorbar(im,orientation='vertical',label='Precipitation [mm]')
tick_locator = ticker.MaxNLocator(nbins=5)
cb.locator = tick_locator
cb.update_ticks()
fig.tight_layout()
plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_'+var+'_absolute.png')

# # temperature full overview 
# var='tas'
# rcp='RCP8.5'
# fig,axes=plt.subplots(nrows=4,ncols=5,figsize=(8,8))
# count=0
# for period in ['2030s','2040s']:
# 	for rcp in ['RCP2.6','RCP8.5']:
# 		for model in GHA['support']['model_names']:
# 			Z=GHA[var][rcp]['period_diff'][period]['models'][model]
# 			Z[Z==0]=np.nan
# 			ax,im=plot_map(axes.flatten()[count],lons,lats,Z,color_type=plt.cm.YlOrBr,color_range=[1,3],color_label=None,subtitle='')
# 			if period=='2030s' and rcp=='RCP2.6':		ax.set_title(model,fontsize=10)
# 			if model==GHA['support']['model_names'][0]: ax.set_ylabel(rcp+' '+period)
# 			count+=1

# cbar_ax=fig.add_axes([0,0.06,1,0.1])
# cbar_ax.axis('off')
# cb=fig.colorbar(im,orientation='horizontal',label='Temperature [K]')
# tick_locator = ticker.MaxNLocator(nbins=5)
# cb.locator = tick_locator
# cb.update_ticks()

# plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_'+var+'_detail.png')

# # precipitation full overview 
# var='pr'
# rcp='RCP8.5'
# fig,axes=plt.subplots(nrows=4,ncols=5,figsize=(8,8))
# count=0
# for period in ['2030s','2040s']:
# 	for rcp in ['RCP2.6','RCP8.5']:
# 		for model in GHA['support']['model_names']:
# 			Z=GHA[var][rcp]['period_rel_diff'][period]['models'][model]*100
# 			Z[Z==0]=np.nan
# 			ax,im=plot_map(axes.flatten()[count],lons,lats,Z,color_type=plt.cm.RdYlBu,color_range=[-20,20],color_label=None,subtitle='')
# 			if period=='2030s' and rcp=='RCP2.6':		ax.set_title(model,fontsize=10)
# 			if model==GHA['support']['model_names'][0]: ax.set_ylabel(rcp+' '+period)
# 			count+=1

# cbar_ax=fig.add_axes([0,0.06,1,0.1])
# cbar_ax.axis('off')
# cb=fig.colorbar(im,orientation='horizontal',label='Precipitation [%]')
# tick_locator = ticker.MaxNLocator(nbins=5)
# cb.locator = tick_locator
# cb.update_ticks()

# plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_'+var+'_detail.png')





