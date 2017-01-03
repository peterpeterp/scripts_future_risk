import sys 
import glob
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
sys.path.append('/Users/peterpfleiderer/Documents/Projects/WB_DRM/')



iso='GHA'
GHA={'rx5':{'rcp2p6':{'models':{}},'rcp8p5':{'models':{}}},'support':{}}

GHA['support']['model_names']=[]
GHA['support']['periods']={'ref':1985,'2030s':2024,'2040s':2034}

GHA['support']['files']={}

# tag='_month_cut'
# GHA['support']['files']['rx5']=glob.glob('Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/CMIP5/*/mon_rx5*_month_cut.nc4')

tag=''
GHA['support']['files']['rx5']=glob.glob('Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/CMIP5/*/mon_rx5*'+iso+'.nc4')


for var in ['rx5']:
	for file in GHA['support']['files'][var]:
		# interprete files
		print file
		for i in range(-6,-2):
			if file.split('_')[i][0:3]=='rcp':
				rcp=file.split('_')[i]
				model=file.split('_')[i-1]
				break


		if model not in GHA['support']['model_names']: GHA['support']['model_names'].append(model)
		nc_in=Dataset(file)

		if len(GHA['support'].keys())==3:
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
			GHA['support']['month']=np.array([int(str(date).split("-")[1])\
							for date in datevar[0][:]])	

		GHA[var][rcp]['models'][model]=np.ma.masked_invalid(nc_in.variables[var][:,:,:])

	# ensemble mean
	for rcp in ['rcp2p6','rcp8p5']:
		GHA[var][rcp]['ensemble_mean']=GHA[var][rcp]['models'][GHA[var][rcp]['models'].keys()[0]].copy()*0
		for model in GHA['support']['model_names']:
			GHA[var][rcp]['ensemble_mean']+=GHA[var][rcp]['models'][model]
		GHA[var][rcp]['ensemble_mean']/=5

###############
# plot settings
###############
lon=GHA['support']['lon'].copy()
lat=GHA['support']['lat'].copy()

rcp_names=['low warming','high warming']
rcp_str=['rcp2p6','rcp8p5']

risk = make_colormap([col_conv('green'), col_conv('white'), 0.2, col_conv('white'), col_conv('yellow'), 0.4, col_conv('yellow'), col_conv('orange'), 0.6, col_conv('orange'), col_conv('red'), 0.8, col_conv('red'), col_conv('violet')])
month_color = mpl.colors.ListedColormap(sns.color_palette("cubehelix", 12))

#####################
# extreme wet events
#####################
var='rx5'

# identify wet season
GHA[var]['wet_season']={}
GHA[var]['climatology']={}
for model in GHA['support']['model_names']:
	GHA[var]['climatology'][model]=GHA[var]['rcp2p6']['models'][model][0:12,:,:].copy()*0
	start_year=GHA['support']['periods']['ref']
	for month in range(12):
		relevant_time_indices=np.where((GHA['support']['year']>start_year) & (GHA['support']['year']<=start_year+20) & (GHA['support']['month']==month+1))[0]
		for y in range(GHA[var]['climatology'][model].shape[1]):
			for x in range(GHA[var]['climatology'][model].shape[2]):
				GHA[var]['climatology'][model][month,y,x]=np.mean(GHA[var]['rcp2p6']['models'][model][relevant_time_indices,y,x])

	GHA[var]['wet_season'][model]=np.argsort(GHA[var]['climatology'][model],axis=0,).astype(float)[-3:,:,:][::-1,:,:]+1
	GHA[var]['wet_season'][model][np.isfinite(GHA[var]['climatology'][model][0:3,:,:])==False]=np.nan
	GHA[var]['wet_season'][model]=np.ma.masked_invalid(GHA[var]['wet_season'][model])

# plot wet season
if True:
	fig,axes=plt.subplots(nrows=3,ncols=5,figsize=(8,6))
	count=0
	for mon in range(3):
		for model in GHA['support']['model_names']:
			Z=GHA[var]['wet_season'][model][mon,:,:].copy()
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
GHA[var]['threshold']={}
for model in GHA['support']['model_names']:
	GHA[var]['threshold'][model]=GHA[var]['rcp2p6']['models'][model][0,:,:].copy()*np.nan
	start_year=GHA['support']['periods']['ref']
	for y in range(GHA[var]['climatology'][model].shape[1]):
		for x in range(GHA[var]['climatology'][model].shape[2]):
			if np.isfinite(GHA[var]['wet_season'][model][0,y,x]):
				relevant_time_indices=np.where((GHA['support']['year']>start_year) & (GHA['support']['year']<=start_year+20) \
					& ((GHA['support']['month'] == GHA[var]['wet_season'][model][0,y,x]) | (GHA['support']['month'] == GHA[var]['wet_season'][model][1,y,x]) | (GHA['support']['month'] == GHA[var]['wet_season'][model][2,y,x])) \
					& (np.isfinite(GHA[var]['rcp2p6']['models'][model][:,y,x])))[0]
				if len(relevant_time_indices)>1:
					relevant_values=np.ma.getdata(GHA[var]['rcp2p6']['models'][model][relevant_time_indices,y,x])
					GHA[var]['threshold'][model][y,x]=np.mean(relevant_values) + 2 * np.std(relevant_values)

# plot treshold
if True:
	fig,axes=plt.subplots(nrows=1,ncols=5,figsize=(8,3))
	count=0
	for model in GHA['support']['model_names']:
		Z=GHA[var]['threshold'][model].copy()
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
GHA[var]['exposure']={'rcp2p6':{'models':{}},'rcp8p5':{'models':{}}}
for rcp in ['rcp2p6','rcp8p5']:
	for model in GHA['support']['model_names']:
		GHA[var]['exposure'][rcp]['models'][model]={}
		for period in GHA['support']['periods']:
			start_year=GHA['support']['periods'][period]
			tmp=GHA[var][rcp]['models'][model][0,:,:].copy()*np.nan
			for y in range(tmp.shape[0]):
				for x in range(tmp.shape[1]):
					if np.isfinite(GHA[var]['wet_season'][model][0,y,x]):
						relevant_time_indices=np.where((GHA['support']['year']>start_year) & (GHA['support']['year']<=start_year+20) \
							& ((GHA['support']['month'] == GHA[var]['wet_season'][model][0,y,x]) | (GHA['support']['month'] == GHA[var]['wet_season'][model][1,y,x]) | (GHA['support']['month'] == GHA[var]['wet_season'][model][2,y,x])) \
							& (np.isfinite(GHA[var][rcp]['models'][model][:,y,x])))[0]
					if len(relevant_time_indices)>1:
						tmp[y,x]=float(len(np.where(GHA[var][rcp]['models'][model][relevant_time_indices,y,x].flatten()>GHA[var]['threshold'][model][y,x])[0]))/len(relevant_time_indices)
			GHA[var]['exposure'][rcp]['models'][model][period]=tmp

# plot exposure
if True:
	for rcp in ['rcp2p6','rcp8p5']:
		fig,axes=plt.subplots(nrows=3,ncols=6,figsize=(10,6))
		count=0
		for period in ['ref','2030s','2040s']:
			for model in GHA['support']['model_names']:
				Z=GHA[var]['exposure'][rcp]['models'][model][period].copy()
				Z[Z==0]=np.nan
				ax,im=plot_map(axes.flatten()[count],lon,lat,Z*100,color_type=plt.cm.YlOrBr,color_range=[0,20],color_label=None,subtitle='')
				if period=='ref':							ax.set_title(model)
				if model==GHA['support']['model_names'][0]:	ax.set_ylabel(period)
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
GHA[var]['exposure_diff']={'rcp2p6':{'models':{}},'rcp8p5':{'models':{}}}	
for rcp in ['rcp2p6','rcp8p5']:
	GHA[var][rcp]['period_diff']={}
	for model in GHA['support']['model_names']:
		GHA[var]['exposure_diff'][rcp]['models'][model]={}
		for period in GHA['support']['periods']:
			if period!='ref':
				GHA[var]['exposure_diff'][rcp]['models'][model][period]=GHA[var]['exposure'][rcp]['models'][model][period]-GHA[var]['exposure'][rcp]['models'][model]['ref']

# plot exposure diff
if True:
	for rcp in ['rcp2p6','rcp8p5']:
		fig,axes=plt.subplots(nrows=2,ncols=6,figsize=(10,4))
		count=0
		for period in ['2030s','2040s']:
			for model in GHA['support']['model_names']:
				Z=GHA[var]['exposure_diff'][rcp]['models'][model][period].copy()
				Z[Z==0]=np.nan
				ax,im=plot_map(axes.flatten()[count],lon,lat,Z*100,color_type=plt.cm.PiYG,color_range=[-10,10],color_label=None,subtitle='')
				if period=='2030s':							ax.set_title(model)
				if model==GHA['support']['model_names'][0]:	ax.set_ylabel(period)
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
	GHA[var]['exposure_diff'][rcp]['ensemble_mean']={}
	for period in GHA['support']['periods']:
		if period!='ref':
			GHA[var]['exposure_diff'][rcp]['ensemble_mean'][period]=GHA[var]['exposure_diff'][rcp]['models'][GHA['support']['model_names'][0]][period].copy()*0
			for model in GHA['support']['model_names']:
				GHA[var]['exposure_diff'][rcp]['ensemble_mean'][period]+=GHA[var]['exposure_diff'][rcp]['models'][model][period]
			GHA[var]['exposure_diff'][rcp]['ensemble_mean'][period]/=5

# agreement
for rcp in ['rcp2p6','rcp8p5']:
	GHA[var]['exposure_diff'][rcp]['agreement']={}
	for period in GHA['support']['periods']:
		if period!='ref':
			GHA[var]['exposure_diff'][rcp]['agreement'][period]=GHA[var]['exposure_diff'][rcp]['models'][GHA['support']['model_names'][0]][period].copy()*0
			for model in GHA['support']['model_names']:
				GHA[var]['exposure_diff'][rcp]['agreement'][period][np.where(np.sign(GHA[var]['exposure_diff'][rcp]['models'][model][period])==np.sign(GHA[var]['exposure_diff'][rcp]['ensemble_mean'][period]))]+=1
			GHA[var]['exposure_diff'][rcp]['agreement'][period][GHA[var]['exposure_diff'][rcp]['agreement'][period]>3]=np.nan
			GHA[var]['exposure_diff'][rcp]['agreement'][period][np.isnan(GHA[var]['exposure_diff'][rcp]['agreement'][period])==False]=0.5
			GHA[var]['exposure_diff'][rcp]['agreement'][period][np.where(np.isfinite(GHA[var]['exposure_diff'][rcp]['ensemble_mean'][period][:,:])==False)[0]]=np.nan


# plot extreme wet events
if True:
	fig,axes=plt.subplots(nrows=2,ncols=2,figsize=(7,6))
	count=0
	for rcp in range(2):
		for period in ['2030s','2040s']:
			Z=GHA[var]['exposure_diff'][rcp_str[rcp]]['ensemble_mean'][period].copy()*100
			Z[Z==0]=np.nan
			print rcp_str[rcp],period,np.mean(np.ma.masked_invalid(Z)),np.min(np.ma.masked_invalid(Z)),np.max(np.ma.masked_invalid(Z))
			ax,im=plot_map(axes.flatten()[count],lon,lat,Z,color_type=risk,color_range=[-2.5,10],color_label=None,subtitle='',grey_area=GHA[var]['exposure_diff'][rcp_str[rcp]]['agreement'][period])
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



