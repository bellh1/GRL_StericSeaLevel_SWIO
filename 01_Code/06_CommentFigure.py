#%% Figure_R1 Mid-depth HSL timeseries across the analysis windows
from functions import *

inDIR = ''
outDIR = ''

plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'Times New Roman'

ARGO = nctopd(inDIR + '/05_ARGO.nc')
box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)
S0, F0 = '2004-01-01', '2024-01-31'

ts = litrend(ARGO, 'shei', s=S0, f=F0, rm_season=True, dmin=300, dmax=2000, timeseries=True, **box)
x = pd.DatetimeIndex(pd.PeriodIndex(pd.to_datetime(ts['time'].values), freq='M').to_timestamp())
y = np.asarray(ts.values, dtype=float)
Y = xr.DataArray(y, dims=('time',), coords={'time': x}, name='y')

pmap = {'2004-2021': ('2004-01-01', '2021-12-31'), '2004-2023': ('2004-01-01', '2023-12-31'), '2004-2024': ('2004-01-01', '2024-01-31'), '2004-2013': ('2004-01-01', '2013-12-31'), '2014-2023': ('2014-01-01', '2023-12-31')}

panels = [['2004-2021'], ['2004-2023'], ['2004-2024'], ['2004-2013', '2014-2023']]
titles = ['Mid-depth HSL, Jan 2004$-$Dec 2021', 'Mid-depth HSL, Jan 2004$-$Dec 2023', 'Mid-depth HSL, Jan 2004$-$Jan 2024', 'Mid-depth HSL, Jan 2004$-$Dec 2013 and Jan 2014$-$Dec 2023']
pstyles = [(0, (3, 2)), (0, (3, 2))]
tcolors = [['black'], ['black'], ['black'], ['red', 'blue']]

res = {}
for pn, (ps, pf) in pmap.items():
    sl, itc, _, _, se, _ = litrend(Y, 'y', s=ps, f=pf, rm_season=False, ar1=False, return_stats=True)
    m = (x >= pd.Timestamp(ps)) & (x <= pd.Timestamp(pf))
    yr = np.asarray(x[m] - x[m][0]) / np.timedelta64(1, 'D') / 365.2425
    res[pn] = {'m': m, 'fit': float(itc) + (float(sl) / 10.0) * yr, 'slope': float(sl), 'err': 2.0 * float(se), 'mean': float(np.nanmean(y[m])), 'n': int(m.sum())}

ltext, mtext, plabels, mlabels = [], [], [], []
for pns in panels:
    ltext.append([r'Trend: $%.2f \pm %.2f\ \mathrm{cm\ decade^{-1}}$' % (res[pn]['slope'], res[pn]['err']) for pn in pns])
    mtext.append([r'Mean: $%.2f\ \mathrm{cm}$' % res[pn]['mean'] for pn in pns])
    plabels.append(['Trend (%s)' % pn.replace('-', '$-$') for pn in pns])
    mlabels.append(['Mean (%s)' % pn.replace('-', '$-$') for pn in pns])

fig = plt.figure(figsize=(24, 33.936))
gs = gridspec.GridSpec(6, 3, height_ratios=[0.2, 1, 1, 1, 1, 0.4], width_ratios=[0.01, 1, 0.01])

ax1 = fig.add_subplot(gs[1, 1])
ax2 = fig.add_subplot(gs[2, 1])
ax3 = fig.add_subplot(gs[3, 1])
ax4 = fig.add_subplot(gs[4, 1])

ax0 = fig.add_subplot(gs[0, 0:2]); ax0.axis('off')
ax0 = fig.add_subplot(gs[5, 0:2]); ax0.axis('off')

axx = [ax1, ax2, ax3, ax4]

for i in range(len(axx)):
    axx[i].plot(x, y, color='grey', linewidth=4, zorder=4, label='Monthly')
    for j, pn in enumerate(panels[i]):
        r = res[pn]
        if len(panels[i]) > 1:
            axx[i].plot(x[r['m']], np.full(r['n'], r['mean']), color=tcolors[i][j], linewidth=8, zorder=2, alpha=0.4, solid_capstyle='butt', label=mlabels[i][j])
        axx[i].plot(x[r['m']], r['fit'], color=tcolors[i][j], linewidth=6, zorder=5, linestyle=pstyles[j], label=plabels[i][j])
    axx[i].set_ylim(-2, 2)
    axx[i].set_yticks([-2, -1, 0, 1, 2])
    axx[i].set_yticklabels(['-2', '-1', '0', '1', '2'])
    axx[i].grid(True)
    axx[i].set_xlim(pd.Timestamp('2004-01-01'), pd.Timestamp('2024-01-01'))
    axx[i].tick_params(axis='both', labelsize=35, pad=10, direction='in')
    axx[i].xaxis.set_major_locator(mdates.YearLocator(2))
    axx[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    axx[i].xaxis.set_minor_locator(mdates.YearLocator(1))
    axx[i].grid(True, which='minor', axis='x', alpha=0.5)
    axx[i].tick_params(axis='x', which='minor', labelbottom=False, direction='in')
    axx[i].set_ylabel(r'$\eta_{\mathrm{steric}}$ [cm]', fontsize=35)
    axx[i].set_xlabel('Year', fontsize=35)
    axx[i].set_title('(' + chr(97 + i) + ') ' + titles[i], fontsize=35, pad=10, loc='left')
    if len(ltext[i]) == 1:
       axx[i].text(0.95, 0.1, ltext[i][0], transform=axx[i].transAxes, fontsize=35, fontweight='bold', va='bottom', ha='right', color=tcolors[i][0])
    else:
       axx[i].text(0.03, 0.14, ltext[i][0], transform=axx[i].transAxes, fontsize=35, fontweight='bold', va='bottom', ha='left', color=tcolors[i][0])
       axx[i].text(0.03, 0.02, mtext[i][0], transform=axx[i].transAxes, fontsize=35, fontweight='bold', va='bottom', ha='left', color=tcolors[i][0])
       axx[i].text(0.97, 0.14, ltext[i][1], transform=axx[i].transAxes, fontsize=35, fontweight='bold', va='bottom', ha='right', color=tcolors[i][1])
       axx[i].text(0.97, 0.02, mtext[i][1], transform=axx[i].transAxes, fontsize=35, fontweight='bold', va='bottom', ha='right', color=tcolors[i][1])
    axx[i].legend(loc='upper left', bbox_to_anchor=(0, 1.05), frameon=False, ncol=3, fontsize=35, handlelength=1.5, handletextpad=0.3, columnspacing=0.6)

plt.subplots_adjust(wspace=0.4)
plt.subplots_adjust(hspace=0.4)
fig.subplots_adjust(left=0.12, right=0.99, top=1, bottom=0)
plt.savefig(outDIR + '/fig_R1.png', dpi=100, bbox_inches=None, transparent=True)

#%% Figure_R2 Upper 2,000 m SSL, TSL, HSL by product - Huang et al. (2024) axes
from functions import *

inDIR = ''
outDIR = ''

plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'Times New Roman'

names = ['ARGO', 'EN4', 'ORAS5', 'SODA']
data = [nctopd(inDIR + '/05_' + n + '.nc') for n in names]
box = dict(lonmin=50, lonmax=80, latmin=-15, latmax=-5)
S0, F0 = '2004-01-01', '2023-12-31'
D1, D2 = 0, 2000

comps = [('SSL', 'hei', 'black'), ('TSL', 'thei', 'red'), ('HSL', 'shei', 'blue')]

ser, slp, err, fitv = {}, {}, {}, {}
x = None
for n, D in zip(names, data):
    for c, v, _ in comps:
        ts = litrend(D, v, s=S0, f=F0, rm_season=True, dmin=D1, dmax=D2, timeseries=True, **box)
        t = pd.DatetimeIndex(pd.PeriodIndex(pd.to_datetime(ts['time'].values), freq='M').to_timestamp())
        yv = np.asarray(ts.values, dtype=float)
        if x is None:
            x = t
        Y = xr.DataArray(yv, dims=('time',), coords={'time': t}, name='y')
        sl, itc, _, _, se, _ = litrend(Y, 'y', s=S0, f=F0, rm_season=False, ar1=False, return_stats=True)
        yr = np.asarray(t - t[0]) / np.timedelta64(1, 'D') / 365.2425
        ser[(n, c)] = yv
        slp[(n, c)] = float(sl)
        err[(n, c)] = 2.0 * float(se)
        fitv[(n, c)] = float(itc) + (float(sl) / 10.0) * yr

fig = plt.figure(figsize=(24, 33.936))
gs = gridspec.GridSpec(6, 4, height_ratios=[1, 1, 1, 1, 1, 2], width_ratios=[0.01, 1, 1, 0.01])

ax1 = fig.add_subplot(gs[1, 1]); ax2 = fig.add_subplot(gs[1, 2])
ax3 = fig.add_subplot(gs[2, 1]); ax4 = fig.add_subplot(gs[2, 2])
ax5 = fig.add_subplot(gs[3, 1]); ax6 = fig.add_subplot(gs[3, 2])
ax7 = fig.add_subplot(gs[4, 1]); ax8 = fig.add_subplot(gs[4, 2])

ax0 = fig.add_subplot(gs[0, 0:3]); ax0.axis('off')
ax0 = fig.add_subplot(gs[5, 0:3]); ax0.axis('off')

axx = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]

for i in ll(axx):
    n = names[int(i / 2)]
    withtrend = (i % 2 == 1)
    for c, v, col in comps:
        axx[i].plot(x, ser[(n, c)], color=col, linewidth=4, zorder=4)
        if withtrend:
            axx[i].plot(x, fitv[(n, c)], color=col, linewidth=3, zorder=5, linestyle=(0, (3, 2)))
    axx[i].set_ylim(-20, 20)
    axx[i].set_yticks([-20, -10, 0, 10, 20])
    axx[i].grid(True)
    axx[i].set_xlim(pd.Timestamp('2004-01-01'), pd.Timestamp('2024-01-01'))
    axx[i].tick_params(axis='both', labelsize=35, pad=10, direction='in')
    axx[i].xaxis.set_major_locator(mdates.YearLocator(4))
    axx[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    axx[i].xaxis.set_minor_locator(mdates.YearLocator(2))
    axx[i].grid(True, which='minor', axis='x', alpha=0.5)
    axx[i].tick_params(axis='x', which='minor', labelbottom=False, direction='in')
    axx[i].set_ylabel(r'$\eta_{\mathrm{steric}}$ [cm]', fontsize=35)
    axx[i].set_xlabel('Year', fontsize=35)
    axx[i].set_title('(' + chr(97 + i) + ') Upper 2,000 m ' + n + (', linear trends' if withtrend else ''), fontsize=35, pad=10, loc='left')
    for spine in axx[i].spines.values(): spine.set_linewidth(2)

    if withtrend:
        items = []
        for c, v, col in comps:
            da = DrawingArea(42, 14, 0, 0)
            da.add_artist(Line2D([0, 34], [7, 7], color=col, linewidth=5))
            txt = TextArea(rf'{c} {slp[(n, c)]:.2f}$\pm${err[(n, c)]:.2f} cm decade$^{{-1}}$', textprops=dict(size=25, family='Times New Roman'))
            items.append(HPacker(children=[da, txt], align='center', pad=0, sep=7))
        anchored = AnchoredOffsetbox(loc='lower right', child=VPacker(children=items, align='left', pad=0, sep=4), pad=0.3, borderpad=0.5, frameon=False, bbox_to_anchor=(0.98, 0.04), bbox_transform=axx[i].transAxes)
        anchored.patch.set_facecolor('white'); anchored.patch.set_alpha(0.65); anchored.patch.set_edgecolor('none')
        anchored.set_zorder(10)
        axx[i].add_artist(anchored)
        handles = [Line2D([0], [0], color='black', lw=6, ls='-', label='Monthly'), Line2D([0], [0], color='black', lw=6, ls=(0, (2, 1)), label='Trend')]
        axx[i].legend(handles=handles, loc='upper left', bbox_to_anchor=(0, 1.05), frameon=False, ncol=2, fontsize=35, handlelength=1.5, handletextpad=0.3, columnspacing=0.6)
    else:
        handles = [Line2D([0], [0], color=col, lw=6, ls='-', label=c) for c, v, col in comps]
        axx[i].legend(handles=handles, loc='upper left', bbox_to_anchor=(0, 1.05), frameon=False, ncol=3, fontsize=35, handlelength=1.5, handletextpad=0.3, columnspacing=0.6)

plt.subplots_adjust(wspace=0.4)
plt.subplots_adjust(hspace=0.4)
fig.subplots_adjust(left=0.05, right=0.99, top=1, bottom=0)
plt.savefig(outDIR + '/fig_R2.png', dpi=100, bbox_inches=None, transparent=True)

#%% Figure_R3 Sea-level budget monthly timeseries - SL, OMESL, SSL
from functions import *

inDIR = ''
outDIR = ''

plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'Times New Roman'

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
colors = ['red', 'blue', 'green', 'saddlebrown']
c_sl, c_om, c_res = 'darkorange', 'purple', 'black'
layers = [(0, 300), (300, 2000), (0, 2000)]
sSSL = {}
for nm in names:
    A = nctopd(inDIR + '/05_' + nm + '.nc')
    sSSL[nm] = [bser(A, 'hei', s0, f0, box, d1, d2) for d1, d2 in layers]
xt = sSL.index

fig = plt.figure(figsize=(24, 36))
gs = gridspec.GridSpec(8, 3, height_ratios=[0.2, 1, 1, 1, 1, 1, 1, 0.4], width_ratios=[0.01, 1, 0.01])

ax1 = fig.add_subplot(gs[1, 1])
ax2 = fig.add_subplot(gs[2, 1])
ax3 = fig.add_subplot(gs[3, 1])
ax4 = fig.add_subplot(gs[4, 1])
ax5 = fig.add_subplot(gs[5, 1])
ax6 = fig.add_subplot(gs[6, 1])

ax0 = fig.add_subplot(gs[0, 0:2]); ax0.axis('off')
ax0 = fig.add_subplot(gs[7, 0:2]); ax0.axis('off')

axx = [ax1, ax2, ax3, ax4, ax5, ax6]
titles = ['SL, OMESL and residual', 'Residual and total steric (0$-$2,000 m)', 'SSL, upper 300 m', 'SSL, mid-depth', 'SSL, upper 2,000 m', 'Unexplained residual']
ylims = [(-20, 20), (-20, 20), (-20, 20), (-4, 4), (-20, 20), (-10, 10)]

draw_series(ax1, sSL, c_sl, 'SL', xt, s0, f0)
draw_series(ax1, sOM, c_om, 'OMESL', xt, s0, f0)
draw_series(ax1, sRES, c_res, 'SL $-$ OMESL', xt, s0, f0)

draw_series(ax2, sRES, c_res, 'SL $-$ OMESL', xt, s0, f0, lw=6)
for j, nm in enumerate(names):
    draw_series(ax2, sSSL[nm][2], colors[j], nm, xt, s0, f0)
    draw_series(ax3, sSSL[nm][0], colors[j], nm, xt, s0, f0)
    draw_series(ax4, sSSL[nm][1], colors[j], nm, xt, s0, f0)
    draw_series(ax5, sSSL[nm][2], colors[j], nm, xt, s0, f0)
    draw_series(ax6, sRES - sSSL[nm][2], colors[j], nm, xt, s0, f0)

for i in range(len(axx)):
    axx[i].axhline(0, color='grey', linewidth=2, linestyle=':', zorder=2)
    axx[i].set_ylim(*ylims[i])
    axx[i].grid(True)
    axx[i].set_xlim(pd.Timestamp('2004-01-01'), pd.Timestamp('2024-01-01'))
    axx[i].tick_params(axis='both', labelsize=35, pad=10, direction='in')
    axx[i].xaxis.set_major_locator(mdates.YearLocator(4))
    axx[i].xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
    axx[i].xaxis.set_minor_locator(mdates.YearLocator(2))
    axx[i].grid(True, which='minor', axis='x', alpha=0.5)
    axx[i].tick_params(axis='x', which='minor', labelbottom=False, direction='in')
    axx[i].set_ylabel(r'$\eta$ [cm]', fontsize=35)
    axx[i].set_title('(' + chr(97 + i) + ') ' + titles[i], fontsize=35, pad=10, loc='left')
    for spine in axx[i].spines.values(): spine.set_linewidth(2)
    if i == len(axx) - 1:
        axx[i].set_xlabel('Year', fontsize=35)
    else:
        axx[i].tick_params(axis='x', labelbottom=False)

for i in range(len(axx)):
    h, l = axx[i].get_legend_handles_labels()
    axx[i].legend(h, l, loc='lower center', bbox_to_anchor=(0.5, -0.05), frameon=False, ncol=len(l), fontsize=35, handlelength=1.5, handletextpad=0.6, columnspacing=3.0)

plt.subplots_adjust(wspace=0.2)
plt.subplots_adjust(hspace=0.3)
fig.subplots_adjust(left=0.05, right=0.99, top=1, bottom=0)
plt.savefig(outDIR + '/fig_R3.png', dpi=100, bbox_inches=None, transparent=True)
