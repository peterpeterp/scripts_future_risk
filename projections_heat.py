import sys,glob
import numpy as np
import dimarray as da 
from netCDF4 import Dataset,netcdftime,num2date
import pandas as pd


from mpl_toolkits.basemap import Basemap, cm
import mpl_toolkits.basemap
import matplotlib.pylab as plt
import matplotlib as mpl
from matplotlib import ticker
from matplotlib.ticker import MaxNLocator
import seaborn as sns
from matplotlib.colors import ListedColormap


sys.path.append('/Users/peterpfleiderer/Documents/Scripts/allgemeine_scripte/')
from country_average import *
from plot_functions import *
from prepare_country_data import *
sys.path.append('/Users/peterpfleiderer/Documents/Projects/WB_DRM/')

iso='GHA'
var='tas'
GHA_heat=prepare_country_dict(var=var,files=glob.glob('Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/CMIP5/*/mon_tas*.nc4'))
GHA_heat['support']['periods']={'ref':1985,'2030s':2024,'2040s':2034}

###############
# plot settings
###############
lon=GHA_heat['support']['lon'].copy()
lat=GHA_heat['support']['lat'].copy()

rcp_names=['low warming','high warming']
rcp_str=['rcp2p6','rcp8p5']

risk = make_colormap([col_conv('green'), col_conv('white'), 0.2, col_conv('white'), col_conv('yellow'), 0.4, col_conv('yellow'), col_conv('orange'), 0.6, col_conv('orange'), col_conv('red'), 0.8, col_conv('red'), col_conv('violet')])
month_color = mpl.colors.ListedColormap(sns.color_palette("cubehelix", 12))

#####################
# extreme hot events
#####################

# identify warm season
GHA_heat['warm_season']={}
GHA_heat['climatology']={}
for model in GHA_heat['support']['model_names']:
	GHA_heat['climatology'][model]=GHA_heat['rcp2p6']['models'][model][0:12,:,:].copy()*0
	start_year=GHA_heat['support']['periods']['ref']
	for month in range(12):
		relevant_time_indices=np.where((GHA_heat['support']['year']>start_year) & (GHA_heat['support']['year']<=start_year+20) & (GHA_heat['support']['month']==month+1))[0]
		for y in range(GHA_heat['climatology'][model].shape[1]):
			for x in range(GHA_heat['climatology'][model].shape[2]):
				GHA_heat['climatology'][model][month,y,x]=np.mean(GHA_heat['rcp2p6']['models'][model][relevant_time_indices,y,x])

	GHA_heat['warm_season'][model]=np.argsort(GHA_heat['climatology'][model],axis=0,).astype(float)[-3:,:,:][::-1,:,:]+1
	GHA_heat['warm_season'][model][np.isfinite(GHA_heat['climatology'][model][0:3,:,:])==False]=np.nan
	GHA_heat['warm_season'][model]=np.ma.masked_invalid(GHA_heat['warm_season'][model])

# plot warm season
if True:
	fig,axes=plt.subplots(nrows=3,ncols=5,figsize=(8,6))
	count=0
	for mon in range(3):
		for model in GHA_heat['support']['model_names']:
			Z=GHA_heat['warm_season'][model][mon,:,:].copy()
			Z[Z==0]=np.nan
			ax,im=plot_map(axes.flatten()[count],lon,lat,Z,color_type=plt.cm.YlOrBr,color_range=[1,5],color_label=None,subtitle='')
			ax.set_title(model)
			count+=1

	cbar_ax=fig.add_axes([0.1,0.1,0.8,0.2])
	cbar_ax.axis('off')
	cb=fig.colorbar(im,orientation='horizontal',label='ratio of months affected by heat extremes [%]')
	tick_locator = ticker.MaxNLocator(nbins=5)
	cb.locator = tick_locator
	cb.update_ticks()
	plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_tas_warm_season.png')
	plt.clf()

# define threshold
GHA_heat['threshold']={}
for model in GHA_heat['support']['model_names']:
	GHA_heat['threshold'][model]=GHA_heat['rcp2p6']['models'][model][0,:,:].copy()*np.nan
	for y in range(GHA_heat['climatology'][model].shape[1]):
		for x in range(GHA_heat['climatology'][model].shape[2]):
			if np.isfinite(GHA_heat['warm_season'][model][0,y,x]):
				relevant_time_indices=np.where((GHA_heat['support']['year']>start_year) & (GHA_heat['support']['year']<=start_year+20) \
							& ((GHA_heat['support']['month'] == GHA_heat['warm_season'][model][0,y,x]) | (GHA_heat['support']['month'] == GHA_heat['warm_season'][model][1,y,x]) | (GHA_heat['support']['month'] == GHA_heat['warm_season'][model][2,y,x])) \
							& (np.isfinite(GHA_heat['rcp2p6']['models'][model][:,y,x])))[0]
				relevant_values=np.ma.getdata(GHA_heat['rcp2p6']['models'][model][relevant_time_indices,y,x])
				GHA_heat['threshold'][model][y,x]=np.mean(relevant_values) + 2 * np.std(relevant_values)

# plot treshold
if True:
	fig,axes=plt.subplots(nrows=1,ncols=5,figsize=(8,3))
	count=0
	for model in GHA_heat['support']['model_names']:
		Z=GHA_heat['threshold'][model].copy()-273.15
		Z[Z==0]=np.nan
		ax,im=plot_map(axes.flatten()[count],lon,lat,Z,color_type=plt.cm.YlOrBr,color_range=[29,35],color_label=None,subtitle='')
		ax.set_title(model)
		count+=1

	cbar_ax=fig.add_axes([0.1,0.1,0.8,0.2])
	cbar_ax.axis('off')
	cb=fig.colorbar(im,orientation='horizontal',label='ratio of months affected by heat extremes [%]')
	tick_locator = ticker.MaxNLocator(nbins=5)
	cb.locator = tick_locator
	cb.update_ticks()
	plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_tas_thresh.png')
	plt.clf()

# get exposure
GHA_heat['exposure']={'rcp2p6':{'models':{}},'rcp8p5':{'models':{}}}
for rcp in ['rcp2p6','rcp8p5']:
	for model in GHA_heat['support']['model_names']:
		GHA_heat['exposure'][rcp]['models'][model]={}
		for period in GHA_heat['support']['periods']:
			start_year=GHA_heat['support']['periods'][period]
			tmp=GHA_heat[rcp]['models'][model][0,:,:].copy()*np.nan
			for y in range(tmp.shape[0]):
				for x in range(tmp.shape[1]):
					if np.isfinite(GHA_heat['warm_season'][model][0,y,x]):
						relevant_time_indices=np.where((GHA_heat['support']['year']>start_year) & (GHA_heat['support']['year']<=start_year+20) \
							& ((GHA_heat['support']['month'] == GHA_heat['warm_season'][model][0,y,x]) | (GHA_heat['support']['month'] == GHA_heat['warm_season'][model][1,y,x]) | (GHA_heat['support']['month'] == GHA_heat['warm_season'][model][2,y,x])) \
							& (np.isfinite(GHA_heat[rcp]['models'][model][:,y,x])))[0]
						tmp[y,x]=float(len(np.where(GHA_heat[rcp]['models'][model][relevant_time_indices,y,x].flatten()>GHA_heat['threshold'][model][y,x])[0]))/len(relevant_time_indices)
			GHA_heat['exposure'][rcp]['models'][model][period]=tmp

# plot exposure
if True:
	for rcp in ['rcp2p6','rcp8p5']:
		fig,axes=plt.subplots(nrows=3,ncols=6,figsize=(10,6))
		count=0
		for period in ['ref','2030s','2040s']:
			for model in GHA_heat['support']['model_names']:
				Z=GHA_heat['exposure'][rcp]['models'][model][period].copy()
				Z[Z==0]=np.nan
				ax,im=plot_map(axes.flatten()[count],lon,lat,Z*100,color_type=plt.cm.YlOrBr,color_range=[0,50],color_label=None,subtitle='')
				if period=='2030s':							ax.set_title(model)
				if model==GHA_heat['support']['model_names'][0]:	ax.set_ylabel(period)
				count+=1

			ax=axes.flatten()[count]
			ax.axis('off')
			count+=1 

		cbar_ax=fig.add_axes([0.8,0.2,0.1,0.6])
		cbar_ax.axis('off')
		cb=fig.colorbar(im,orientation='vertical',label='ratio of months affected by heat extremes [%]')
		tick_locator = ticker.MaxNLocator(nbins=5)
		cb.locator = tick_locator
		cb.update_ticks()
		plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_tas_exposure_'+rcp+'.png')
		plt.clf()

#exposure diff
GHA_heat['exposure_diff']={'rcp2p6':{'models':{}},'rcp8p5':{'models':{}}}	
for rcp in ['rcp2p6','rcp8p5']:
	GHA_heat[rcp]['period_diff']={}
	for model in GHA_heat['support']['model_names']:
		GHA_heat['exposure_diff'][rcp]['models'][model]={}
		for period in GHA_heat['support']['periods']:
			if period!='ref':
				GHA_heat['exposure_diff'][rcp]['models'][model][period]=GHA_heat['exposure'][rcp]['models'][model][period]-GHA_heat['exposure'][rcp]['models'][model]['ref']

# ensemble mean
for rcp in ['rcp2p6','rcp8p5']:
	GHA_heat['exposure_diff'][rcp]['ensemble_mean']={}
	for period in GHA_heat['support']['periods']:
		if period!='ref':
			GHA_heat['exposure_diff'][rcp]['ensemble_mean'][period]=GHA_heat['exposure_diff'][rcp]['models'][GHA_heat['support']['model_names'][0]][period].copy()*0
			for model in GHA_heat['support']['model_names']:
				GHA_heat['exposure_diff'][rcp]['ensemble_mean'][period]+=GHA_heat['exposure_diff'][rcp]['models'][model][period]
			GHA_heat['exposure_diff'][rcp]['ensemble_mean'][period]/=5

# agreement
for rcp in ['rcp2p6','rcp8p5']:
	GHA_heat['exposure_diff'][rcp]['agreement']={}
	for period in GHA_heat['support']['periods']:
		if period!='ref':
			GHA_heat['exposure_diff'][rcp]['agreement'][period]=GHA_heat['exposure_diff'][rcp]['models'][GHA_heat['support']['model_names'][0]][period].copy()*0
			for model in GHA_heat['support']['model_names']:
				GHA_heat['exposure_diff'][rcp]['agreement'][period][np.where(np.sign(GHA_heat['exposure_diff'][rcp]['models'][model][period])==np.sign(GHA_heat['exposure_diff'][rcp]['ensemble_mean'][period]))]+=1
			GHA_heat['exposure_diff'][rcp]['agreement'][period][GHA_heat['exposure_diff'][rcp]['agreement'][period]>3]=np.nan
			GHA_heat['exposure_diff'][rcp]['agreement'][period][np.isnan(GHA_heat['exposure_diff'][rcp]['agreement'][period])==False]=0.5
			GHA_heat['exposure_diff'][rcp]['agreement'][period][np.where(np.isfinite(GHA_heat['exposure_diff'][rcp]['ensemble_mean'][period][:,:])==False)[0]]=np.nan

# extreme hot events
if True:
	fig,axes=plt.subplots(nrows=2,ncols=2,figsize=(7,6))
	count=0
	for rcp in range(2):
		for period in ['2030s','2040s']:
			Z=GHA_heat['exposure_diff'][rcp_str[rcp]]['ensemble_mean'][period].copy()*100
			Z[Z==0]=np.nan
			print rcp_str[rcp],period,np.mean(np.ma.masked_invalid(Z)),np.min(np.ma.masked_invalid(Z)),np.max(np.ma.masked_invalid(Z))
			ax,im=plot_map(axes.flatten()[count],lon,lat,Z,color_type=risk,color_range=[-20,80],color_label=None,subtitle='',grey_area=GHA_heat['exposure_diff'][rcp_str[rcp]]['agreement'][period])
			if period=='2030s':	ax.set_ylabel(rcp_names[rcp])
			if rcp==0:	ax.set_title(period)
			count+=1

	cbar_ax=fig.add_axes([0.8,0.1,0.1,0.8])
	cbar_ax.axis('off')
	cb=fig.colorbar(im,orientation='vertical',label='change in frequency of extreme dry events \n [percentage of affected months]')
	tick_locator = ticker.MaxNLocator(nbins=5)
	cb.locator = tick_locator
	cb.update_ticks()
	fig.tight_layout()
	plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_tas_exposure_diff.png')

