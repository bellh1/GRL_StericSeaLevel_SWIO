#%% Comment 3-1
from functions import *
inDIR = ''

box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)
ARGO = nctopd(inDIR + '/05_ARGO.nc')

longw = [('2004-2021', '2004-01-01', '2021-12-31'), ('2004-2023', '2004-01-01', '2023-12-31'), ('2004-2024', '2004-01-01', '2024-01-31')]

# Number_01 mid-depth thermosteric trend over the three longer windows
for pn, ps, pf in longw:
    print('Number_01 TSL mid-depth %s   : %+.2f +/- %.2f cm/decade' % ((pn,) + tr_trend(ARGO, 'thei', ps, pf, 300, 2000, box)))

# Number_02 mid-depth halosteric trend over the three longer windows
for pn, ps, pf in longw:
    print('Number_02 HSL mid-depth %s   : %+.2f +/- %.2f cm/decade' % ((pn,) + tr_trend(ARGO, 'shei', ps, pf, 300, 2000, box)))

# Number_03 mid-depth compensation over the three longer windows
for pn, ps, pf in longw:
    t = round(tr_trend(ARGO, 'thei', ps, pf, 300, 2000, box)[0], 2)
    h = round(tr_trend(ARGO, 'shei', ps, pf, 300, 2000, box)[0], 2)
    print('Number_03 compensation %s    : %.0f %%' % (pn, abs(h) / abs(t) * 100.0))

# Number_04 mid-depth halosteric trend over the first decade
print('Number_04 HSL mid-depth 2004-2013 : %+.2f +/- %.2f cm/decade' % tr_trend(ARGO, 'shei', '2004-01-01', '2013-12-31', 300, 2000, box))

# Number_05 mid-depth halosteric trend over the second decade
print('Number_05 HSL mid-depth 2014-2023 : %+.2f +/- %.2f cm/decade' % tr_trend(ARGO, 'shei', '2014-01-01', '2023-12-31', 300, 2000, box))

# Number_06 upper 300 m steric trend in the two halves and over the full record, for footnote a
for pn, ps, pf in [('2004-2013', '2004-01-01', '2013-12-31'), ('2014-2023', '2014-01-01', '2023-12-31'), ('2004-2023', '2004-01-01', '2023-12-31')]:
    print('Number_06 SSL upper 300 m %s : %+.2f +/- %.2f cm/decade' % ((pn,) + tr_trend(ARGO, 'hei', ps, pf, 0, 300, box)))

#%% Comment 3-2
from functions import *
inDIR = ''

box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)
mean_names = ['ARGO', 'EN4', 'ORAS5', 'SODA']

# Number_01 ensemble-mean halosteric trend, upper 300 m, 2004-2023
print('Number_01 HSL upper 300 m, mean   : %+.2f +/- %.2f cm/decade' % ensemble_mean([load(x, inDIR) for x in mean_names], 'shei', '2004-01-01', '2023-12-31', 0, 300))

# Number_02 ensemble-mean halosteric trend, mid-depth, 2004-2023
print('Number_02 HSL mid-depth, mean     : %+.2f +/- %.2f cm/decade' % ensemble_mean([load(x, inDIR) for x in mean_names], 'shei', '2004-01-01', '2023-12-31', 300, 2000))

# Number_03 ensemble-mean thermosteric trend, mid-depth, 2004-2023
print('Number_03 TSL mid-depth, mean     : %+.2f +/- %.2f cm/decade' % ensemble_mean([load(x, inDIR) for x in mean_names], 'thei', '2004-01-01', '2023-12-31', 300, 2000))

# Number_04 ensemble-mean upper 2,000 m steric trend, 2004-2021
m0 = ensemble_mean([load(x, inDIR) for x in mean_names], 'hei', '2004-01-01', '2021-12-31', 0, 2000)
print('Number_04 SSL 0-2,000 m, mean     : %+.2f +/- %.2f cm/decade' % m0)

# Number_05 MOAA GPV v2 upper 2,000 m steric trend, 2004-2021
m1 = tr_trend(load('ARGO', inDIR), 'hei', '2004-01-01', '2021-12-31', 0, 2000, box)
print('Number_05 SSL 0-2,000 m, v2 04-21 : %+.2f +/- %.2f cm/decade' % m1)

# Number_06 MOAA GPV v1 upper 2,000 m steric trend, 2004-2021
m2 = tr_trend(load('MOAAv1', inDIR), 'hei', '2004-01-01', '2021-12-31', 0, 2000, box)
print('Number_06 SSL 0-2,000 m, v1 04-21 : %+.2f +/- %.2f cm/decade' % m2)

# Number_07 MOAA GPV v1 upper 2,000 m steric trend, 2002-2021
m3 = tr_trend(load('MOAAv1', inDIR), 'hei', '2002-01-01', '2021-12-31', 0, 2000, box)
print('Number_07 SSL 0-2,000 m, v1 02-21 : %+.2f +/- %.2f cm/decade' % m3)

# Number_08 reconciliation ladder increments, one element changed per step
v = [m0[0], m1[0], m2[0], m3[0]]
for lbl, i in [('four-product mean to v2', 1), ('v2 to v1, same window', 2), ('2004 to 2002 start', 3)]:
    print('Number_08 increment, %-24s: %+.2f cm/decade' % (lbl, v[i] - v[i - 1]))
print('Number_08 residual vs Huang et al. 1.20      : %+.2f cm/decade' % (v[3] - 1.20))

# Number_09 MOAA GPV v1 upper 2,000 m halosteric trend, 2002-2021
print('Number_09 HSL 0-2,000 m, v1 02-21 : %+.2f +/- %.2f cm/decade' % tr_trend(load('MOAAv1', inDIR), 'shei', '2002-01-01', '2021-12-31', 0, 2000, box))

# Number_10 MOAA GPV v1 mid-depth halosteric trend, 2002-2021
print('Number_10 HSL mid-depth, v1 02-21 : %+.2f +/- %.2f cm/decade' % tr_trend(load('MOAAv1', inDIR), 'shei', '2002-01-01', '2021-12-31', 300, 2000, box))

#%% Comment 3-4
from functions import *
inDIR = ''

s0, f0 = '2004-01-01', '2023-12-31'
box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)

Duacs = nctopd(inDIR + '/01_DUACS.nc')
Grace = nctopd(inDIR + '/01_GRACE.nc')
G = Grace['sla']()
G = G.assign_coords(time=pd.PeriodIndex(pd.to_datetime(G['time'].values), freq='M').to_timestamp())
G = G.isel(time=np.where(np.isfinite(G.values).any(axis=(1, 2)))[0]).rename('sla')
sSL = bser(Duacs, 'sla', s0, f0, box)
sOM = bser(G, 'sla', s0, f0, box)
sRES = sSL - sOM

# Number_01 total sea level from satellite altimetry
print('Number_01 SL altimetry            : %s cm/decade' % fit_series(sSL, s0, f0)[0])

# Number_02 ocean-mass equivalent sea level
print('Number_02 OMESL                   : %s cm/decade' % fit_series(sOM, s0, f0)[0])

# Number_03 SL minus OMESL residual
print('Number_03 SL - OMESL residual     : %s cm/decade' % fit_series(sRES, s0, f0)[0])

ARGO = nctopd(inDIR + '/05_ARGO.nc')

# Number_04 steric sea level, upper 300 m
print('Number_04 SSL upper 300 m         : %s cm/decade' % fit_series(bser(ARGO, 'hei', s0, f0, box, 0, 300), s0, f0)[0])

# Number_05 steric sea level, mid-depth
print('Number_05 SSL mid-depth           : %s cm/decade' % fit_series(bser(ARGO, 'hei', s0, f0, box, 300, 2000), s0, f0)[0])

# Number_06 steric sea level, upper 2,000 m
print('Number_06 SSL upper 2,000 m       : %s cm/decade' % fit_series(bser(ARGO, 'hei', s0, f0, box, 0, 2000), s0, f0)[0])

# Number_07 residual left unexplained after the upper 2,000 m steric term, across the four products
rr = []
for nm in ['ARGO', 'EN4', 'ORAS5', 'SODA']:
    A = nctopd(inDIR + '/05_' + nm + '.nc')
    rr.append(float(fit_series(sRES - bser(A, 'hei', s0, f0, box, 0, 2000), s0, f0)[0].split(' ±')[0]))
print('Number_07 unexplained residual    : %.2f to %.2f cm/decade' % (min(rr), max(rr)))

#%% Comment 3-5
from functions import *
inDIR = ''

box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)
A7 = nctopd(inDIR + '/07_ARGO.nc')

# Number_01 mid-depth temperature heave-to-spice partition
h = box_layer_integral(A7, 'heave_tr', box, 300, 2000)
s = box_layer_integral(A7, 'spice_tr', box, 300, 2000)
rh = abs(h) / (abs(h) + abs(s)) * 100.0
print('Number_01 T heave:spice           : %.0f:%.0f' % (rh, 100.0 - rh))

# Number_02 mid-depth salinity heave-to-spice partition
h = box_layer_integral(A7, 'heave_sr', box, 300, 2000)
s = box_layer_integral(A7, 'spice_sr', box, 300, 2000)
rh = abs(h) / (abs(h) + abs(s)) * 100.0
print('Number_02 S heave:spice           : %.0f:%.0f' % (rh, 100.0 - rh))

#%% Comment 3-7
from functions import *
inDIR = ''

s0, f0 = '2004-01-01', '2023-12-31'
box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)
d1, d2 = 300, 2000
A5 = nctopd(inDIR + '/05_ARGO.nc')
A7 = nctopd(inDIR + '/07_ARGO.nc')

# Number_01 thermosteric-halosteric cross term, largest absolute value over the three layers
cross = []
for a, b in [(0, 300), (300, 2000), (0, 2000)]:
    cross.append(abs(tr_trend(A5, 'hei', s0, f0, a, b, box)[0] - tr_trend(A5, 'thei', s0, f0, a, b, box)[0] - tr_trend(A5, 'shei', s0, f0, a, b, box)[0]))
print('Number_01 largest cross term      : %.4f cm/decade' % max(cross))

# Number_02 mid-depth temperature, heave plus spice as a fraction of the total trend
h = box_layer_integral(A7, 'heave_tr', box, d1, d2)
s = box_layer_integral(A7, 'spice_tr', box, d1, d2)
t = box_layer_integral(A7, 'trend_tr', box, d1, d2)
print('Number_02 T (heave+spice)/total   : %.1f %%' % ((h + s) / t * 100.0))

# Number_03 mid-depth salinity, heave plus spice as a fraction of the total trend
h = box_layer_integral(A7, 'heave_sr', box, d1, d2)
s = box_layer_integral(A7, 'spice_sr', box, d1, d2)
t = box_layer_integral(A7, 'trend_sr', box, d1, d2)
print('Number_03 S (heave+spice)/total   : %.1f %%' % ((h + s) / t * 100.0))

sTSL = bser(A5, 'thei', s0, f0, box, d1, d2)
sHSL = bser(A5, 'shei', s0, f0, box, d1, d2)

# Number_04 AR(1)-adjusted mid-depth thermosteric interval
print('Number_04 TSL mid-depth, AR(1)    : %+.2f +/- %.2f cm/decade' % ar1_ci(sTSL, s0, f0))

# Number_05 AR(1)-adjusted mid-depth halosteric interval
print('Number_05 HSL mid-depth, AR(1)    : %+.2f +/- %.2f cm/decade' % ar1_ci(sHSL, s0, f0))

A3 = nctopd(inDIR + '/03_ARGO.nc')
A3._ds = A3._ds.sel(lat=slice(box['latmin'], box['latmax']), lon=slice(box['lonmin'], box['lonmax']))
[setattr(v, '_ds', A3._ds) for _, v in A3.items() if hasattr(v, '_ds')]
hser_t, hser_s = heave_trend(A3, s=s0, f=f0, depth='m', rm_season=True, return_series=True)
sser_t, sser_s = spice_trend(A3, s=s0, f=f0, depth='m', rm_season=True, return_series=True)
ser = {'TSL': sTSL, 'HSL': sHSL, 'T_heave': bser(hser_t.rename('x'), 'x', s0, f0, box, d1, d2, rs=False), 'T_spice': bser(sser_t.rename('x'), 'x', s0, f0, box, d1, d2, rs=False), 'S_heave': bser(hser_s.rename('x'), 'x', s0, f0, box, d1, d2, rs=False), 'S_spice': bser(sser_s.rename('x'), 'x', s0, f0, box, d1, d2, rs=False)}
est, lo, hi, boot, info = mbb(ser, nboot=10000, stats_fn=mbb_ratios, seed=1234)

# Number_06 moving-block bootstrap interval for the mid-depth compensation
print('Number_06 MBB compensation        : %.1f  [%.1f, %.1f] %%' % (est['comp_HSL_over_TSL_%'], lo['comp_HSL_over_TSL_%'], hi['comp_HSL_over_TSL_%']))

# Number_07 moving-block bootstrap interval for the temperature heave fraction
print('Number_07 MBB T heave             : %.1f  [%.1f, %.1f] %%' % (est['T_heave_%'], lo['T_heave_%'], hi['T_heave_%']))

# Number_08 moving-block bootstrap interval for the temperature spice fraction
print('Number_08 MBB T spice             : %.1f  [%.1f, %.1f] %%' % (est['T_spice_%'], lo['T_spice_%'], hi['T_spice_%']))

# Number_09 moving-block bootstrap interval for the salinity heave fraction
print('Number_09 MBB S heave             : %.1f  [%.1f, %.1f] %%' % (est['S_heave_%'], lo['S_heave_%'], hi['S_heave_%']))

# Number_10 moving-block bootstrap interval for the salinity spice fraction
print('Number_10 MBB S spice             : %.1f  [%.1f, %.1f] %%' % (est['S_spice_%'], lo['S_spice_%'], hi['S_spice_%']))

# Number_11 salinity spice fraction minus temperature spice fraction, and its bootstrap support
d = np.asarray(boot['spiceS_minus_spiceT_pp'], dtype=float)
d = d[np.isfinite(d)]
q = np.percentile(d, [2.5, 97.5])
print('Number_11 S spice - T spice       : %.1f pp  [%.1f, %.1f]  one-sided p = %.2f' % (est['spiceS_minus_spiceT_pp'], q[0], q[1], float((d <= 0).mean())))

Grace = nctopd(inDIR + '/01_GRACE.nc')
Duacs = nctopd(inDIR + '/01_DUACS.nc')
gt = pd.DatetimeIndex(pd.PeriodIndex(pd.to_datetime(Grace['time']().values), freq='M').to_timestamp())
span = np.asarray(Grace['span']().values, dtype=float)
sla = Grace['sla']().assign_coords(time=gt)
has = np.isfinite(sla.values).any(axis=(1, 2))
obs = np.isfinite(span)
runs = grace_gap_runs(obs)

# Number_12 GRACE/GRACE-FO month counts and the longest gap
print('Number_12 months on the axis      : %d' % len(gt))
print('Number_12 months with a solution  : %d' % int(obs.sum()))
print('Number_12 months interpolated     : %d' % int((has & ~obs).sum()))
print('Number_12 longest gap             : %s to %s (%d months)' % (gt[runs[0][0]].strftime('%Y-%m'), gt[runs[0][1]].strftime('%Y-%m'), runs[0][1] - runs[0][0] + 1))

gSL = bser(Duacs['sla']().rename('sla'), 'sla', s0, f0, box)
gOM = bser(sla.isel(time=np.where(has)[0]).rename('sla'), 'sla', s0, f0, box)
gRE = gSL - gOM
mobs = pd.Series(obs, index=gt)

# Number_13 ocean-mass trend with and without the interpolated months
print('Number_13 OMESL, gap-filled       : %s  (n = %d)' % fit_series(gOM, s0, f0))
print('Number_13 OMESL, solutions only   : %s  (n = %d)' % fit_series(gOM, s0, f0, mobs))

# Number_14 residual trend with and without the interpolated months
print('Number_14 residual, gap-filled    : %s  (n = %d)' % fit_series(gRE, s0, f0))
print('Number_14 residual, solutions only: %s  (n = %d)' % fit_series(gRE, s0, f0, mobs))

V1 = nctopd(inDIR + '/05_MOAAv1.nc')

# Number_15 mid-depth halosteric trend in v1 and v2 over the windows quoted in the response
for lbl, D in [('v2', A5), ('v1', V1)]:
    for pn, ws, wf in [('2004-2021', '2004-01-01', '2021-12-31'), ('2004-2022', '2004-01-01', '2022-12-31'), ('2004-2013', '2004-01-01', '2013-12-31'), ('2014-2022', '2014-01-01', '2022-12-31')]:
        print('Number_15 HSL mid-depth %s %s : %+.2f +/- %.2f cm/decade' % ((lbl, pn) + tr_trend(D, 'shei', ws, wf, d1, d2, box)))

# Number_16 heave-to-spice partition of the mid-depth trends by product version and window
for lbl, fname, ws, wf, pn in [('MOAA GPV v2', 'ARGO', '2004-01-01', '2023-12-31', '2004-2023'), ('MOAA GPV v2', 'ARGO', '2004-01-01', '2022-12-31', '2004-2022'), ('MOAA GPV v1', 'MOAAv1', '2004-01-01', '2022-12-31', '2004-2022')]:
    B = nctopd(inDIR + '/03_' + fname + '.nc')
    B._ds = B._ds.sel(lat=slice(box['latmin'], box['latmax']), lon=slice(box['lonmin'], box['lonmax']))
    [setattr(v, '_ds', B._ds) for _, v in B.items() if hasattr(v, '_ds')]
    ht, hs = heave_trend(B, s=ws, f=wf, depth='m', rm_season=True, return_series=True)
    st, ss = spice_trend(B, s=ws, f=wf, depth='m', rm_season=True, return_series=True)
    vals = []
    for da in [ht, st, hs, ss]:
        y = bser(da.rename('x'), 'x', ws, wf, box, d1, d2, rs=False)
        Y = xr.DataArray(y.values, dims=('time',), coords={'time': pd.DatetimeIndex(y.index)}, name='y')
        vals.append(float(litrend(Y, 'y', s=ws, f=wf, rm_season=False, ar1=False, return_stats=True)[0]))
    fT = abs(vals[0]) / (abs(vals[0]) + abs(vals[1])) * 100.0
    fS = abs(vals[2]) / (abs(vals[2]) + abs(vals[3])) * 100.0
    print('Number_16 %s %s  T %.0f:%.0f   S %.0f:%.0f' % (lbl, pn, fT, 100 - fT, fS, 100 - fS))
