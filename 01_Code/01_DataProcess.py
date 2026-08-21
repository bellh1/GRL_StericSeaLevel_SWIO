#%% 00 to 01 ARGO: varname + domain/period cut + pressure to depth; TOPO: regrid to the ARGO grid
from functions import *
inDIR = ''
ARGO=nctopd(inDIR+'/00_ARGO.nc')
ds = ARGO._ds.rename({'PRES':'pres', 'TOI':'temp', 'SOI':'sali'})
ds = ds.sortby(['lat','lon','pres'])
ds = ds.sel(lon=slice(39, 121), lat=slice(-71, 26), time=slice('2004-01-01', '2024-01-31'))
W, depth_tgt = pres2depth_w(ds['pres'].values, ds['lat'].values, lat_ref=None, dim='pres')
ARGO = pd.Series({'time': ds['time'], 'depth': xr.DataArray(depth_tgt, dims=('depth',)), 'lat': ds['lat'], 'lon': ds['lon'], 'temp': p2z(ds['temp'], W), 'sali': p2z(ds['sali'], W)}, dtype=object)
pdtonc(ARGO, inDIR+'/01_ARGO.nc', time_chunk=12, depth_chunk=16, lat_chunk=90, lon_chunk=180)

ARGO=nctopd(inDIR+'/01_ARGO.nc')
topo=nctopd(inDIR+'/00_TOPO.nc')
topo_regrid = regrid(data=topo['elevation']().values, latfrom=topo['lat']().values, lonfrom=topo['lon']().values, latto=ARGO['lat']().values, lonto=ARGO['lon']().values, n_jobs=-1, backend='threading')
topo = pdlabel(topo, 'del', ['elevation'])
topo=pdlabel(topo, 'data', 'lat', ARGO['lat']().values)
topo=pdlabel(topo, 'data', 'lon', ARGO['lon']().values)
topo=pdlabel(topo, 'data', 'topo', topo_regrid)
topo._ds = topo._ds.sortby(['lat','lon']).sel(lat=slice(-71, 26), lon=slice(39, 121))
[setattr(v, '_ds', topo._ds) for _, v in topo.items() if hasattr(v, '_ds')]
pdtonc(topo, inDIR+'/01_TOPO.nc')

#%% 01 to 02 mask below topography + drop empty depth levels
from functions import *
inDIR = ''
topo=nctopd(inDIR+'/01_TOPO.nc')
ARGO=nctopd(inDIR+'/01_ARGO.nc')

d4 = xr.DataArray(ARGO['depth'](), dims=('depth',)).broadcast_like(ARGO['temp']())
t4 = topo['topo']().broadcast_like(ARGO['temp']())
ARGO = pdlabel(ARGO, 'data', 'temp', ARGO['temp']().where(d4 <= t4))
ARGO = pdlabel(ARGO, 'data', 'sali', ARGO['sali']().where(d4 <= t4))
valid_depth = (~(((ARGO['temp']().isnull()) & (ARGO['sali']().isnull())).all(dim=('time', 'lat', 'lon')))).compute()
ARGO = pdlabel(ARGO, 'data', 'depth', ARGO['depth']().isel(depth=valid_depth), 'temp', ARGO['temp']().isel(depth=valid_depth), 'sali', ARGO['sali']().isel(depth=valid_depth))
pdtonc(ARGO, inDIR+'/02_ARGO.nc', time_chunk=12, depth_chunk=16, lat_chunk=90, lon_chunk=180)

#%% 02 to 03 conservative temperature, absolute salinity + sigma0
from functions import *
inDIR = ''
ARGO=nctopd(inDIR+'/02_ARGO.nc')
ARGO._ds = ARGO._ds.assign_coords(time=('time', copy.copy(pd.DatetimeIndex(pd.to_datetime(ARGO['time']().values).to_period('M').to_timestamp()))))
[setattr(v, '_ds', ARGO._ds) for _, v in ARGO.items() if hasattr(v, '_ds')]
ct, as_ = ctas(ARGO, temptype='c', salitype='ps')
ARGO = pdlabel(ARGO, 'data', 'temp', ct)
ARGO = pdlabel(ARGO, 'data', 'sali', as_)
ARGO = pdlabel(ARGO, 'data', 'dens', gsw.sigma0(as_, ct))
pdtonc(ARGO, inDIR+'/03_ARGO.nc', time_chunk=6, depth_chunk=16, lat_chunk=90, lon_chunk=180)

#%% 03 to 04 specific volume + 2004-2023 reference state + layer thickness
from functions import *
inDIR = ''
ARGO=nctopd(inDIR+'/03_ARGO.nc')
sv = specvol(ARGO).persist()
ARGO = pdlabel(ARGO, 'data', 'vol', sv)
tsl = slice('2004-01-01', '2023-12-31')
t = np.nanmean(ARGO['temp']().sel(time=tsl).values, axis=0)
s = np.nanmean(ARGO['sali']().sel(time=tsl).values, axis=0)
svt = specvolts(ARGO, 'sali', s).persist()
svs = specvolts(ARGO, 'temp', t).persist()
ARGO = pdlabel(ARGO, 'data', 'tvol', svt)
ARGO = pdlabel(ARGO, 'data', 'svol', svs)
ARGO = pdlabel(ARGO, 'data', 'tmean', t)
ARGO = pdlabel(ARGO, 'data', 'smean', s)
ARGO = pdlabel(ARGO, 'data', 'd_ran', dz(ARGO['depth']().values))
ARGO = pdlabel(ARGO, 'del', ['temp', 'sali', 'dens'])
pdtonc(ARGO, inDIR+'/04_ARGO.nc', time_chunk=12, depth_chunk=16, lat_chunk=90, lon_chunk=180)

#%% 04 to 05 steric height calculation
from functions import *
inDIR = ''
ARGO=nctopd(inDIR+'/04_ARGO.nc')
ARGO = pdlabel(ARGO, 'data', 'hei', steric_h(ARGO, 'vol', mt='tmean', ms='smean', dz='d_ran'))
ARGO = pdlabel(ARGO, 'data', 'thei', steric_h(ARGO, 'tvol', mt='tmean', ms='smean', dz='d_ran'))
ARGO = pdlabel(ARGO, 'data', 'shei', steric_h(ARGO, 'svol', mt='tmean', ms='smean', dz='d_ran'))
ARGO = pdlabel(ARGO, 'del', ['vol', 'tvol', 'svol', 'tmean', 'smean'])
pdtonc(ARGO, inDIR+'/05_ARGO.nc', time_chunk=12, depth_chunk=16, lat_chunk=90, lon_chunk=180)

#%% 03 to 06 spice & heave trends + AR(1)-adjusted significance
from functions import *
inDIR = ''
ARGO=nctopd(inDIR+'/03_ARGO.nc')
heave_t, heave_s= heave_trend(ARGO, s='2004-01-01', f='2023-12-31', depth='m', rm_season=True)
spice_t, spice_s= spice_trend(ARGO, s='2004-01-01', f='2023-12-31', depth='m', rm_season=True)
ARGO = pdlabel(ARGO, 'data', 'heave_tr', heave_t)
ARGO = pdlabel(ARGO, 'data', 'heave_sr', heave_s)
ARGO = pdlabel(ARGO, 'data', 'spice_tr', spice_t)
ARGO = pdlabel(ARGO, 'data', 'spice_sr', spice_s)
ARGO = pdlabel(ARGO, 'data', 'trend_tr', litrend(ARGO, 'temp',s='2004-01-01', f='2023-12-31', rm_season=True))
ARGO = pdlabel(ARGO, 'data', 'trend_sr', litrend(ARGO, 'sali',s='2004-01-01', f='2023-12-31', rm_season=True))

hser_t, hser_s = heave_trend(ARGO, s='2004-01-01', f='2023-12-31', depth='m', rm_season=True, return_series=True)
sser_t, sser_s = spice_trend(ARGO, s='2004-01-01', f='2023-12-31', depth='m', rm_season=True, return_series=True)
for nm, da, rs in [('p_trend_tr', ARGO['temp'](), True), ('p_trend_sr', ARGO['sali'](), True), ('p_heave_tr', hser_t, False), ('p_heave_sr', hser_s, False), ('p_spice_tr', sser_t, False), ('p_spice_sr', sser_s, False)]:
    _, _, _, pv, _, _ = litrend(da.rename('x'), 'x', s='2004-01-01', f='2023-12-31', rm_season=rs, lonmin=50, lonmax=80, ar1=True, return_stats=True)
    ARGO = pdlabel(ARGO, 'data', nm, pv.compute())

tsl = slice('2004-01-01', '2023-12-31')
dens = np.nanmean(ARGO['dens']().sel(time=tsl).values, axis=0)
ARGO = pdlabel(ARGO, 'del', ['dens'])
ARGO = pdlabel(ARGO, 'data', 'dens', dens)
ARGO = pdlabel(ARGO, 'del', ['temp', 'sali'])
pdtonc(ARGO, inDIR+'/06_ARGO.nc', time_chunk=12, depth_chunk=16, lat_chunk=90, lon_chunk=180)

#%% 00 to 01 varname + domain/period cut + 2,000 m truncation for all datasets (EN4, ORAS5, SODA) + TOPO subdomain
from functions import *
inDIR = ''

EN4 = nctopd(inDIR+'/00_EN4.nc', align_chunks=False)
EN4 = pdlabel(EN4, 'fix', ['temperature', 'salinity'], ['temp', 'sali'])
ds = EN4._ds
ds = ds.isel({c: slice(None, None, -1) for c in ['lat','lon','depth'] if ds[c].values[0] > ds[c].values[-1]})
ds = ds.sel(time=slice('2004-01-01', '2024-01-31'), lat=slice(-21, 1), lon=slice(49, 81))
z = np.asarray(ds['depth'].values, dtype='float64')
dsz = ds.sel(depth=slice(None, 2000.0))
if not np.any(np.isclose(z, 2000.0)):
    k = int(np.searchsorted(z, 2000.0))
    dsz = xr.concat([dsz, ds.isel(depth=slice(k-1, k+1)).interp(depth=[2000.0])], dim='depth').sortby('depth')
EN4._ds = dsz
[setattr(v, '_ds', EN4._ds) for _, v in EN4.items() if hasattr(v, '_ds')]
pdtonc(EN4, inDIR+'/01_EN4.nc', time_chunk=12, depth_chunk=16)

topo = nctopd(inDIR+'/01_TOPO.nc')
topo._ds = topo._ds.sortby(['lat','lon']).sel(lat=slice(-21, 1), lon=slice(49, 81))
[setattr(v, '_ds', topo._ds) for _, v in topo.items() if hasattr(v, '_ds')]
pdtonc(topo, inDIR+'/02_TOPO.nc')

ORAS5 = nctopd(inDIR+'/00_ORAS5.nc', align_chunks=False)
ORAS5 = pdlabel(ORAS5, 'fix', ['time_counter', 'deptht', 'votemper', 'vosaline'], ['time', 'depth', 'temp', 'sali'])
ds = ORAS5._ds
ds = ds.isel({c: slice(None, None, -1) for c in ['lat','lon','depth'] if ds[c].values[0] > ds[c].values[-1]})
ds = ds.sel(time=slice('2004-01-01', '2024-01-31'), lat=slice(-21, 1), lon=slice(49, 81))
z = np.asarray(ds['depth'].values, dtype='float64')
dsz = ds.sel(depth=slice(None, 2000.0))
if not np.any(np.isclose(z, 2000.0)):
    k = int(np.searchsorted(z, 2000.0))
    dsz = xr.concat([dsz, ds.isel(depth=slice(k-1, k+1)).interp(depth=[2000.0])], dim='depth').sortby('depth')
ORAS5._ds = dsz
[setattr(v, '_ds', ORAS5._ds) for _, v in ORAS5.items() if hasattr(v, '_ds')]
pdtonc(ORAS5, inDIR+'/01_ORAS5.nc', time_chunk=12, depth_chunk=16)

SODA = nctopd(inDIR+'/00_SODA.nc', align_chunks=False)
SODA = pdlabel(SODA, 'fix', ['st_ocean', 'salt'], ['depth', 'sali'])
ds = SODA._ds
ds = ds.isel({c: slice(None, None, -1) for c in ['lat','lon','depth'] if ds[c].values[0] > ds[c].values[-1]})
ds = ds.sel(time=slice('2004-01-01', '2024-01-31'), lat=slice(-21, 1), lon=slice(49, 81))
z = np.asarray(ds['depth'].values, dtype='float64')
dsz = ds.sel(depth=slice(None, 2000.0))
if not np.any(np.isclose(z, 2000.0)):
    k = int(np.searchsorted(z, 2000.0))
    dsz = xr.concat([dsz, ds.isel(depth=slice(k-1, k+1)).interp(depth=[2000.0])], dim='depth').sortby('depth')
SODA._ds = dsz
[setattr(v, '_ds', SODA._ds) for _, v in SODA.items() if hasattr(v, '_ds')]
pdtonc(SODA, inDIR+'/01_SODA.nc', time_chunk=12, depth_chunk=16)

#%% 01 to 02 mask below topography + drop empty depth levels for all datasets (EN4, ORAS5, SODA)
from functions import *
inDIR = ''
topo=nctopd(inDIR+'/02_TOPO.nc')
nc_files=['EN4', 'ORAS5', 'SODA']
for i in ll(nc_files):
    data=nctopd(inDIR+'/01_'+nc_files[i]+'.nc')
    d4 = xr.DataArray(data['depth'](), dims=('depth',)).broadcast_like(data['temp']())
    t4 = topo['topo']().broadcast_like(data['temp']())
    data = pdlabel(data, 'data', 'temp', data['temp']().where(d4 <= t4))
    data = pdlabel(data, 'data', 'sali', data['sali']().where(d4 <= t4))
    valid_depth = (~(((data['temp']().isnull()) & (data['sali']().isnull())).all(dim=('time', 'lat', 'lon')))).compute()
    data = pdlabel(data, 'data', 'depth', data['depth']().isel(depth=valid_depth), 'temp', data['temp']().isel(depth=valid_depth), 'sali', data['sali']().isel(depth=valid_depth))
    pdtonc(data, inDIR+'/02_'+nc_files[i]+'.nc', time_chunk=12, depth_chunk=16, lat_chunk=90, lon_chunk=180)

#%% 02 to 03 conservative temperature, absolute salinity + sigma0 for all datasets (EN4, ORAS5, SODA)
from functions import *
inDIR = ''
nc_files=['EN4', 'ORAS5', 'SODA']

for i in ll(nc_files):
    nc_file=nctopd(inDIR+'/02_'+nc_files[i]+'.nc')
    nc_file._ds = nc_file._ds.assign_coords(time=('time', copy.copy(pd.DatetimeIndex(pd.to_datetime(nc_file['time']().values).to_period('M').to_timestamp()))))
    [setattr(v, '_ds', nc_file._ds) for _, v in nc_file.items() if hasattr(v, '_ds')]
    if nc_files[i] == 'EN4':
        ct, as_ = ctas(nc_file, temptype='k', salitype='ps')
    else:
        ct, as_ = ctas(nc_file, temptype='c', salitype='ps')
    nc_file = pdlabel(nc_file, 'data', 'temp', ct)
    nc_file = pdlabel(nc_file, 'data', 'sali', as_)
    nc_file = pdlabel(nc_file, 'data', 'dens', gsw.sigma0(as_, ct))
    pdtonc(nc_file, inDIR+'/03_'+nc_files[i]+'.nc', time_chunk=6, depth_chunk=16, lat_chunk=90, lon_chunk=180)

#%% 03 to 04 specific volume + 2004-2023 reference state + layer thickness for all datasets (EN4, ORAS5, SODA)
from functions import *
inDIR = ''
nc_files=['EN4', 'ORAS5', 'SODA']
for i in ll(nc_files):
    nc_file=nctopd(inDIR+'/03_'+nc_files[i]+'.nc')
    sv = specvol(nc_file).persist()
    nc_file = pdlabel(nc_file, 'data', 'vol', sv)
    tsl = slice('2004-01-01', '2023-12-31')
    t = np.nanmean(nc_file['temp']().sel(time=tsl).values, axis=0)
    s = np.nanmean(nc_file['sali']().sel(time=tsl).values, axis=0)
    svt = specvolts(nc_file, 'sali', s).persist()
    svs = specvolts(nc_file, 'temp', t).persist()
    nc_file = pdlabel(nc_file, 'data', 'tvol', svt)
    nc_file = pdlabel(nc_file, 'data', 'svol', svs)
    nc_file = pdlabel(nc_file, 'data', 'tmean', t)
    nc_file = pdlabel(nc_file, 'data', 'smean', s)
    nc_file = pdlabel(nc_file, 'data', 'd_ran', dz(nc_file['depth']().values))
    nc_file = pdlabel(nc_file, 'del', ['temp', 'sali', 'dens'])
    pdtonc(nc_file, inDIR+'/04_'+nc_files[i]+'.nc', time_chunk=12, depth_chunk=16)

#%% 04 to 05 steric height calculation for all datasets (EN4, ORAS5, SODA)
from functions import *
inDIR = ''
nc_files=['EN4', 'ORAS5', 'SODA']
for i in ll(nc_files):
    nc_file=nctopd(inDIR+'/04_'+nc_files[i]+'.nc')
    nc_file = pdlabel(nc_file, 'data', 'hei', steric_h(nc_file, 'vol', mt='tmean', ms='smean', dz='d_ran'))
    nc_file = pdlabel(nc_file, 'data', 'thei', steric_h(nc_file, 'tvol', mt='tmean', ms='smean', dz='d_ran'))
    nc_file = pdlabel(nc_file, 'data', 'shei', steric_h(nc_file, 'svol', mt='tmean', ms='smean', dz='d_ran'))
    nc_file = pdlabel(nc_file, 'del', ['vol', 'tvol', 'svol', 'tmean', 'smean'])
    pdtonc(nc_file, inDIR+'/05_'+nc_files[i]+'.nc', time_chunk=12, depth_chunk=16)

#%% 03 to 06 spice & heave trends + AR(1)-adjusted significance for all datasets (EN4, ORAS5, SODA)
from functions import *
inDIR = ''
nc_files=['EN4', 'ORAS5', 'SODA']
for i in ll(nc_files):
    nc_file=nctopd(inDIR+'/03_'+nc_files[i]+'.nc')
    heave_t, heave_s= heave_trend(nc_file, s='2004-01-01', f='2023-12-31', depth='m', rm_season=True)
    spice_t, spice_s= spice_trend(nc_file, s='2004-01-01', f='2023-12-31', depth='m', rm_season=True)
    nc_file = pdlabel(nc_file, 'data', 'heave_tr', heave_t)
    nc_file = pdlabel(nc_file, 'data', 'heave_sr', heave_s)
    nc_file = pdlabel(nc_file, 'data', 'spice_tr', spice_t)
    nc_file = pdlabel(nc_file, 'data', 'spice_sr', spice_s)
    nc_file = pdlabel(nc_file, 'data', 'trend_tr', litrend(nc_file, 'temp',s='2004-01-01', f='2023-12-31', rm_season=True))
    nc_file = pdlabel(nc_file, 'data', 'trend_sr', litrend(nc_file, 'sali',s='2004-01-01', f='2023-12-31', rm_season=True))

    hser_t, hser_s = heave_trend(nc_file, s='2004-01-01', f='2023-12-31', depth='m', rm_season=True, return_series=True)
    sser_t, sser_s = spice_trend(nc_file, s='2004-01-01', f='2023-12-31', depth='m', rm_season=True, return_series=True)
    for nm, da, rs in [('p_trend_tr', nc_file['temp'](), True), ('p_trend_sr', nc_file['sali'](), True), ('p_heave_tr', hser_t, False), ('p_heave_sr', hser_s, False), ('p_spice_tr', sser_t, False), ('p_spice_sr', sser_s, False)]:
        _, _, _, pv, _, _ = litrend(da.rename('x'), 'x', s='2004-01-01', f='2023-12-31', rm_season=rs, lonmin=50, lonmax=80, ar1=True, return_stats=True)
        nc_file = pdlabel(nc_file, 'data', nm, pv.compute())

    dens = np.nanmean(nc_file['dens']().sel(time=slice('2004-01-01','2023-12-31')).values, axis=0)
    nc_file = pdlabel(nc_file, 'del', ['dens'])
    nc_file = pdlabel(nc_file, 'data', 'dens', dens)
    nc_file = pdlabel(nc_file, 'del', ['temp', 'sali'])
    pdtonc(nc_file, inDIR+'/06_'+nc_files[i]+'.nc', time_chunk=6, depth_chunk=16, lat_chunk=90, lon_chunk=180)

#%% 03 to 07 spice & heave trends + OLS significance and standard errors (no AR(1)) for all datasets (ARGO, EN4, ORAS5, SODA)
from functions import *
inDIR = ''
nc_files=['ARGO', 'EN4', 'ORAS5', 'SODA']
for i in ll(nc_files):
    nc_file=nctopd(inDIR+'/03_'+nc_files[i]+'.nc')
    heave_t, heave_s= heave_trend(nc_file, s='2004-01-01', f='2023-12-31', depth='m', rm_season=True)
    spice_t, spice_s= spice_trend(nc_file, s='2004-01-01', f='2023-12-31', depth='m', rm_season=True)
    nc_file = pdlabel(nc_file, 'data', 'heave_tr', heave_t)
    nc_file = pdlabel(nc_file, 'data', 'heave_sr', heave_s)
    nc_file = pdlabel(nc_file, 'data', 'spice_tr', spice_t)
    nc_file = pdlabel(nc_file, 'data', 'spice_sr', spice_s)
    nc_file = pdlabel(nc_file, 'data', 'trend_tr', litrend(nc_file, 'temp',s='2004-01-01', f='2023-12-31', rm_season=True))
    nc_file = pdlabel(nc_file, 'data', 'trend_sr', litrend(nc_file, 'sali',s='2004-01-01', f='2023-12-31', rm_season=True))

    hser_t, hser_s = heave_trend(nc_file, s='2004-01-01', f='2023-12-31', depth='m', rm_season=True, return_series=True)
    sser_t, sser_s = spice_trend(nc_file, s='2004-01-01', f='2023-12-31', depth='m', rm_season=True, return_series=True)
    for nm, da, rs in [('p_trend_tr', nc_file['temp'](), True), ('p_trend_sr', nc_file['sali'](), True), ('p_heave_tr', hser_t, False), ('p_heave_sr', hser_s, False), ('p_spice_tr', sser_t, False), ('p_spice_sr', sser_s, False)]:
        _, _, _, pv, se, _ = litrend(da.rename('x'), 'x', s='2004-01-01', f='2023-12-31', rm_season=rs, lonmin=50, lonmax=80, ar1=False, return_stats=True)
        nc_file = pdlabel(nc_file, 'data', nm, pv.compute())
        nc_file = pdlabel(nc_file, 'data', nm.replace('p_', 'se_', 1), se.compute())

    dens = np.nanmean(nc_file['dens']().sel(time=slice('2004-01-01','2023-12-31')).values, axis=0)
    nc_file = pdlabel(nc_file, 'del', ['dens'])
    nc_file = pdlabel(nc_file, 'data', 'dens', dens)
    nc_file = pdlabel(nc_file, 'del', ['temp', 'sali'])
    tchunk = 12 if nc_files[i] == 'ARGO' else 6
    pdtonc(nc_file, inDIR+'/07_'+nc_files[i]+'.nc', time_chunk=tchunk, depth_chunk=16, lat_chunk=90, lon_chunk=180)

#%% 00 to 01 GRACE mascons + DUACS altimetry regridded to the ARGO grid
from functions import *
inDIR = ''

recent_t = pd.date_range(start='2004-01-01', end='2023-12-01', freq='MS')
ARGO = nctopd(inDIR+'/01_ARGO.nc')
alat = ARGO['lat']().values
alon = ARGO['lon']().values

Grace = nctopd(inDIR+'/00_GRACE.nc', drop_bounds=False)
tb = Grace['time_bounds']().values
g_lat = Grace['lat']().values
g_lon = Grace['lon']().values
g_ocean = 1.0 - Grace['land_mask']().values
g_sla, g_epoch = grace_month(Grace['lwe_thickness']().values, tb, recent_t, max_gap=2)
g_unc, _ = grace_month(Grace['uncertainty']().values, tb, recent_t, max_gap=2)

b0 = pd.DatetimeIndex(np.asarray(tb[:, 0], dtype='datetime64[ns]'))
b1 = pd.DatetimeIndex(np.asarray(tb[:, 1], dtype='datetime64[ns]'))
g_mon = pd.PeriodIndex(b0 + (b1 - b0)/2, freq='M').to_timestamp()
g_span = pd.Series((b1 - b0).days, index=g_mon).groupby(level=0).mean().reindex(recent_t).values

g_num, g_unum = regrid(data=g_sla*g_ocean, data1=g_unc*g_ocean, latfrom=g_lat, lonfrom=g_lon, latto=alat, lonto=alon, n_jobs=-1, backend='threading')
g_frac = regrid(data=g_ocean, latfrom=g_lat, lonfrom=g_lon, latto=alat, lonto=alon, n_jobs=-1, backend='threading')
g_den = np.where(g_frac >= 0.5, g_frac, np.nan)

out = pd.Series({'time': g_epoch, 'lat': alat, 'lon': alon, 'sla': g_num/g_den, 'unc': g_unum/g_den, 'ocean_frac': g_frac, 'span': g_span}, dtype=object)
pdtonc(out, inDIR+'/01_GRACE.nc', time_chunk=12)

Duacs = nctopd(inDIR+'/00_DUACS.nc')
d_time = pd.to_datetime(Duacs['time']().values).to_period('M').to_timestamp()
d_sel = (d_time >= recent_t[0]) & (d_time <= recent_t[-1])
d_ds = Duacs._ds.isel(time=np.where(d_sel)[0]).sel(latitude=slice(alat[0], alat[-1]), longitude=slice(alon[0], alon[-1]))

out = pd.Series({'time': d_time[d_sel], 'lat': alat, 'lon': alon, 'sla': d_ds['sla'].values*100.0}, dtype=object)
pdtonc(out, inDIR+'/01_DUACS.nc', time_chunk=12)
