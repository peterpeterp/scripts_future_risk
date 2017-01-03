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
var='rx5'
GHA_rx5=prepare_country_dict(var=var,files=glob.glob('Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/CMIP5/*/mon_rx5*'+iso+'.nc4'))
GHA_rx5['support']['periods']={'ref':1985,'2030s':2024,'2040s':2034}

###############
# plot settings
###############
lon=GHA_rx5['support']['lon'].copy()
lat=GHA_rx5['support']['lat'].copy()

rcp_names=['low warming','high warming']
rcp_str=['rcp2p6','rcp8p5']

risk = make_colormap([col_conv('green'), col_conv('white'), 0.2, col_conv('white'), col_conv('yellow'), 0.4, col_conv('yellow'), col_conv('orange'), 0.6, col_conv('orange'), col_conv('red'), 0.8, col_conv('red'), col_conv('violet')])
month_color = mpl.colors.ListedColormap(sns.color_palette("cubehelix", 12))

#####################
# extreme wet events
#####################

# identify wet season
GHA_rx5['wet_season']={}
GHA_rx5['climatology']={}
for model in GHA_rx5['support']['model_names']:
	GHA_rx5['climatology'][model]=GHA_rx5['rcp2p6']['models'][model][0:12,:,:].copy()*0
	start_year=GHA_rx5['support']['periods']['ref']
	for month in range(12):
		relevant_time_indices=np.where((GHA_rx5['support']['year']>start_year) & (GHA_rx5['support']['year']<=start_year+20) & (GHA_rx5['support']['month']==month+1))[0]
		for y in range(GHA_rx5['climatology'][model].shape[1]):
			for x in range(GHA_rx5['climatology'][model].shape[2]):
				GHA_rx5['climatology'][model][month,y,x]=np.mean(GHA_rx5['rcp2p6']['models'][model][relevant_time_indices,y,x])

	GHA_rx5['wet_season'][model]=np.argsort(GHA_rx5['climatology'][model],axis=0,).astype(float)[-3:,:,:][::-1,:,:]+1
	GHA_rx5['wet_season'][model][np.isfinite(GHA_rx5['climatology'][model][0:3,:,:])==False]=np.nan
	GHA_rx5['wet_season'][model]=np.ma.masked_invalid(GHA_rx5['wet_season'][model])

# plot wet season
if True:
	fig,axes=plt.subplots(nrows=3,ncols=5,figsize=(8,6))
	count=0
	for mon in range(3):
		for model in GHA_rx5['support']['model_names']:
			Z=GHA_rx5['wet_season'][model][mon,:,:].copy()
			Z[Z==0]=np.nan
			ax,im=plot_map(axes.flatten()[count],lon,lat,Z,color_type=month_color,color_range=[1,12],color_label=None,subtitle='')
			ax.set_title(model)
			count+=1

	cbar_ax=fig.add_axes([0.1,0.1,0.8,0.2])
	cbar_ax.axis('off')
	cb=fig.colorbar(im,orientation='horizontal',label='ratio of months affected by heat extremes [%]')
	tick_locator = ticker.MaxNLocator(nbins=5)
	cb.locator = tick_locator
	cb.update_ticks()
	plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_'+var+'_season'+tag+'.png')
	plt.clf()

# define threshold
GHA_rx5['threshold']={}
for model in GHA_rx5['support']['model_names']:
	GHA_rx5['threshold'][model]=GHA_rx5['rcp2p6']['models'][model][0,:,:].copy()*np.nan
	start_year=GHA_rx5['support']['periods']['ref']
	for y in range(GHA_rx5['climatology'][model].shape[1]):
		for x in range(GHA_rx5['climatology'][model].shape[2]):
			if np.isfinite(GHA_rx5['wet_season'][model][0,y,x]):
				relevant_time_indices=np.where((GHA_rx5['support']['year']>start_year) & (GHA_rx5['support']['year']<=start_year+20) \
					& ((GHA_rx5['support']['month'] == GHA_rx5['wet_season'][model][0,y,x]) | (GHA_rx5['support']['month'] == GHA_rx5['wet_season'][model][1,y,x]) | (GHA_rx5['support']['month'] == GHA_rx5['wet_season'][model][2,y,x])) \
					& (np.isfinite(GHA_rx5['rcp2p6']['models'][model][:,y,x])))[0]
				if len(relevant_time_indices)>1:
					relevant_values=np.ma.getdata(GHA_rx5['rcp2p6']['models'][model][relevant_time_indices,y,x])
					GHA_rx5['threshold'][model][y,x]=np.mean(relevant_values) + 2 * np.std(relevant_values)

# plot treshold
if True:
	fig,axes=plt.subplots(nrows=1,ncols=5,figsize=(8,3))
	count=0
	for model in GHA_rx5['support']['model_names']:
		Z=GHA_rx5['threshold'][model].copy()
		Z[Z==0]=np.nan
		ax,im=plot_map(axes.flatten()[count],lon,lat,Z,color_type=plt.cm.YlOrBr,color_range=[80,150],color_label=None,subtitle='')
		ax.set_title(model)
		count+=1

	cbar_ax=fig.add_axes([0.1,0.1,0.8,0.2])
	cbar_ax.axis('off')
	cb=fig.colorbar(im,orientation='horizontal',label='ratio of months affected by heat extremes [%]')
	tick_locator = ticker.MaxNLocator(nbins=5)
	cb.locator = tick_locator
	cb.update_ticks()
	plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_'+var+'_thresh'+tag+'.png')
	plt.clf()


# get exposure
GHA_rx5['exposure']={'rcp2p6':{'models':{}},'rcp8p5':{'models':{}}}
for rcp in ['rcp2p6','rcp8p5']:
	for model in GHA_rx5['support']['model_names']:
		GHA_rx5['exposure'][rcp]['models'][model]={}
		for period in GHA_rx5['support']['periods']:
			start_year=GHA_rx5['support']['periods'][period]
			tmp=GHA_rx5[rcp]['models'][model][0,:,:].copy()*np.nan
			for y in range(tmp.shape[0]):
				for x in range(tmp.shape[1]):
					if np.isfinite(GHA_rx5['wet_season'][model][0,y,x]):
						relevant_time_indices=np.where((GHA_rx5['support']['year']>start_year) & (GHA_rx5['support']['year']<=start_year+20) \
							& ((GHA_rx5['support']['month'] == GHA_rx5['wet_season'][model][0,y,x]) | (GHA_rx5['support']['month'] == GHA_rx5['wet_season'][model][1,y,x]) | (GHA_rx5['support']['month'] == GHA_rx5['wet_season'][model][2,y,x])) \
							& (np.isfinite(GHA_rx5[rcp]['models'][model][:,y,x])))[0]
					if len(relevant_time_indices)>1:
						tmp[y,x]=float(len(np.where(GHA_rx5[rcp]['models'][model][relevant_time_indices,y,x].flatten()>GHA_rx5['threshold'][model][y,x])[0]))/len(relevant_time_indices)
			GHA_rx5['exposure'][rcp]['models'][model][period]=tmp

# plot exposure
if True:
	for rcp in ['rcp2p6','rcp8p5']:
		fig,axes=plt.subplots(nrows=3,ncols=6,figsize=(10,6))
		count=0
		for period in ['ref','2030s','2040s']:
			for model in GHA_rx5['support']['model_names']:
				Z=GHA_rx5['exposure'][rcp]['models'][model][period].copy()
				Z[Z==0]=np.nan
				ax,im=plot_map(axes.flatten()[count],lon,lat,Z*100,color_type=plt.cm.YlOrBr,color_range=[0,20],color_label=None,subtitle='')
				if period=='ref':							ax.set_title(model)
				if model==GHA_rx5['support']['model_names'][0]:	ax.set_ylabel(period)
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
		plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_'+var+'_exposure_'+rcp+tag+'.png')
		plt.clf()

#exposure diff
GHA_rx5['exposure_diff']={'rcp2p6':{'models':{}},'rcp8p5':{'models':{}}}	
for rcp in ['rcp2p6','rcp8p5']:
	GHA_rx5[rcp]['period_diff']={}
	for model in GHA_rx5['support']['model_names']:
		GHA_rx5['exposure_diff'][rcp]['models'][model]={}
		for period in GHA_rx5['support']['periods']:
			if period!='ref':
				GHA_rx5['exposure_diff'][rcp]['models'][model][period]=GHA_rx5['exposure'][rcp]['models'][model][period]-GHA_rx5['exposure'][rcp]['models'][model]['ref']

# plot exposure diff
if True:
	for rcp in ['rcp2p6','rcp8p5']:
		fig,axes=plt.subplots(nrows=2,ncols=6,figsize=(10,4))
		count=0
		for period in ['2030s','2040s']:
			for model in GHA_rx5['support']['model_names']:
				Z=GHA_rx5['exposure_diff'][rcp]['models'][model][period].copy()
				Z[Z==0]=np.nan
				ax,im=plot_map(axes.flatten()[count],lon,lat,Z*100,color_type=plt.cm.PiYG,color_range=[-10,10],color_label=None,subtitle='')
				if period=='2030s':							ax.set_title(model)
				if model==GHA_rx5['support']['model_names'][0]:	ax.set_ylabel(period)
				count+=1

			ax=axes.flatten()[count]
			ax.axis('off')
			count+=1 

		cbar_ax=fig.add_axes([0.8,0.2,0.1,0.6])
		cbar_ax.axis('off')
		cb=fig.colorbar(im,orientation='vertical',label='change in ratio of months affected by heat extremes [%]')
		tick_locator = ticker.MaxNLocator(nbins=5)
		cb.locator = tick_locator
		cb.update_ticks()
		plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_'+var+'_exposure_diff_'+rcp+tag+'.png')
		plt.clf()	

# ensemble mean
for rcp in ['rcp2p6','rcp8p5']:
	GHA_rx5['exposure_diff'][rcp]['ensemble_mean']={}
	for period in GHA_rx5['support']['periods']:
		if period!='ref':
			GHA_rx5['exposure_diff'][rcp]['ensemble_mean'][period]=GHA_rx5['exposure_diff'][rcp]['models'][GHA_rx5['support']['model_names'][0]][period].copy()*0
			for model in GHA_rx5['support']['model_names']:
				GHA_rx5['exposure_diff'][rcp]['ensemble_mean'][period]+=GHA_rx5['exposure_diff'][rcp]['models'][model][period]
			GHA_rx5['exposure_diff'][rcp]['ensemble_mean'][period]/=5

# agreement
for rcp in ['rcp2p6','rcp8p5']:
	GHA_rx5['exposure_diff'][rcp]['agreement']={}
	for period in GHA_rx5['support']['periods']:
		if period!='ref':
			GHA_rx5['exposure_diff'][rcp]['agreement'][period]=GHA_rx5['exposure_diff'][rcp]['models'][GHA_rx5['support']['model_names'][0]][period].copy()*0
			for model in GHA_rx5['support']['model_names']:
				GHA_rx5['exposure_diff'][rcp]['agreement'][period][np.where(np.sign(GHA_rx5['exposure_diff'][rcp]['models'][model][period])==np.sign(GHA_rx5['exposure_diff'][rcp]['ensemble_mean'][period]))]+=1
			GHA_rx5['exposure_diff'][rcp]['agreement'][period][GHA_rx5['exposure_diff'][rcp]['agreement'][period]>3]=np.nan
			GHA_rx5['exposure_diff'][rcp]['agreement'][period][np.isnan(GHA_rx5['exposure_diff'][rcp]['agreement'][period])==False]=0.5
			GHA_rx5['exposure_diff'][rcp]['agreement'][period][np.where(np.isfinite(GHA_rx5['exposure_diff'][rcp]['ensemble_mean'][period][:,:])==False)[0]]=np.nan


# plot extreme wet events
if True:
	fig,axes=plt.subplots(nrows=2,ncols=2,figsize=(7,6))
	count=0
	for rcp in range(2):
		for period in ['2030s','2040s']:
			Z=GHA_rx5['exposure_diff'][rcp_str[rcp]]['ensemble_mean'][period].copy()*100
			Z[Z==0]=np.nan
			print rcp_str[rcp],period,np.mean(np.ma.masked_invalid(Z)),np.min(np.ma.masked_invalid(Z)),np.max(np.ma.masked_invalid(Z))
			ax,im=plot_map(axes.flatten()[count],lon,lat,Z,color_type=risk,color_range=[-2.5,10],color_label=None,subtitle='',grey_area=GHA_rx5['exposure_diff'][rcp_str[rcp]]['agreement'][period])
			if period=='2030s':	ax.set_ylabel(rcp_names[rcp])
			if rcp==0:	ax.set_title(period)
			count+=1

	cbar_ax=fig.add_axes([0.8,0.1,0.1,0.8])
	cbar_ax.axis('off')
	cb=fig.colorbar(im,orientation='vertical',label='change in frequency of extreme wet events \n [percentage of affected months]')
	tick_locator = ticker.MaxNLocator(nbins=5)
	cb.locator = tick_locator
	cb.update_ticks()
	fig.tight_layout()
	plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_'+var+'_exposure_diff'+tag+'.png')


# plot increase



