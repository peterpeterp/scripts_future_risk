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
from country_average import *
from plot_functions import *
sys.path.append('/Users/peterpfleiderer/Documents/Projects/WB_DRM/')

iso='CMR'

rcp_str=['RCP2.6','RCP8.5']

for varin in ['spei_12m','spei_6m','spei_1m']:
	for rcp in range(2):
		nc_in=Dataset('/Users/peterpfleiderer/Documents/Projects/WB_DRM/climate_risk_data/'+iso+'/MWI_CMIP5_'+varin+'_exposure.nc4')
		var_names=list(nc_in.variables.keys())

		expo=nc_in.variables['exposure'][:]


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

		expo_masked=np.ma.masked_invalid(expo)


		period_str=['Reference','2030s','2040s']
		model_str=nc_in.variables['exposure'].getncattr('models').split(' ')

		fig,axes=plt.subplots(nrows=3,ncols=5,figsize=(12,12))


		count=0
		for time in range(3):
			for model in range(5):
				ax,im=plot_map(axes.flat[count],lons,lats,expo[:,:,time,rcp,model],color_type=plt.cm.seismic,color_range=[-0.1,0.1],color_label=None,subtitle=model_str[model])	
				if model==0:	ax.set_ylabel(period_str[time],size='large')
				count+=1

		cbar_ax=fig.add_axes([0,0.05,1,0.15])
		cbar_ax.axis('off')
		fig.colorbar(im,orientation='horizontal',label='ratio of months affected by SPEI -2')
		#fig.tight_layout()
		plt.suptitle(varin+' '+rcp_str[rcp],size='large')

		plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_'+varin+'_detail_'+rcp_str[rcp]+'.png')
		plt.clf()







###############
# detail SPEI view
###############


# for varin in ['spei_12m','spei_6m','spei_1m']:
# 	for rcp in range(2):
# 		nc_in=Dataset('/Users/peterpfleiderer/Documents/Projects/WB_DRM/climate_risk_data/'+iso+'/MWI_CMIP5_'+varin+'_exposure.nc4')
# 		var_names=list(nc_in.variables.keys())

# 		expo=nc_in.variables['exposure'][:]


# 		lat=nc_in.variables['lat'][:]
# 		lon=nc_in.variables['lon'][:]

# 		lon=lon.copy()
# 		step=np.diff(lon,1)[0]
# 		lon-=step/2
# 		lon=np.append(lon,np.array(lon[-1]+step))

# 		lat=lat.copy()
# 		step=np.diff(lat,1)[0]
# 		lat-=step/2
# 		lat=np.append(lat,lat[-1]+step)

# 		lons, lats = np.meshgrid(lon,lat)

# 		expo_masked=np.ma.masked_invalid(expo)


# 		period_str=['Reference','2030s','2040s']
# 		model_str=nc_in.variables['exposure'].getncattr('models').split(' ')

# 		fig,axes=plt.subplots(nrows=3,ncols=5,figsize=(12,12))


# 		count=0
# 		for time in range(3):
# 			for model in range(5):
# 				ax,im=plot_map(axes.flat[count],lons,lats,expo[:,:,time,rcp,model],color_type=plt.cm.seismic,color_range=[-0.1,0.1],color_label=None,subtitle=model_str[model])	
# 				if model==0:	ax.set_ylabel(period_str[time],size='large')
# 				count+=1

# 		cbar_ax=fig.add_axes([0,0.05,1,0.15])
# 		cbar_ax.axis('off')
# 		fig.colorbar(im,orientation='horizontal',label='ratio of months affected by SPEI -2')
# 		#fig.tight_layout()
# 		plt.suptitle(varin+' '+rcp_str[rcp],size='large')

# 		plt.savefig('/Users/peterpfleiderer/Documents/Projects/WB_DRM/plots/'+iso+'/'+iso+'_'+varin+'_detail_'+rcp_str[rcp]+'.png')
# 		plt.clf()
