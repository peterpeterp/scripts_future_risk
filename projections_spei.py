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
var='SPEI'
GHA_spei=prepare_country_dict(var=var,files=glob.glob('Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/CMIP5/*/spei*12m*.nc4'))
GHA_spei['support']['periods']={'ref':1985,'2030s':2024,'2040s':2034}

###############
# plot settings
###############
lon=GHA_spei['support']['lon'].copy()
lat=GHA_spei['support']['lat'].copy()

rcp_names=['low warming','high warming']
rcp_str=['rcp2p6','rcp8p5']

risk = make_colormap([col_conv('green'), col_conv('white'), 0.2, col_conv('white'), col_conv('yellow'), 0.4, col_conv('yellow'), col_conv('orange'), 0.6, col_conv('orange'), col_conv('red'), 0.8, col_conv('red'), col_conv('violet')])
month_color = mpl.colors.ListedColormap(sns.color_palette("cubehelix", 12))

#####################
# extreme dry events
#####################

#exposure
GHA_spei['exposure']={'rcp2p6':{'models':{}},'rcp8p5':{'models':{}}}
for rcp in ['rcp2p6','rcp8p5']:
	for model in GHA_spei['support']['model_names']:
		GHA_spei['exposure'][rcp]['models'][model]={}
		for period in GHA_spei['support']['periods']:
			start_year=GHA_spei['support']['periods'][period]
			relevant_time_indices=np.where((GHA_spei['support']['year']>start_year) & (GHA_spei['support']['year']<=start_year+20))[0]
			tmp=GHA_spei[rcp]['models'][model][0,:,:].copy()
			for y in range(tmp.shape[0]):
				for x in range(tmp.shape[1]):
					tmp[y,x]=float(len(np.where(GHA_spei[rcp]['models'][model][relevant_time_indices,y,x].flatten()<=-2)[0]))/len(relevant_time_indices)
			GHA_spei['exposure'][rcp]['models'][model][period]=tmp

#exposure diff
GHA_spei['exposure_diff']={'rcp2p6':{'models':{}},'rcp8p5':{'models':{}}}	
for rcp in ['rcp2p6','rcp8p5']:
	GHA_spei[rcp]['period_diff']={}
	for model in GHA_spei['support']['model_names']:
		GHA_spei['exposure_diff'][rcp]['models'][model]={}
		for period in GHA_spei['support']['periods']:
			if period!='ref':
				GHA_spei['exposure_diff'][rcp]['models'][model][period]=GHA_spei['exposure'][rcp]['models'][model][period]-GHA_spei['exposure'][rcp]['models'][model]['ref']

# ensemble mean
for rcp in ['rcp2p6','rcp8p5']:
	GHA_spei['exposure_diff'][rcp]['ensemble_mean']={}
	for period in GHA_spei['support']['periods']:
		if period!='ref':
			GHA_spei['exposure_diff'][rcp]['ensemble_mean'][period]=GHA_spei['exposure_diff'][rcp]['models'][GHA_spei['support']['model_names'][0]][period].copy()*0
			for model in GHA_spei['support']['model_names']:
				GHA_spei['exposure_diff'][rcp]['ensemble_mean'][period]+=GHA_spei['exposure_diff'][rcp]['models'][model][period]
			GHA_spei['exposure_diff'][rcp]['ensemble_mean'][period]/=5

# agreement
for rcp in ['rcp2p6','rcp8p5']:
	GHA_spei['exposure_diff'][rcp]['agreement']={}
	for period in GHA_spei['support']['periods']:
		if period!='ref':
			GHA_spei['exposure_diff'][rcp]['agreement'][period]=GHA_spei['exposure_diff'][rcp]['models'][GHA_spei['support']['model_names'][0]][period].copy()*0
			for model in GHA_spei['support']['model_names']:
				GHA_spei['exposure_diff'][rcp]['agreement'][period][np.where(np.sign(GHA_spei['exposure_diff'][rcp]['models'][model][period])==np.sign(GHA_spei['exposure_diff'][rcp]['ensemble_mean'][period]))]+=1
			GHA_spei['exposure_diff'][rcp]['agreement'][period][GHA_spei['exposure_diff'][rcp]['agreement'][period]>3]=np.nan
			GHA_spei['exposure_diff'][rcp]['agreement'][period][np.isnan(GHA_spei['exposure_diff'][rcp]['agreement'][period])==False]=0.5
			GHA_spei['exposure_diff'][rcp]['agreement'][period][np.where(np.isfinite(GHA_spei['exposure_diff'][rcp]['ensemble_mean'][period][:,:])==False)[0]]=np.nan

# extreme dry events overview
if True:
	fig,axes=plt.subplots(nrows=2,ncols=2,figsize=(7,6))
	count=0
	for rcp in range(2):
		for period in ['2030s','2040s']:
			Z=GHA_spei['exposure_diff'][rcp_str[rcp]]['ensemble_mean'][period].copy()*100
			Z[Z==0]=np.nan
			print rcp_str[rcp],period,np.mean(np.ma.masked_invalid(Z)),np.min(np.ma.masked_invalid(Z)),np.max(np.ma.masked_invalid(Z))
			ax,im=plot_map(axes.flatten()[count],lon,lat,Z,color_type=risk,color_range=[-7,28],color_label=None,subtitle='',grey_area=GHA_spei['exposure_diff'][rcp_str[rcp]]['agreement'][period])
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
	plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_SPEI_exposure.png')


