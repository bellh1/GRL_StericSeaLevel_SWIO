#%% Table_S1 Sea-level budget trends, valid months and GRACE gaps
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
mon = pd.DataFrame('', index=rows, columns=names)
tbl.loc['SL', names[0]], mon.loc['SL', names[0]] = fit_series(sSL, s0, f0)
tbl.loc['OMESL', names[0]], mon.loc['OMESL', names[0]] = fit_series(sOM, s0, f0)
tbl.loc['SL - OMESL (residual)', names[0]], mon.loc['SL - OMESL (residual)', names[0]] = fit_series(sRES, s0, f0)
tbl.loc['Dataset'] = names
mon.loc['Dataset'] = names
for nm in names:
    tbl.loc['SSL (Upper 300m)', nm], mon.loc['SSL (Upper 300m)', nm] = fit_series(sSSL[nm][0], s0, f0)
    tbl.loc['SSL (Mid-depth)', nm], mon.loc['SSL (Mid-depth)', nm] = fit_series(sSSL[nm][1], s0, f0)
    tbl.loc['SSL (Upper 2,000m)', nm], mon.loc['SSL (Upper 2,000m)', nm] = fit_series(sSSL[nm][2], s0, f0)
    tbl.loc['residual - (Upper 2,000m)', nm], mon.loc['residual - (Upper 2,000m)', nm] = fit_series(sRES - sSSL[nm][2], s0, f0)

gt = pd.DatetimeIndex(pd.PeriodIndex(pd.to_datetime(Grace['time']().values), freq='M').to_timestamp())
span = np.asarray(Grace['span']().values, dtype=float)
sla = Grace['sla']().assign_coords(time=gt)

has = np.isfinite(sla.values).any(axis=(1, 2))
obs = np.isfinite(span)
fill = has & ~obs
miss = ~has
runs = grace_gap_runs(obs)

cnt = pd.DataFrame({'count': [len(gt), int(obs.sum()), int(fill.sum()), int(miss.sum())]}, index=['months on the analysis axis', 'months with a GRACE solution', 'months filled by interpolation', 'months left missing'])
gaps = pd.DataFrame([[gt[a2].strftime('%Y-%m'), gt[b2].strftime('%Y-%m'), b2 - a2 + 1] for a2, b2 in runs], columns=['start', 'end', 'months'])

with pd.ExcelWriter(outDIR + '/Tbl_S1.xlsx', engine='openpyxl') as xw:
    tbl.to_excel(xw, sheet_name='budget', header=False, index=True)
    mon.to_excel(xw, sheet_name='valid_months', header=False, index=True)
    cnt.to_excel(xw, sheet_name='counts')
    gaps.to_excel(xw, sheet_name='gaps', index=False)

#%% Table_S2 Window sensitivity of SSL, TSL, HSL by layer
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

tbl.to_excel(outDIR + '/Tbl_S2.xlsx', sheet_name='Tbl_S2', header=True, index=True)

#%% Table_S3 Layer x product x window trends including MOAA GPV v1
from functions import *
inDIR = ''
outDIR = ''

mean_names = ['ARGO', 'EN4', 'ORAS5', 'SODA']
names = mean_names + ['MOAAv1']
data = [nctopd(inDIR + '/05_' + n + '.nc') for n in names]
box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)

comps = [('SSL', 'hei'), ('TSL', 'thei'), ('HSL', 'shei')]
layers = [('0-2000', 0, 2000), ('0-300', 0, 300), ('300-2000', 300, 2000)]
windows = [('2004-2021', '2004-01-01', '2021-12-31'), ('2004-2023', '2004-01-01', '2023-12-31')]

cols = ['%s (%s)' % (ln, wn) for ln, _, _ in layers for wn, _, _ in windows]
rows = ['Months ' + n for n in names] + ['%s %s' % (c, n) for c, _ in comps for n in names + ['MEAN']]
tbl = pd.DataFrame('', index=rows, columns=cols)
tbl.index.name = 'Trend [cm decade-1], tropical SWIO'

for ln, d1, d2 in layers:
    for wn, ws, wf in windows:
        col = '%s (%s)' % (ln, wn)
        sls = []
        for n, D in zip(names, data):
            for c, v in comps:
                sl, se = tr_trend(D, v, ws, wf, d1, d2, box)
                tbl.loc['%s %s' % (c, n), col] = '%.2f ± %.2f' % (sl, se)
                if n in mean_names:
                    sls.append((c, sl))
            ts = litrend(D, 'hei', s=ws, f=wf, rm_season=True, dmin=d1, dmax=d2, timeseries=True, **box)
            tbl.loc['Months ' + n, col] = int(np.asarray(ts.values).size)
        for c, _ in comps:
            v = np.array([s for cc, s in sls if cc == c])
            tbl.loc['%s MEAN' % c, col] = '%.2f ± %.2f' % (v.mean(), v.std(ddof=1))

tbl.to_excel(outDIR + '/Tbl_S3.xlsx', sheet_name='Tbl_S3', header=True, index=True)

#%% Table_S4 Reconciliation ladder with Huang et al. (2024)
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

tbl2c = pd.DataFrame(rows).set_index(['Layer', 'Step'])[['SSL', 'TSL', 'HSL', 'Months']]
tbl2c.to_excel(outDIR + '/Tbl_S4.xlsx', sheet_name='Tbl_S4', header=True, index=True)
