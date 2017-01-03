import numpy as np
from netCDF4 import Dataset
import os,sys
import glob

os.chdir('/home/pepflei/CA/Scripts/allgemeine_scripte')
sys.path.append('/home/pepflei/CA/Scripts/allgemeine_scripte')
from country_zoom import *
from country_average import *
os.chdir('/home/pepflei/CA')

iso='GHA'

# prepare directory
os.system('mkdir /home/pepflei/CA/data/country_data/'+iso)
os.system('mkdir /home/pepflei/CA/data/country_data/'+iso+'/raw/')
os.system('mkdir /home/pepflei/CA/data/country_data/'+iso+'/raw/CMIP5/')
os.system('mkdir /home/pepflei/CA/data/country_data/'+iso+'/raw/OBS/')
for rcp in ['RCP2.6','RCP8.5']:
	os.system('mkdir /home/pepflei/CA/data/country_data/'+iso+'/raw/CMIP5/'+rcp)
for obs in ['CRU','NCEP']:
	os.system('mkdir /home/pepflei/CA/data/country_data/'+iso+'/raw/OBS/'+obs)

job_id=int(os.environ["SLURM_ARRAY_TASK_ID"])
print 'job_id=',job_id

if job_id==0:
	# CMIP5 tas
	for rcp in ['RCP2.6','RCP8.5']:
		all_files=glob.glob('/p/projects/climber3/knaus/Global/Input_data/CMIP5/'+rcp+'/*/mon_tas_*')
		for file in all_files:
			country_zoom(in_file=file,out_file='/home/pepflei/CA/data/country_data/'+iso+'/raw/CMIP5/'+rcp+'/'+file.split('/')[-1].replace('.nc4','_'+iso+'.nc4'),var='tas',iso=iso,mask_path='/home/pepflei/CA/masks/')
		country_average(all_files,var='tas',out_path='/home/pepflei/CA/data/country_data/'+iso+'/raw/CMIP5/'+rcp+'/',popYear='None',continents=['africa'],countries=[iso])

if job_id==1:
	# CMIP5 pr
	for rcp in ['RCP2.6','RCP8.5']:
		all_files=glob.glob('/p/projects/climber3/knaus/Global/Input_data/CMIP5/'+rcp+'/*/mon_pr_*')
		for file in all_files:
			country_zoom(in_file=file,out_file='/home/pepflei/CA/data/country_data/'+iso+'/raw/CMIP5/'+rcp+'/'+file.split('/')[-1].replace('.nc4','_'+iso+'.nc4'),var='pr',iso=iso,mask_path='/home/pepflei/CA/masks/')
		country_average(all_files,var='pr',out_path='/home/pepflei/CA/data/country_data/'+iso+'/raw/CMIP5/'+rcp+'/',popYear='None',continents=['africa'],countries=[iso])

if job_id==2:
	# CMIP5 rx5
	RCPs=['RCP2.6','RCP8.5']
	rcps=['rcp2p6','rcp8p5']
	for rcp in range(2):
		all_files=glob.glob('/p/projects/tumble/carls/shared_folder/rx5/mon_rx5_*'+rcps[rcp]+'*')
		all_files=glob.glob('/p/projects/tumble/carls/shared_folder/rx5/R_rx5/mon_rx5_*'+rcps[rcp]+'*')
		for file in all_files:
			country_zoom(in_file=file,out_file='/home/pepflei/CA/data/country_data/'+iso+'/raw/CMIP5/'+RCPs[rcp]+'/'+file.split('/')[-1].replace('.nc4','_'+iso+'_month_cut.nc4'),var='rx5',iso=iso,mask_path='/home/pepflei/CA/masks/')
			country_average(in_file=file,out_file='/home/pepflei/CA/data/country_data/'+iso+'/raw/CMIP5/'+RCPs[rcp]+'/'+file.split('/')[-1].replace('.nc4','_'+iso+'_month_cut.csv'),var='rx5',mask_files=['/home/pepflei/CA/masks/720x360/sov_2015_africa.nc'],countries=[iso])

if job_id==3:
	# CMIP5 spei 12m
	for rcp in ['2.6','8.5']:
		all_files=glob.glob('/p/projects/climber3/knaus/Global/Indices/SPEI/CMIP5/spei_*_rcp'+rcp+'_*12m*')
		for file in all_files:
			country_zoom(in_file=file,out_file='/home/pepflei/CA/data/country_data/'+iso+'/raw/CMIP5/RCP'+rcp+'/'+file.split('/')[-1].replace('.nc4','_'+iso+'.nc4'),var='SPEI',iso=iso,mask_path='/home/pepflei/CA/masks/')
		country_average(all_files,var='SPEI',out_path='/home/pepflei/CA/data/country_data/'+iso+'/raw/CMIP5/RCP'+rcp+'/',popYear='None',continents=['africa'],countries=[iso])

if job_id==4:
	# CMIP5 spei 6m
	for rcp in ['2.6','8.5']:
		all_files=glob.glob('/p/projects/climber3/knaus/Global/Indices/SPEI/CMIP5/spei_*_rcp'+rcp+'_*6m*')
		for file in all_files:
			country_zoom(in_file=file,out_file='/home/pepflei/CA/data/country_data/'+iso+'/raw/CMIP5/RCP'+rcp+'/'+file.split('/')[-1].replace('.nc4','_'+iso+'.nc4'),var='SPEI',iso=iso,mask_path='/home/pepflei/CA/masks/')
		country_average(all_files,var='SPEI',out_path='/home/pepflei/CA/data/country_data/'+iso+'/raw/CMIP5/RCP'+rcp+'/',popYear='None',continents=['africa'],countries=[iso])

if job_id==5:
	# CMIP5 spei 1m
	for rcp in ['2.6','8.5']:
		all_files=glob.glob('/p/projects/climber3/knaus/Global/Indices/SPEI/CMIP5/spei_*_rcp'+rcp+'_*1m*')
		for file in all_files:
			country_zoom(in_file=file,out_file='/home/pepflei/CA/data/country_data/'+iso+'/raw/CMIP5/RCP'+rcp+'/'+file.split('/')[-1].replace('.nc4','_'+iso+'.nc4'),var='SPEI',iso=iso,mask_path='/home/pepflei/CA/masks/')
		country_average(all_files,var='SPEI',out_path='/home/pepflei/CA/data/country_data/'+iso+'/raw/CMIP5/RCP'+rcp+'/',popYear='None',continents=['africa'],countries=[iso])

if job_id==6:
	# CMIP5 spei 3m
	for rcp in ['2.6','8.5']:
		all_files=glob.glob('/p/projects/tumble/carls/shared_folder/SPEI/spei_*_rcp'+rcp+'_*3m*')
		for file in all_files:
			country_zoom(in_file=file,out_file='/home/pepflei/CA/data/country_data/'+iso+'/raw/CMIP5/RCP'+rcp+'/'+file.split('/')[-1].replace('.nc4','_'+iso+'.nc4'),var='spei',iso=iso,mask_path='/home/pepflei/CA/masks/')
		country_average(all_files,var='spei',out_path='/home/pepflei/CA/data/country_data/'+iso+'/raw/CMIP5/RCP'+rcp+'/',popYear='None',continents=['africa'],countries=[iso])







if job_id==7:
	# NCEP tas
	all_files=glob.glob('/p/projects/climber3/knaus/Global/Input_data/NCEP/tas_*')
	for file in all_files:
		country_zoom(in_file=file,out_file='/home/pepflei/CA/data/country_data/'+iso+'/raw/OBS/NCEP/'+file.split('/')[-1].replace('.nc4','_'+iso+'.nc4'),var='tas',iso=iso,mask_path='/home/pepflei/CA/masks/')
	country_average(all_files,var='tas',out_path='/home/pepflei/CA/data/country_data/'+iso+'/raw/OBS/NCEP/',popYear='None',continents=['africa'],countries=[iso])

if job_id==8:
	# NCEP pr
	all_files=glob.glob('/p/projects/climber3/knaus/Global/Input_data/NCEP/pr_*')
	for file in all_files:
		country_zoom(in_file=file,out_file='/home/pepflei/CA/data/country_data/'+iso+'/raw/OBS/NCEP/'+file.split('/')[-1].replace('.nc4','_'+iso+'.nc4'),var='pr',iso=iso,mask_path='/home/pepflei/CA/masks/')
	country_average(all_files,var='pr',out_path='/home/pepflei/CA/data/country_data/'+iso+'/raw/OBS/NCEP/',popYear='None',continents=['africa'],countries=[iso])

if job_id==9:
	# NCEP SPEI
	all_files=glob.glob('/p/projects/climber3/knaus/Global/Indices/SPEI/NCEP/*')
	for file in all_files:
		country_zoom(in_file=file,out_file='/home/pepflei/CA/data/country_data/'+iso+'/raw/OBS/NCEP/'+file.split('/')[-1].replace('.nc4','_'+iso+'.nc4'),var='SPEI',iso=iso,mask_path='/home/pepflei/CA/masks/')
	country_average(all_files,var='SPEI',out_path='/home/pepflei/CA/data/country_data/'+iso+'/raw/OBS/NCEP/',popYear='None',continents=['africa'],countries=[iso])







if job_id==10:
	# CRU tas
	all_files=glob.glob('/p/projects/elis/CRUDATA_TS3_23/cru_ts3.23.1901.2014.tmp.dat.nc')
	for file in all_files:
		country_zoom(in_file=file,out_file='/home/pepflei/CA/data/country_data/'+iso+'/raw/OBS/CRU/'+file.split('/')[-1].replace('.nc4','_'+iso+'.nc4'),var='tmp',iso=iso,mask_path='/home/pepflei/CA/masks/')
	country_average(all_files,var='tmp',out_path='/home/pepflei/CA/data/country_data/'+iso+'/raw/OBS/CRU/',popYear='None',continents=['africa'],countries=[iso])

if job_id==11:
	# CRU pre
	all_files=glob.glob('/p/projects/elis/CRUDATA_TS3_23/cru_ts3.23.1901.2014.pre.dat.nc')
	for file in all_files:
		country_zoom(in_file=file,out_file='/home/pepflei/CA/data/country_data/'+iso+'/raw/OBS/CRU/'+file.split('/')[-1].replace('.nc4','_'+iso+'.nc4'),var='pre',iso=iso,mask_path='/home/pepflei/CA/masks/')
	country_average(all_files,var='pre',out_path='/home/pepflei/CA/data/country_data/'+iso+'/raw/OBS/CRU/',popYear='None',continents=['africa'],countries=[iso])

if job_id==12:
	# CRU spei
	all_files=glob.glob('/home/pepflei/CA/data/SPEI/CRU/*')
	for file in all_files:
		country_zoom(in_file=file,out_file='/home/pepflei/CA/data/country_data/'+iso+'/raw/OBS/CRU/'+file.split('/')[-1].replace('.nc4','_'+iso+'.nc4'),var='spei',iso=iso,mask_path='/home/pepflei/CA/masks/')
	country_average(all_files,var='spei',out_path='/home/pepflei/CA/data/country_data/'+iso+'/raw/OBS/CRU/',popYear='None',continents=['africa'],countries=[iso])













