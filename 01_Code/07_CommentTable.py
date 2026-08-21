#%% Table_R1 Window sensitivity of SSL, TSL, HSL by layer
from functions import *
inDIR = ''
outDIR = ''

ARGO = nctopd(inDIR + '/05_ARGO.nc')
box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)

periods = [('2004-2021', '2004-01-01', '2021-12-31'), ('2004-2023', '2004-01-01', '2023-12-31'), ('2004-2024', '2004-01-01', '2024-01-31'), ('2004-2013', '2004-01-01', '2013-12-31'), ('2014-2023', '2014-01-01', '2023-12-31')]

comps = [('SSL', 'hei'), ('TSL', 'thei'), ('HSL', 'shei')]
layers = [('Upper 300 m', 0, 300), ('Mid-depth', 300, 2000)]

rows = ['Months used'] + ['%s (%s)' % (c, ln) for c, _ in comps for ln, _, _ in layers]
tbl = pd.DataFrame('', index=rows, columns=[p[0] for p in periods])
tbl.index.name = 'Trend [cm decade-1], tropical SWIO'

for c, v in comps:
    for ln, d1, d2 in layers:
        for pn, ps, pf in periods:
            txt, n = cell_trend(ARGO, v, d1, d2, ps, pf, box)
            tbl.loc['%s (%s)' % (c, ln), pn] = txt
            tbl.loc['Months used', pn] = n

tbl.to_excel(outDIR + '/Tbl_R1.xlsx', sheet_name='Tbl_R1', header=True, index=True)

#%% Table_R3 Layer x product x window trends, four products
from functions import *
inDIR = ''
outDIR = ''

names = ['ARGO', 'EN4', 'ORAS5', 'SODA']
data = [nctopd(inDIR + '/05_' + n + '.nc') for n in names]
box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)

comps = [('SSL', 'hei'), ('TSL', 'thei'), ('HSL', 'shei')]
layers = [('0-2000', 0, 2000), ('0-300', 0, 300), ('300-2000', 300, 2000)]
windows = [('2004-2021', '2004-01-01', '2021-12-31'), ('2004-2023', '2004-01-01', '2023-12-31')]

cols = ['%s (%s)' % (ln, wn) for ln, _, _ in layers for wn, _, _ in windows]
rows = ['Months used'] + ['%s %s' % (c, n) for c, _ in comps for n in names + ['MEAN']]
tbl = pd.DataFrame('', index=rows, columns=cols)
tbl.index.name = 'Trend [cm decade-1], tropical SWIO, upper 2,000 m budget'

for ln, d1, d2 in layers:
    for wn, ws, wf in windows:
        col = '%s (%s)' % (ln, wn)
        sls = []
        for n, D in zip(names, data):
            for c, v in comps:
                sl, se = tr_trend(D, v, ws, wf, d1, d2, box)
                tbl.loc['%s %s' % (c, n), col] = '%.2f ± %.2f' % (sl, se)
                sls.append((c, sl))
        for c, _ in comps:
            v = np.array([s for cc, s in sls if cc == c])
            tbl.loc['%s MEAN' % c, col] = '%.2f ± %.2f' % (v.mean(), v.std(ddof=1))
        ts = litrend(data[0], 'hei', s=ws, f=wf, rm_season=True, dmin=d1, dmax=d2, timeseries=True, **box)
        tbl.loc['Months used', col] = int(np.asarray(ts.values).size)

tbl.to_excel(outDIR + '/Tbl_R3.xlsx', sheet_name='Tbl_R3', header=True, index=True)

#%% Table_R4 Sea-level budget terms by product
from functions import *
inDIR = ''
outDIR = ''

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

names = ['ARGO', 'EN4', 'ORAS5', 'SODA']
layers = [(0, 300), (300, 2000), (0, 2000)]
sSSL = {}
for nm in names:
    A = nctopd(inDIR + '/05_' + nm + '.nc')
    sSSL[nm] = [bser(A, 'hei', s0, f0, box, d1, d2) for d1, d2 in layers]

rows = ['SL', 'OMESL', 'SL - OMESL (residual)', 'Dataset', 'SSL (Upper 300m)', 'SSL (Mid-depth)', 'SSL (Upper 2,000m)', 'residual - (Upper 2,000m)']
tbl = pd.DataFrame('', index=rows, columns=names)
tbl.loc['SL', names[0]] = fit_series(sSL, s0, f0)[0]
tbl.loc['OMESL', names[0]] = fit_series(sOM, s0, f0)[0]
tbl.loc['SL - OMESL (residual)', names[0]] = fit_series(sRES, s0, f0)[0]
tbl.loc['Dataset'] = names
for nm in names:
    tbl.loc['SSL (Upper 300m)', nm] = fit_series(sSSL[nm][0], s0, f0)[0]
    tbl.loc['SSL (Mid-depth)', nm] = fit_series(sSSL[nm][1], s0, f0)[0]
    tbl.loc['SSL (Upper 2,000m)', nm] = fit_series(sSSL[nm][2], s0, f0)[0]
    tbl.loc['residual - (Upper 2,000m)', nm] = fit_series(sRES - sSSL[nm][2], s0, f0)[0]

tbl.to_excel(outDIR + '/Tbl_R4.xlsx', sheet_name='Tbl_R4', header=False, index=True)

#%% Table_R5 Effect of interpolating the short GRACE gaps on the budget trends
from functions import *
inDIR = ''
outDIR = ''

s0, f0 = '2004-01-01', '2023-12-31'
box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)

Duacs = nctopd(inDIR + '/01_DUACS.nc')
Grace = nctopd(inDIR + '/01_GRACE.nc')

gt = pd.DatetimeIndex(pd.PeriodIndex(pd.to_datetime(Grace['time']().values), freq='M').to_timestamp())
span = np.asarray(Grace['span']().values, dtype=float)
sla = Grace['sla']().assign_coords(time=gt)

has = np.isfinite(sla.values).any(axis=(1, 2))
obs = np.isfinite(span)

sSL = bser(Duacs['sla']().rename('sla'), 'sla', s0, f0, box)
sOM = bser(sla.isel(time=np.where(has)[0]).rename('sla'), 'sla', s0, f0, box)
sRE = sSL - sOM
mobs = pd.Series(obs, index=gt)

rows = []
for lab, ser in [('OMESL', sOM), ('SL - OMESL (residual)', sRE)]:
    a, na = fit_series(ser, s0, f0)
    b, nb = fit_series(ser, s0, f0, mobs)
    rows.append([lab, a, na, b, nb])
a, na = fit_series(sSL, s0, f0)
rows.insert(0, ['SL (altimetry)', a, na, a, na])

tbl = pd.DataFrame(rows, columns=['Quantity', 'All months (gap-filled)', 'n', 'GRACE solution months only', 'n'])
tbl = tbl.set_index('Quantity')
tbl.columns = pd.MultiIndex.from_tuples([('All months (gap-filled)', 'trend'), ('All months (gap-filled)', 'n'), ('GRACE solution months only', 'trend'), ('GRACE solution months only', 'n')])

tbl.to_excel(outDIR + '/Tbl_R5.xlsx', sheet_name='Tbl_R5')

#%% Table_R6 AR(1) and moving-block bootstrap uncertainties for the mid-depth trends and ratios
from functions import *
inDIR = ''
outDIR = ''

s0, f0 = '2004-01-01', '2023-12-31'
box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)
d1, d2 = 300, 2000

A5 = nctopd(inDIR + '/05_ARGO.nc')
sTSL = bser(A5, 'thei', s0, f0, box, d1, d2)
sHSL = bser(A5, 'shei', s0, f0, box, d1, d2)

A3 = nctopd(inDIR + '/03_ARGO.nc')
A3._ds = A3._ds.sel(lat=slice(box['latmin'], box['latmax']), lon=slice(box['lonmin'], box['lonmax']))
[setattr(v, '_ds', A3._ds) for _, v in A3.items() if hasattr(v, '_ds')]
hser_t, hser_s = heave_trend(A3, s=s0, f=f0, depth='m', rm_season=True, return_series=True)
sser_t, sser_s = spice_trend(A3, s=s0, f=f0, depth='m', rm_season=True, return_series=True)

ser = {'TSL': sTSL, 'HSL': sHSL, 'T_heave': bser(hser_t.rename('x'), 'x', s0, f0, box, d1, d2, rs=False), 'T_spice': bser(sser_t.rename('x'), 'x', s0, f0, box, d1, d2, rs=False), 'S_heave': bser(hser_s.rename('x'), 'x', s0, f0, box, d1, d2, rs=False), 'S_spice': bser(sser_s.rename('x'), 'x', s0, f0, box, d1, d2, rs=False)}

est, lo, hi, boot, info = mbb(ser, nboot=10000, stats_fn=mbb_ratios, seed=1234)

rows = []
for nm in ser:
    b, e = ar1_ci(ser[nm], s0, f0)
    rows.append([nm, '%.3f' % est[nm], '%.3f ± %.3f' % (b, e), '[%.3f, %.3f]' % (lo[nm], hi[nm])])
for nm in ['comp_HSL_over_TSL_%', 'T_heave_%', 'T_spice_%', 'S_heave_%', 'S_spice_%']:
    rows.append([nm, '%.1f' % est[nm], '-', '[%.1f, %.1f]' % (lo[nm], hi[nm])])

tbl = pd.DataFrame(rows, columns=['Quantity', 'Estimate', 'AR(1)-adjusted OLS 95% CI', 'MBB 95% CI'])
tbl = tbl.set_index('Quantity')

tbl.to_excel(outDIR + '/Tbl_R6.xlsx', sheet_name='Tbl_R6', index=True)

#%% Table_R7 Reconciliation ladder with Huang et al. (2024)
from functions import *
inDIR = ''
outDIR = ''

box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)
D1, D2 = 0, 2000
comps = [('SSL', 'hei'), ('TSL', 'thei'), ('HSL', 'shei')]

HUANG = {'label': 'Huang et al. (2024), 2002-2021', 'SSL': '1.20 ± 0.20', 'TSL': 'not tabulated', 'HSL': 'described as negligible', 'Months': ''}

steps = [('This study, 4-product mean, 2004-2021', None, '2004-01-01', '2021-12-31'), ('MOAA GPV v2, 2004-2021', 'ARGO', '2004-01-01', '2021-12-31'), ('MOAA GPV v1, 2004-2021', 'MOAAv1', '2004-01-01', '2021-12-31'), ('MOAA GPV v1, 2002-2021', 'MOAAv1', '2002-01-01', '2021-12-31')]

mean_names = ['ARGO', 'EN4', 'ORAS5', 'SODA']
layers = [('0-2,000 m', D1, D2), ('300-2,000 m', 300, 2000)]

rows = []
for ln, d1, d2 in layers:
    for lbl, prod, ws, wf in steps:
        r = {'Layer': ln, 'Step': lbl}
        for c, v in comps:
            if prod is None:
                vals = [tr_trend(load(n, inDIR), v, ws, wf, d1, d2, box)[0] for n in mean_names]
                r[c] = '%.2f ± %.2f' % (np.mean(vals), np.std(vals, ddof=1))
            else:
                sl, se = tr_trend(load(prod, inDIR), v, ws, wf, d1, d2, box)
                r[c] = '%.2f ± %.2f' % (sl, se)
        n0 = prod if prod else mean_names[0]
        ts = litrend(load(n0, inDIR), 'hei', s=ws, f=wf, rm_season=True, dmin=d1, dmax=d2, timeseries=True, **box)
        r['Months'] = int(np.asarray(ts.values).size)
        rows.append(r)

rows.append({'Layer': '0-2,000 m', 'Step': HUANG['label'], 'SSL': HUANG['SSL'], 'TSL': HUANG['TSL'], 'HSL': HUANG['HSL'], 'Months': HUANG['Months']})

tbl = pd.DataFrame(rows).set_index(['Layer', 'Step'])[['SSL', 'TSL', 'HSL', 'Months']]
tbl.to_excel(outDIR + '/Tbl_R7.xlsx', sheet_name='Tbl_R7', header=True, index=True)

#%% Table_R8 Mid-depth TSL, HSL and compensation in MOAA GPV v1 and v2
from functions import *
inDIR = ''
outDIR = ''

box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)
d1, d2 = 300, 2000
data = {'MOAA GPV v2': nctopd(inDIR + '/05_ARGO.nc'), 'MOAA GPV v1': nctopd(inDIR + '/05_MOAAv1.nc')}

periods = [('2004-2021', '2004-01-01', '2021-12-31', ['MOAA GPV v2', 'MOAA GPV v1']), ('2004-2022', '2004-01-01', '2022-12-31', ['MOAA GPV v2', 'MOAA GPV v1']), ('2004-2013', '2004-01-01', '2013-12-31', ['MOAA GPV v2', 'MOAA GPV v1']), ('2014-2022', '2014-01-01', '2022-12-31', ['MOAA GPV v2', 'MOAA GPV v1']), ('2004-2023', '2004-01-01', '2023-12-31', ['MOAA GPV v2']), ('2014-2023', '2014-01-01', '2023-12-31', ['MOAA GPV v2'])]

rows, idx = [], []
for lbl, D in data.items():
    for pn, ws, wf, valid in periods:
        if lbl not in valid:
            continue
        tsl, tse = tr_trend(D, 'thei', ws, wf, d1, d2, box)
        hsl, hse = tr_trend(D, 'shei', ws, wf, d1, d2, box)
        resolved = (tsl - tse > 0) and (hsl + hse < 0)
        comp = '%.0f' % (-hsl / tsl * 100.0) if resolved else 'n/a'
        ts = litrend(D, 'hei', s=ws, f=wf, rm_season=True, dmin=d1, dmax=d2, timeseries=True, **box)
        idx.append((lbl, pn))
        rows.append(['%.2f ± %.2f' % (tsl, tse), '%.2f ± %.2f' % (hsl, hse), comp, int(np.asarray(ts.values).size)])

tbl = pd.DataFrame(rows, index=pd.MultiIndex.from_tuples(idx, names=['Product', 'Period']), columns=['TSL (cm decade-1)', 'HSL (cm decade-1)', 'Compensation (%)', 'Months'])
tbl.to_excel(outDIR + '/Tbl_R8.xlsx', sheet_name='Tbl_R8', header=True, index=True)
