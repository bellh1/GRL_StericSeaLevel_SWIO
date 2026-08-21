#%% Key Points
from functions import *
inDIR = ''

s0, f0 = '2004-01-01', '2023-12-31'
box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)
ARGO = nctopd(inDIR + '/05_ARGO.nc')

# Number_01 mid-depth halosteric compensation of thermosteric expansion, 2004-2023, from the trends as reported to two decimals
tsl = round(tr_trend(ARGO, 'thei', s0, f0, 300, 2000, box)[0], 2)
hsl = round(tr_trend(ARGO, 'shei', s0, f0, 300, 2000, box)[0], 2)
print('Number_01 mid-depth compensation |HSL|/|TSL| : %.0f %%' % (abs(hsl) / abs(tsl) * 100.0))

#%% Abstract
from functions import *
inDIR = ''

s0, f0 = '2004-01-01', '2023-12-31'
box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)
ARGO = nctopd(inDIR + '/05_ARGO.nc')

# Number_01 thermosteric trend, upper 300 m, 2004-2023
sl, se = tr_trend(ARGO, 'thei', s0, f0, 0, 300, box)
print('Number_01 TSL upper 300 m      : %+.2f +/- %.2f cm/decade' % (sl, se))

# Number_02 thermosteric trend, mid-depth 300-2,000 m, 2004-2023
sl, se = tr_trend(ARGO, 'thei', s0, f0, 300, 2000, box)
print('Number_02 TSL mid-depth        : %+.2f +/- %.2f cm/decade' % (sl, se))

# Number_03 halosteric trend, upper 300 m, 2004-2023
sl, se = tr_trend(ARGO, 'shei', s0, f0, 0, 300, box)
print('Number_03 HSL upper 300 m      : %+.2f +/- %.2f cm/decade' % (sl, se))

# Number_04 halosteric trend, mid-depth 300-2,000 m, 2004-2023
sl, se = tr_trend(ARGO, 'shei', s0, f0, 300, 2000, box)
print('Number_04 HSL mid-depth        : %+.2f +/- %.2f cm/decade' % (sl, se))

# Number_05 mid-depth halosteric compensation of thermosteric expansion, from the trends as reported to two decimals
tsl = round(tr_trend(ARGO, 'thei', s0, f0, 300, 2000, box)[0], 2)
hsl = round(tr_trend(ARGO, 'shei', s0, f0, 300, 2000, box)[0], 2)
print('Number_05 mid-depth compensation: %.0f %%' % (abs(hsl) / abs(tsl) * 100.0))

A7 = nctopd(inDIR + '/07_ARGO.nc')

# Number_06 mid-depth temperature heave-to-spice partition
h = box_layer_integral(A7, 'heave_tr', box, 300, 2000)
s = box_layer_integral(A7, 'spice_tr', box, 300, 2000)
rh = abs(h) / (abs(h) + abs(s)) * 100.0
print('Number_06 T heave:spice        : %.0f:%.0f' % (rh, 100.0 - rh))

# Number_07 mid-depth salinity heave-to-spice partition
h = box_layer_integral(A7, 'heave_sr', box, 300, 2000)
s = box_layer_integral(A7, 'spice_sr', box, 300, 2000)
rh = abs(h) / (abs(h) + abs(s)) * 100.0
print('Number_07 S heave:spice        : %.0f:%.0f' % (rh, 100.0 - rh))

#%% Plain Language Summary
from functions import *
inDIR = ''

s0, f0 = '2004-01-01', '2023-12-31'
box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)
ARGO = nctopd(inDIR + '/05_ARGO.nc')

# Number_01 mid-depth halosteric compensation of thermosteric expansion, 2004-2023, from the trends as reported to two decimals
tsl = round(tr_trend(ARGO, 'thei', s0, f0, 300, 2000, box)[0], 2)
hsl = round(tr_trend(ARGO, 'shei', s0, f0, 300, 2000, box)[0], 2)
print('Number_01 mid-depth compensation : %.0f %%' % (abs(hsl) / abs(tsl) * 100.0))

#%% Data 2.1
from functions import *
inDIR = ''

s0, f0 = '2004-01-01', '2023-12-31'
box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)

Grace = nctopd(inDIR + '/01_GRACE.nc')
gt = pd.DatetimeIndex(pd.PeriodIndex(pd.to_datetime(Grace['time']().values), freq='M').to_timestamp())
span = np.asarray(Grace['span']().values, dtype=float)
sla = Grace['sla']().assign_coords(time=gt)
has = np.isfinite(sla.values).any(axis=(1, 2))
obs = np.isfinite(span)
sOM = bser(sla.isel(time=np.where(has)[0]).rename('sla'), 'sla', s0, f0, box)
mobs = pd.Series(obs, index=gt)

# Number_01 ocean-mass equivalent sea level, all months including gap-filled
txt, n = fit_series(sOM, s0, f0)
print('Number_01 OMESL, all months             : %s cm/decade  (n = %d)' % (txt, n))

# Number_02 ocean-mass equivalent sea level, GRACE solution months only
txt, n = fit_series(sOM, s0, f0, mobs)
print('Number_02 OMESL, GRACE solutions only   : %s cm/decade  (n = %d)' % (txt, n))

#%% Methods 2.2
from functions import *
inDIR = ''

s0, f0 = '2004-01-01', '2023-12-31'
box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)
A5 = nctopd(inDIR + '/05_ARGO.nc')
A7 = nctopd(inDIR + '/07_ARGO.nc')

# Number_01 thermosteric-halosteric cross term, largest absolute value over the three layers
cross = []
for d1, d2 in [(0, 300), (300, 2000), (0, 2000)]:
    ssl = tr_trend(A5, 'hei', s0, f0, d1, d2, box)[0]
    tsl = tr_trend(A5, 'thei', s0, f0, d1, d2, box)[0]
    hsl = tr_trend(A5, 'shei', s0, f0, d1, d2, box)[0]
    cross.append(abs(ssl - (tsl + hsl)))
print('Number_01 largest cross term            : %.4f cm/decade' % max(cross))

# Number_02 mid-depth temperature, heave plus spice as a fraction of the total trend
h = box_layer_integral(A7, 'heave_tr', box, 300, 2000)
s = box_layer_integral(A7, 'spice_tr', box, 300, 2000)
t = box_layer_integral(A7, 'trend_tr', box, 300, 2000)
print('Number_02 T (heave+spice)/total         : %.1f %% (departure %.1f %%)' % ((h + s) / t * 100.0, abs((h + s) / t * 100.0 - 100.0)))

# Number_03 mid-depth salinity, heave plus spice as a fraction of the total trend
h = box_layer_integral(A7, 'heave_sr', box, 300, 2000)
s = box_layer_integral(A7, 'spice_sr', box, 300, 2000)
t = box_layer_integral(A7, 'trend_sr', box, 300, 2000)
print('Number_03 S (heave+spice)/total         : %.1f %% (departure %.1f %%)' % ((h + s) / t * 100.0, abs((h + s) / t * 100.0 - 100.0)))

sTSL = bser(A5, 'thei', s0, f0, box, 300, 2000)
sHSL = bser(A5, 'shei', s0, f0, box, 300, 2000)

# Number_04 AR(1)-adjusted mid-depth thermosteric interval
sl, ci = ar1_ci(sTSL, s0, f0)
print('Number_04 TSL mid-depth, AR(1)          : %+.2f +/- %.2f cm/decade' % (sl, ci))

# Number_05 AR(1)-adjusted mid-depth halosteric interval
sl, ci = ar1_ci(sHSL, s0, f0)
print('Number_05 HSL mid-depth, AR(1)          : %+.2f +/- %.2f cm/decade' % (sl, ci))

A3 = nctopd(inDIR + '/03_ARGO.nc')
A3._ds = A3._ds.sel(lat=slice(box['latmin'], box['latmax']), lon=slice(box['lonmin'], box['lonmax']))
[setattr(v, '_ds', A3._ds) for _, v in A3.items() if hasattr(v, '_ds')]
hser_t, hser_s = heave_trend(A3, s=s0, f=f0, depth='m', rm_season=True, return_series=True)
sser_t, sser_s = spice_trend(A3, s=s0, f=f0, depth='m', rm_season=True, return_series=True)
ser = {'TSL': sTSL, 'HSL': sHSL, 'T_heave': bser(hser_t.rename('x'), 'x', s0, f0, box, 300, 2000, rs=False), 'T_spice': bser(sser_t.rename('x'), 'x', s0, f0, box, 300, 2000, rs=False), 'S_heave': bser(hser_s.rename('x'), 'x', s0, f0, box, 300, 2000, rs=False), 'S_spice': bser(sser_s.rename('x'), 'x', s0, f0, box, 300, 2000, rs=False)}

est, lo, hi, boot, info = mbb(ser, nboot=10000, stats_fn=mbb_ratios, seed=1234)

# Number_06 moving-block bootstrap interval for the mid-depth compensation
print('Number_06 MBB 95%% compensation          : %.0f-%.0f %%' % (lo['comp_HSL_over_TSL_%'], hi['comp_HSL_over_TSL_%']))

# Number_07 moving-block bootstrap interval for the temperature spice fraction
print('Number_07 MBB 95%% T spice fraction      : %.0f-%.0f %%' % (lo['T_spice_%'], hi['T_spice_%']))

# Number_08 moving-block bootstrap interval for the salinity spice fraction
print('Number_08 MBB 95%% S spice fraction      : %.0f-%.0f %%' % (lo['S_spice_%'], hi['S_spice_%']))

# Number_09 moving-block bootstrap interval for the salinity heave fraction
print('Number_09 MBB 95%% S heave fraction      : %.1f-%.0f %%' % (lo['S_heave_%'], hi['S_heave_%']))

#%% Result 3.1
from functions import *
inDIR = ''

s0, f0 = '2004-01-01', '2023-12-31'
box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)
ARGO = nctopd(inDIR + '/05_ARGO.nc')

Duacs = nctopd(inDIR + '/01_DUACS.nc')
Grace = nctopd(inDIR + '/01_GRACE.nc')
G = Grace['sla']()
G = G.assign_coords(time=pd.PeriodIndex(pd.to_datetime(G['time'].values), freq='M').to_timestamp())
G = G.isel(time=np.where(np.isfinite(G.values).any(axis=(1, 2)))[0]).rename('sla')
sSL = bser(Duacs, 'sla', s0, f0, box)
sOM = bser(G, 'sla', s0, f0, box)
sRES = sSL - sOM

# Number_01 ocean-mass equivalent sea level from GRACE/GRACE-FO
print('Number_01 OMESL                        : %s cm/decade' % fit_series(sOM, s0, f0)[0])

# Number_02 total sea level from satellite altimetry
print('Number_02 SL altimetry                 : %s cm/decade' % fit_series(sSL, s0, f0)[0])

# Number_03 SL minus OMESL residual
print('Number_03 SL - OMESL residual          : %s cm/decade' % fit_series(sRES, s0, f0)[0])

# Number_04 upper 2,000 m steric sea level, MOAA GPV v2
print('Number_04 SSL upper 2,000 m            : %s cm/decade' % fit_series(bser(ARGO, 'hei', s0, f0, box, 0, 2000), s0, f0)[0])

# Number_05 residual left unexplained after the upper 2,000 m steric term, across the four products
rr = []
for nm in ['ARGO', 'EN4', 'ORAS5', 'SODA']:
    A = nctopd(inDIR + '/05_' + nm + '.nc')
    rr.append(float(fit_series(sRES - bser(A, 'hei', s0, f0, box, 0, 2000), s0, f0)[0].split(' ±')[0]))
print('Number_05 unexplained residual range   : %.2f to %.2f cm/decade' % (min(rr), max(rr)))

# Number_06 upper 2,000 m steric trend
print('Number_06 SSL upper 2,000 m            : %+.2f cm/decade' % tr_trend(ARGO, 'hei', s0, f0, 0, 2000, box)[0])

# Number_07 upper 2,000 m thermosteric trend
print('Number_07 TSL upper 2,000 m            : %+.2f cm/decade' % tr_trend(ARGO, 'thei', s0, f0, 0, 2000, box)[0])

# Number_08 upper 2,000 m halosteric trend
print('Number_08 HSL upper 2,000 m            : %+.2f cm/decade' % tr_trend(ARGO, 'shei', s0, f0, 0, 2000, box)[0])

# Number_09 thermosteric trend, upper 300 m
t_top = round(tr_trend(ARGO, 'thei', s0, f0, 0, 300, box)[0], 2)
print('Number_09 TSL upper 300 m              : %+.2f cm/decade' % t_top)

# Number_10 thermosteric trend, mid-depth
t_bot = round(tr_trend(ARGO, 'thei', s0, f0, 300, 2000, box)[0], 2)
print('Number_10 TSL mid-depth                : %+.2f cm/decade' % t_bot)

# Number_11 halosteric trend, upper 300 m
s_top = round(tr_trend(ARGO, 'shei', s0, f0, 0, 300, box)[0], 2)
print('Number_11 HSL upper 300 m              : %+.2f cm/decade' % s_top)

# Number_12 upper-ocean halosteric compensation, from the trends as reported to two decimals
print('Number_12 upper 300 m compensation     : %.0f %%' % (abs(s_top) / abs(t_top) * 100.0))

# Number_13 halosteric trend, mid-depth
s_bot = round(tr_trend(ARGO, 'shei', s0, f0, 300, 2000, box)[0], 2)
print('Number_13 HSL mid-depth                : %+.2f cm/decade' % s_bot)

# Number_14 mid-depth halosteric compensation, from the trends as reported to two decimals
print('Number_14 mid-depth compensation       : %.0f %%' % (abs(s_bot) / abs(t_bot) * 100.0))

# Number_15 ratio of mid-depth to upper-ocean halosteric contraction, from the trends as reported to two decimals
print('Number_15 HSL mid / HSL upper          : factor %.1f' % (abs(s_bot) / abs(s_top)))

# Number_16 steric sea level, mid-depth
print('Number_16 SSL mid-depth                : %+.2f cm/decade' % tr_trend(ARGO, 'hei', s0, f0, 300, 2000, box)[0])

# Number_17 steric sea level, upper 300 m
sl, se = tr_trend(ARGO, 'hei', s0, f0, 0, 300, box)
print('Number_17 SSL upper 300 m              : %+.2f +/- %.2f cm/decade' % (sl, se))

# Number_18 mid-depth halosteric trend over the period shared with Huang et al. (2024)
print('Number_18 HSL mid-depth, 2004-2021     : %+.2f cm/decade' % tr_trend(ARGO, 'shei', '2004-01-01', '2021-12-31', 300, 2000, box)[0])

V1 = nctopd(inDIR + '/05_MOAAv1.nc')

# Number_19 upper 2,000 m steric trend in the configuration of Huang et al. (2024)
print('Number_19 SSL 0-2,000 m, v1 2002-2021  : %+.2f cm/decade' % tr_trend(V1, 'hei', '2002-01-01', '2021-12-31', 0, 2000, box)[0])

# Number_20 upper 2,000 m halosteric trend in the same configuration
sl, se = tr_trend(V1, 'shei', '2002-01-01', '2021-12-31', 0, 2000, box)
print('Number_20 HSL 0-2,000 m, v1 2002-2021  : %+.2f +/- %.2f cm/decade' % (sl, se))

#%% Result 3.2
from functions import *
inDIR = ''

s0, f0 = '2004-01-01', '2023-12-31'
box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)
A3 = nctopd(inDIR + '/03_ARGO.nc')
A7 = nctopd(inDIR + '/07_ARGO.nc')

# Number_01 mid-depth mean conservative temperature trend
mean_tr = box_layer_mean(A7, 'trend_tr', box, 300, 2000)
sl, _, _, _, se, _ = litrend(A3, 'temp', s=s0, f=f0, rm_season=True, dmin=300, dmax=2000, ar1=False, return_stats=True, **box)
h_eff = float(sl) / mean_tr
print('Number_01 mid-depth mean T trend       : (%.2f +/- %.2f) x10^-1 degC/decade' % (mean_tr * 1e1, 2.0 * float(se) / h_eff * 1e1))

# Number_02 mid-depth mean absolute salinity trend
mean_sr = box_layer_mean(A7, 'trend_sr', box, 300, 2000)
sl, _, _, _, se, _ = litrend(A3, 'sali', s=s0, f=f0, rm_season=True, dmin=300, dmax=2000, ar1=False, return_stats=True, **box)
h_eff = float(sl) / mean_sr
print('Number_02 mid-depth mean S trend       : (%.2f +/- %.2f) x10^-2 g/kg/decade' % (mean_sr * 1e2, 2.0 * float(se) / h_eff * 1e2))

# Number_03 mid-depth salinity heave-to-spice partition
h = box_layer_integral(A7, 'heave_sr', box, 300, 2000)
s = box_layer_integral(A7, 'spice_sr', box, 300, 2000)
rh = abs(h) / (abs(h) + abs(s)) * 100.0
print('Number_03 S heave:spice                : %.0f:%.0f' % (rh, 100.0 - rh))

# Number_04 mid-depth temperature heave-to-spice partition
h = box_layer_integral(A7, 'heave_tr', box, 300, 2000)
s = box_layer_integral(A7, 'spice_tr', box, 300, 2000)
rh = abs(h) / (abs(h) + abs(s)) * 100.0
print('Number_04 T heave:spice                : %.0f:%.0f' % (rh, 100.0 - rh))

#%% Discussion 4
from functions import *
inDIR = ''

s0, f0 = '2004-01-01', '2023-12-31'
box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)
ARGO = nctopd(inDIR + '/05_ARGO.nc')

# Number_01 mid-depth halosteric compensation of thermosteric expansion, 2004-2023, from the trends as reported to two decimals
tsl = round(tr_trend(ARGO, 'thei', s0, f0, 300, 2000, box)[0], 2)
hsl = round(tr_trend(ARGO, 'shei', s0, f0, 300, 2000, box)[0], 2)
print('Number_01 mid-depth compensation       : %.0f %%' % (abs(hsl) / abs(tsl) * 100.0))

# Number_02 mid-depth halosteric trend over the first decade
sl, se = tr_trend(ARGO, 'shei', '2004-01-01', '2013-12-31', 300, 2000, box)
print('Number_02 HSL mid-depth, 2004-2013     : %+.2f +/- %.2f cm/decade' % (sl, se))

# Number_03 mid-depth halosteric trend over the second decade
sl, se = tr_trend(ARGO, 'shei', '2014-01-01', '2023-12-31', 300, 2000, box)
print('Number_03 HSL mid-depth, 2014-2023     : %+.2f +/- %.2f cm/decade' % (sl, se))

#%% Conclusion 5
from functions import *
inDIR = ''

s0, f0 = '2004-01-01', '2023-12-31'
box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)
ARGO = nctopd(inDIR + '/05_ARGO.nc')
A7 = nctopd(inDIR + '/07_ARGO.nc')

# Number_01 mid-depth halosteric compensation of thermosteric expansion, 2004-2023, from the trends as reported to two decimals
tsl = round(tr_trend(ARGO, 'thei', s0, f0, 300, 2000, box)[0], 2)
hsl = round(tr_trend(ARGO, 'shei', s0, f0, 300, 2000, box)[0], 2)
print('Number_01 mid-depth compensation       : %.0f %%' % (abs(hsl) / abs(tsl) * 100.0))

# Number_02 mid-depth salinity heave-to-spice partition
h = box_layer_integral(A7, 'heave_sr', box, 300, 2000)
s = box_layer_integral(A7, 'spice_sr', box, 300, 2000)
rh = abs(h) / (abs(h) + abs(s)) * 100.0
print('Number_02 S heave:spice                : %.0f:%.0f' % (rh, 100.0 - rh))
