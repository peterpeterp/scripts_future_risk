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
GHA={'tas':{'RCP2.6':{'models':{}},'RCP8.5':{'models':{}}}, 'SPEI':{'RCP2.6':{'models':{}},'RCP8.5':{'models':{}}},'support':{}, 'rx5':{'RCP2.6':{'models':{}},'RCP8.5':{'models':{}}},'support':{}}

GHA['support']['model_names']=[]
GHA['support']['periods']={'ref':1985,'2030s':2024,'2040s':2034}

GHA['support']['files']={}
GHA['support']['files']['tas']=glob.glob('Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/CMIP5/*/mon_tas*.nc4')
GHA['support']['files']['SPEI']=glob.glob('Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/CMIP5/*/spei*12m*.nc4')
GHA['support']['files']['rx5']=glob.glob('Projects/WB_DRM/country_data/climate_input/'+iso+'/raw/CMIP5/*/mon_rx5*.nc4')

for var in ['tas','SPEI','rx5']:
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
	for rcp in ['RCP2.6','RCP8.5']:
		GHA[var][rcp]['ensemble_mean']=GHA[var][rcp]['models'][GHA[var][rcp]['models'].keys()[0]].copy()*0
		for model in GHA['support']['model_names']:
			GHA[var][rcp]['ensemble_mean']+=GHA[var][rcp]['models'][model]
		GHA[var][rcp]['ensemble_mean']/=5

###############
# plot settings
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

fig,axes=plt.subplots(nrows=3,ncols=5,figsize=(7,6))
ax,im=plot_map(axes[0,3],lons,lats,Z,color_type=month_color,color_range=[1,12],color_label=None,subtitle='')
ax.set_aspect(1.)
plt.show()
#fig.tight_layout()
plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_test.png')

rcp_names=['low warming','high warming']
rcp_str=['RCP2.6','RCP8.5']

risk = make_colormap([col_conv('green'), col_conv('white'), 0.2, col_conv('white'), col_conv('yellow'), 0.4, col_conv('yellow'), col_conv('orange'), 0.6, col_conv('orange'), col_conv('red'), 0.8, col_conv('red'), col_conv('violet')])
month_color = mpl.colors.ListedColormap(sns.color_palette("cubehelix", 12))

#####################
# extreme dry events
#####################
var='SPEI'

#exposure
GHA[var]['exposure']={'RCP2.6':{'models':{}},'RCP8.5':{'models':{}}}
for rcp in ['RCP2.6','RCP8.5']:
	for model in GHA['support']['model_names']:
		GHA[var]['exposure'][rcp]['models'][model]={}
		for period in GHA['support']['periods']:
			start_year=GHA['support']['periods'][period]
			relevant_time_indices=np.where((GHA['support']['year']>start_year) & (GHA['support']['year']<=start_year+20))[0]
			tmp=GHA[var][rcp]['models'][model][0,:,:].copy()
			for y in range(tmp.shape[0]):
				for x in range(tmp.shape[1]):
					tmp[y,x]=float(len(np.where(GHA[var][rcp]['models'][model][relevant_time_indices,y,x].flatten()<=-2)[0]))/len(relevant_time_indices)
			GHA[var]['exposure'][rcp]['models'][model][period]=tmp

#exposure diff
GHA[var]['exposure_diff']={'RCP2.6':{'models':{}},'RCP8.5':{'models':{}}}	
for rcp in ['RCP2.6','RCP8.5']:
	GHA[var][rcp]['period_diff']={}
	for model in GHA['support']['model_names']:
		GHA[var]['exposure_diff'][rcp]['models'][model]={}
		for period in GHA['support']['periods']:
			if period!='ref':
				GHA[var]['exposure_diff'][rcp]['models'][model][period]=GHA[var]['exposure'][rcp]['models'][model][period]-GHA[var]['exposure'][rcp]['models'][model]['ref']

# ensemble mean
for rcp in ['RCP2.6','RCP8.5']:
	GHA[var]['exposure_diff'][rcp]['ensemble_mean']={}
	for period in GHA['support']['periods']:
		if period!='ref':
			GHA[var]['exposure_diff'][rcp]['ensemble_mean'][period]=GHA[var]['exposure_diff'][rcp]['models'][GHA['support']['model_names'][0]][period].copy()*0
			for model in GHA['support']['model_names']:
				GHA[var]['exposure_diff'][rcp]['ensemble_mean'][period]+=GHA[var]['exposure_diff'][rcp]['models'][model][period]
			GHA[var]['exposure_diff'][rcp]['ensemble_mean'][period]/=5

# agreement
for rcp in ['RCP2.6','RCP8.5']:
	GHA[var]['exposure_diff'][rcp]['agreement']={}
	for period in GHA['support']['periods']:
		if period!='ref':
			GHA[var]['exposure_diff'][rcp]['agreement'][period]=GHA[var]['exposure_diff'][rcp]['models'][GHA['support']['model_names'][0]][period].copy()*0
			for model in GHA['support']['model_names']:
				GHA[var]['exposure_diff'][rcp]['agreement'][period][np.where(np.sign(GHA[var]['exposure_diff'][rcp]['models'][model][period])==np.sign(GHA[var]['exposure_diff'][rcp]['ensemble_mean'][period]))]+=1
			GHA[var]['exposure_diff'][rcp]['agreement'][period][GHA[var]['exposure_diff'][rcp]['agreement'][period]>3]=np.nan
			GHA[var]['exposure_diff'][rcp]['agreement'][period][np.isnan(GHA[var]['exposure_diff'][rcp]['agreement'][period])==False]=0.5
			GHA[var]['exposure_diff'][rcp]['agreement'][period][np.where(np.isfinite(GHA[var][rcp]['models'][model][0,:,:])==False)[0]]=np.nan

# extreme dry events overview
if False:
	fig,axes=plt.subplots(nrows=2,ncols=2,figsize=(7,6))
	count=0
	for rcp in range(2):
		for period in ['2030s','2040s']:
			Z=GHA['SPEI']['exposure_diff'][rcp_str[rcp]]['ensemble_mean'][period].copy()*100
			Z[Z==0]=np.nan
			print rcp_str[rcp],period,np.mean(np.ma.masked_invalid(Z)),np.min(np.ma.masked_invalid(Z)),np.max(np.ma.masked_invalid(Z))
			ax,im=plot_map(axes.flatten()[count],lons,lats,Z,color_type=rvb,color_range=[-7,28],color_label=None,subtitle='',grey_area=GHA['SPEI']['exposure_diff'][rcp_str[rcp]]['agreement'][period])
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


