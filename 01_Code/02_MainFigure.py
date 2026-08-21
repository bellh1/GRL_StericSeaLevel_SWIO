#%% Figure_1 ALT, SSL, TSL, HSL + GRACE map - ARGO
from functions import *
plt.rcParams['font.family'] = 'Times New Roman'
inDIR = ''
outDIR = ''
Duacs=nctopd(inDIR+'/01_DUACS.nc')
Grace=nctopd(inDIR+'/01_GRACE.nc')
ARGO=nctopd(inDIR+'/05_ARGO.nc')

Resid = xr.DataArray(Duacs['sla']().values - Grace['sla']().values, dims=('time','lat','lon'), coords={'time': Grace['time']().values, 'lat': ARGO['lat']().values, 'lon': ARGO['lon']().values}, name='sla')

slp_duacs, _, _, p_duacs, _, _ = litrend(Duacs, 'sla', s='2004-01-01', f='2023-12-31', rm_season=True, ar1=False, return_stats=True)
slp_grace, _, _, p_grace, _, _ = litrend(Grace, 'sla', s='2004-01-01', f='2023-12-31', rm_season=True, ar1=False, return_stats=True)
slp_resid, _, _, p_resid, _, _ = litrend(Resid, 'sla', s='2004-01-01', f='2023-12-31', rm_season=True, ar1=False, return_stats=True)
ts, _, _, p_ts, _, _ = litrend(ARGO, 'hei', s='2004-01-01', f='2023-12-31', rm_season=True, dmin=0, dmax=2000, ar1=False, return_stats=True)
t, _, _, p_t, _, _ = litrend(ARGO, 'thei', s='2004-01-01', f='2023-12-31', rm_season=True, dmin=0, dmax=2000, ar1=False, return_stats=True)
s, _, _, p_s, _, _ = litrend(ARGO, 'shei', s='2004-01-01', f='2023-12-31', rm_season=True, dmin=0, dmax=2000, ar1=False, return_stats=True)
slp_duacs, slp_grace, slp_resid, ts, t, s = slp_duacs.values, slp_grace.values, slp_resid.values, ts.values, t.values, s.values
p_duacs, p_grace, p_resid, p_ts, p_t, p_s = p_duacs.values, p_grace.values, p_resid.values, p_ts.values, p_t.values, p_s.values

plt.rcParams['mathtext.fontset'] = 'stix'
cmap = cmc.roma_r

titles = ['(a) SL', '(b) OMESL', '(c) SL – OMESL (residual)', '(d) SSL', '(e) TSL', '(f) HSL']

clevels = np.linspace(-5, 5, 11)

fmt_lon = lambda lon: r'$%d^\circ$E' % lon
fmt_lat = lambda lat: (r'Equ' if lat == 0 else r'$%d^\circ$%s' % (abs(int(lat)), 'S' if lat < 0 else 'N'))

fig = plt.figure(figsize=(24, 33.936))

gs = gridspec.GridSpec(4, 7, height_ratios=[1, 1, 1, 1.5], width_ratios=[0.1, 3, 0.1,3, 0.1,3, 0.8])
ax1 = fig.add_subplot(gs[1, 1])
ax2 = fig.add_subplot(gs[1, 3])
ax3 = fig.add_subplot(gs[1, 5])
ax4 = fig.add_subplot(gs[2, 1])
ax5 = fig.add_subplot(gs[2, 3])
ax6 = fig.add_subplot(gs[2, 5])

ax0 = fig.add_subplot(gs[0, 0:7])
ax0.axis('off')
ax0 = fig.add_subplot(gs[3, 0:7])
ax0.axis('off')

lon, lat = np.meshgrid(ARGO['lon']().values, ARGO['lat']().values)
lon1, lat1 = lon, lat

indian_ocean_polygon = [(40, -35), (40, 25), (56, 25), (100, 23), (100, 20), (100, 21), (100, 20), (95, 18), (94, 10), (95, 6), (100, 2), (101, -3), (103, -5), (120, -10), (120, -20), (120, -35)]

inside_duacs = polygon_mask(lon, lat, indian_ocean_polygon)
inside_argo = polygon_mask(lon1, lat1, indian_ocean_polygon)

slp_duacs1 = np.ma.masked_where(~inside_duacs, slp_duacs)
slp_grace1 = np.ma.masked_where(~inside_duacs, slp_grace)
slp_diff1 = np.ma.masked_where(~inside_duacs, slp_resid)

ts1 = np.ma.masked_where(~inside_argo, ts)
t1 = np.ma.masked_where(~inside_argo, t)
s1 = np.ma.masked_where(~inside_argo, s)

m = Basemap(projection='merc', llcrnrlon=40, urcrnrlon=120, llcrnrlat=-35, urcrnrlat=25, resolution='l', ax=ax1)
x, y = m(lon, lat)
cs = m.contourf(x, y, slp_duacs1, cmap=cmap, levels=clevels, extend='both', zorder=0)
stip_sig(m, p_duacs, inside_duacs, lon, lat)

m2 = Basemap(projection='merc', llcrnrlon=40, urcrnrlon=120, llcrnrlat=-35, urcrnrlat=25, resolution='l', ax=ax2)
cs = m2.contourf(x, y, slp_grace1, cmap=cmap, levels=clevels, extend='both', zorder=0)
stip_sig(m2, p_grace, inside_duacs, lon, lat)

m3 = Basemap(projection='merc', llcrnrlon=40, urcrnrlon=120, llcrnrlat=-35, urcrnrlat=25, resolution='l', ax=ax3)
cs2 = m3.contourf(x, y, slp_diff1, cmap=cmap, levels=clevels, extend='both', zorder=0)
stip_sig(m3, p_resid, inside_duacs, lon, lat)

m4 = Basemap(projection='merc', llcrnrlon=40, urcrnrlon=120, llcrnrlat=-35, urcrnrlat=25, resolution='l', ax=ax4)
cs2 = m4.contourf(x, y, ts1, cmap=cmap, levels=clevels, extend='both', zorder=0)
stip_sig(m4, p_ts, inside_argo, lon, lat)

m5 = Basemap(projection='merc', llcrnrlon=40, urcrnrlon=120, llcrnrlat=-35, urcrnrlat=25, resolution='l', ax=ax5)
cs2 = m5.contourf(x, y, t1, cmap=cmap, levels=clevels, extend='both', zorder=0)
stip_sig(m5, p_t, inside_argo, lon, lat)

m6 = Basemap(projection='merc', llcrnrlon=40, urcrnrlon=120, llcrnrlat=-35, urcrnrlat=25, resolution='l', ax=ax6)
cs2 = m6.contourf(x, y, s1, cmap=cmap, levels=clevels, extend='both', zorder=0)
stip_sig(m6, p_s, inside_argo, lon, lat)

for i in (m,m2,m3,m4, m5, m6):
    i.drawcoastlines(linewidth=0.3)
    i.fillcontinents(color='lightgray', lake_color='lightgray', zorder=2)
    i.drawparallels(np.arange(-95, 95, 5), labels=[0, 0, 0, 0], color='gray', linewidth=0.3)
    i.drawmeridians(np.arange(-5, 365, 5), labels=[0, 0, 0, 0], color='gray', linewidth=0.3)
    par = i.drawparallels(np.arange(-90, 90, 10), labels=[1,0,0,0], fontsize=35, color='gray', linewidth=1, dashes=[2,2], fmt=fmt_lat)
    i.drawmeridians(np.arange(0, 360, 20), labels=[0, 0, 0, 0], fontsize=35, color='gray', linewidth=1, dashes=[2, 2])
    mer = i.drawmeridians(np.arange(10, 360, 20), labels=[0,0,0,1], fontsize=35, color='gray', linewidth=1, dashes=[2,2], fmt=fmt_lon)
    mbox(i, 50, 80, -15, -5, 'black', 5, 10)

ax=[ax1, ax2, ax3, ax4, ax5, ax6]
for j in ll(ax):
    ax[j].set_aspect(0.8)
    for spine in ax[j].spines.values(): spine.set_linewidth(2)
    ax[j].set_title(titles[j], fontsize=35, pad=10, loc='left')
cbar_ax1 = fig.add_axes([0.94, 0.475, 0.02, 0.25])
cb1 = fig.colorbar(cs, cax=cbar_ax1)
cb1.ax.tick_params(labelsize=35, pad=10)
cb1.set_ticks([-5,-4,-3,-2,-1,0,1,2,3,4,5])
cbar_ax1.text(-1, 0, r'Trend [cm decade$^{-1}$] ',va='center', ha='center', fontsize=35, rotation=90)
for spine in cb1.ax.spines.values(): spine.set_linewidth(2)

plt.subplots_adjust(wspace=0.2)
plt.subplots_adjust(hspace=-0.55)
fig.subplots_adjust(left=0.05, right=0.99, top=1, bottom=0)
plt.savefig(outDIR + '/fig_01.png', dpi=100, bbox_inches=None, transparent=True)

#%% Figure_2 SSL, TSL, HSL Upper 300 & Mid-depth timeseries
from functions import *
inDIR = ''
outDIR = ''
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'Times New Roman'

ARGO = nctopd(inDIR + '/05_ARGO.nc')
dataset=pd.Series(index=['ts_top','ts_bot', 't_top', 't_bot', 's_top', 's_bot'], dtype='object')

dataset.loc['ts_top']=litrend(ARGO, 'hei', s='2004-01-01', f='2023-12-31', rm_season=True, dmin=0, dmax=300, lonmin=50, lonmax=80, latmin=-15, latmax=-5, timeseries=True).values
dataset.loc['ts_bot']=litrend(ARGO, 'hei', s='2004-01-01', f='2023-12-31', rm_season=True, dmin=300, dmax=2000, lonmin=50, lonmax=80, latmin=-15, latmax=-5, timeseries=True).values

dataset.loc['t_top']=litrend(ARGO, 'thei', s='2004-01-01', f='2023-12-31', rm_season=True, dmin=0, dmax=300, lonmin=50, lonmax=80, latmin=-15, latmax=-5, timeseries=True).values
dataset.loc['t_bot']=litrend(ARGO, 'thei', s='2004-01-01', f='2023-12-31', rm_season=True, dmin=300, dmax=2000, lonmin=50, lonmax=80, latmin=-15, latmax=-5, timeseries=True).values

dataset.loc['s_top']=litrend(ARGO, 'shei', s='2004-01-01', f='2023-12-31', rm_season=True, dmin=0, dmax=300, lonmin=50, lonmax=80, latmin=-15, latmax=-5, timeseries=True).values
dataset.loc['s_bot']=litrend(ARGO, 'shei', s='2004-01-01', f='2023-12-31', rm_season=True, dmin=300, dmax=2000, lonmin=50, lonmax=80, latmin=-15, latmax=-5, timeseries=True).values
x=datacut(ARGO, 'hei', s='2004-01-01', f='2023-12-31', dmin=0, dmax=10, lonmin=50, lonmax=51, latmin=-15, latmax=-14)['time']

ltext=['', '']
for var, dmin, dmax in [('hei', 0, 300), ('hei', 300, 2000), ('thei', 0, 300), ('thei', 300, 2000), ('shei', 0, 300), ('shei', 300, 2000)]:
    sl, _, _, _, se, dof = litrend(ARGO, var, s='2004-01-01', f='2023-12-31', rm_season=True, dmin=dmin, dmax=dmax, lonmin=50, lonmax=80, latmin=-15, latmax=-5, ar1=False, return_stats=True)
    ltext.append(rf'${float(sl):.2f} \pm {float(2.0 * se):.2f}\ \mathrm{{cm\ decade^{{-1}}}}$')

fig = plt.figure(figsize=(24, 33.936))
gs = gridspec.GridSpec(6, 4, height_ratios=[1, 1, 1, 1, 1, 2], width_ratios=[0.01,1,1,0.01])

ax1 = fig.add_subplot(gs[1, 1])
ax2 = fig.add_subplot(gs[1, 2])

ax3 = fig.add_subplot(gs[2, 1])
ax4 = fig.add_subplot(gs[2, 2])

ax5 = fig.add_subplot(gs[3, 1])
ax6 = fig.add_subplot(gs[3, 2])

ax7 = fig.add_subplot(gs[4, 1])
ax8 = fig.add_subplot(gs[4, 2])

ax0 = fig.add_subplot(gs[0, 0:3])
ax0.axis('off')
ax0 = fig.add_subplot(gs[5, 0:3])
ax0.axis('off')

cc=['', 'black', 'red', 'blue']
titles=['Upper 300 m', 'Mid-depth', 'Upper 300 m SSL', 'Mid-depth SSL', 'Upper 300 m TSL', 'Mid-depth TSL', 'Upper 300 m HSL', 'Mid-depth HSL']

ax1.plot(x, dataset.loc['ts_top'], color='black', linewidth=4, zorder=4)
ax1.plot(x, dataset.loc['t_top'], color='red', linewidth=4, zorder=4)
ax1.plot(x, dataset.loc['s_top'], color='blue', linewidth=4, zorder=4)
ax2.plot(x, dataset.loc['ts_bot'], color='black', linewidth=4, zorder=4)
ax2.plot(x, dataset.loc['t_bot'], color='red', linewidth=4, zorder=4)
ax2.plot(x, dataset.loc['s_bot'], color='blue', linewidth=4, zorder=4)

ax3.plot(x, dataset.loc['ts_top'], color='black', linewidth=4, zorder=4)
ax3.plot(x, trend(x, dataset.loc['ts_top']), color='black', linewidth=3, zorder=5, linestyle=(0, (3, 2)))
ax4.plot(x, dataset.loc['ts_bot'], color='black', linewidth=4, zorder=4)
ax4.plot(x, trend(x, dataset.loc['ts_bot']), color='black', linewidth=3, zorder=5, linestyle=(0, (3, 2)))

ax5.plot(x, dataset.loc['t_top'], color='red', linewidth=4, zorder=4)
ax5.plot(x, trend(x, dataset.loc['t_top']), color='red', linewidth=3, zorder=5, linestyle=(0, (3, 2)))
ax6.plot(x, dataset.loc['t_bot'], color='red', linewidth=4, zorder=4)
ax6.plot(x, trend(x, dataset.loc['t_bot']), color='red', linewidth=3, zorder=5, linestyle=(0, (3, 2)))

ax7.plot(x, dataset.loc['s_top'], color='blue', linewidth=4, zorder=4)
ax7.plot(x, trend(x, dataset.loc['s_top']), color='blue', linewidth=3, zorder=5, linestyle=(0, (3, 2)))
ax8.plot(x, dataset.loc['s_bot'], color='blue', linewidth=4, zorder=4)
ax8.plot(x, trend(x, dataset.loc['s_bot']), color='blue', linewidth=3, zorder=5, linestyle=(0, (3, 2)))

axx=[ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]

for i in ll(axx):
    if i % 2 == 0:
        axx[i].set_ylim(-20,20)
        axx[i].set_yticks([-20,-10,0,10,20])
    else:
        axx[i].set_ylim(-5,5)
        axx[i].set_yticks([-5, -2.5, 0, 2.5, 5])
        axx[i].set_yticklabels(['-5', '-2.5', '0', '2.5', '5'])
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
    axx[i].set_title('('+chr(97+i)+') '+titles[i], fontsize=35, pad=10, loc='left')
    axx[i].text(0.95, 0.1, ltext[i], transform=axx[i].transAxes, fontsize=35, fontweight='bold', va='bottom', ha='right')
    for spine in axx[i].spines.values(): spine.set_linewidth(2)
    if i==0 or i==1:
        handles = [Line2D([0],[0], color='k', lw=6, ls='-', label='SSL'),Line2D([0],[0], color='red', lw=6, ls='-', label='TSL'),Line2D([0],[0], color='blue', lw=6, ls='-', label='HSL')]
        axx[i].legend(handles=handles, loc='upper left', bbox_to_anchor=(0, 1.05), frameon=False, ncol=3, fontsize=35, handlelength=1.5, handletextpad=0.3, columnspacing=0.6)
    else:
        handles = [Line2D([0],[0], color=cc[int(i/2)], lw=6, ls='-', label='Monthly'), Line2D([0],[0], color=cc[int(i/2)], lw=6, label='Trend', linestyle=(0, (2, 1)))]
        axx[i].legend(handles=handles, loc='upper left', bbox_to_anchor=(0, 1.05), frameon=False, ncol=2, fontsize=35, handlelength=1.5, handletextpad=0.3, columnspacing=0.6)

plt.subplots_adjust(wspace=0.4)
plt.subplots_adjust(hspace=0.4)
fig.subplots_adjust(left=0.05, right=0.99, top=1, bottom=0)
plt.savefig(outDIR + '/fig_02.png', dpi=100, bbox_inches=None, transparent=True)

#%% Figure_3 T, S Trend Heave & Spice
from functions import *
inDIR = ''
outDIR = ''
ARGO=nctopd(inDIR+'/07_ARGO.nc')
dataset=pd.Series(index=['trend', 'heave','spice', 'depth'])

dataset.loc['strend']=datacut(ARGO,'trend_sr', lonmin=50, lonmax=80, latmin=-60, latmax=20, dmin=0, dmax=2500)['trend_sr'].values
dataset.loc['sheave']=datacut(ARGO,'heave_sr', lonmin=50, lonmax=80, latmin=-60, latmax=20, dmin=0, dmax=2500)['heave_sr'].values
dataset.loc['sspice']=datacut(ARGO,'spice_sr', lonmin=50, lonmax=80, latmin=-60, latmax=20, dmin=0, dmax=2500)['spice_sr'].values
dataset.loc['ttrend']=datacut(ARGO,'trend_tr', lonmin=50, lonmax=80, latmin=-60, latmax=20, dmin=0, dmax=2500)['trend_tr'].values
dataset.loc['theave']=datacut(ARGO,'heave_tr', lonmin=50, lonmax=80, latmin=-60, latmax=20, dmin=0, dmax=2500)['heave_tr'].values
dataset.loc['tspice']=datacut(ARGO,'spice_tr', lonmin=50, lonmax=80, latmin=-60, latmax=20, dmin=0, dmax=2500)['spice_tr'].values
dataset.loc['depth']=datacut(ARGO,'heave_sr', lonmin=50, lonmax=80, latmin=-60, latmax=20, dmin=0, dmax=2500)['depth']
dataset.loc['dens']=datacut(ARGO,'dens', lonmin=50, lonmax=80, latmin=-60, latmax=20, dmin=0, dmax=2500)['dens']
lon=datacut(ARGO,'heave_sr', lonmin=50, lonmax=80, latmin=-60, latmax=20, dmin=0, dmax=2500)['lon']
lat=datacut(ARGO,'heave_sr', lonmin=50, lonmax=80, latmin=-60, latmax=20, dmin=0, dmax=2500)['lat']

pval=[ARGO['p_'+v]().sel(lat=slice(-60, 20), depth=slice(0, 2500)).values for v in ['trend_tr','heave_tr','spice_tr','trend_sr','heave_sr','spice_sr']]

title=['Temperature Trend','Temperature Heave','Temperature Spice', 'Salinity Trend','Salinity Heave','Salinity Spice']
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['hatch.linewidth'] = 1
cmap1 = cmc.vik

cmap2 = cmc.bam
fig = plt.figure(figsize=(24, 33.936))
gs = gridspec.GridSpec(5, 5, height_ratios=[1,1,-0.1,1,1.2], width_ratios=[0,1,1,1,-0.2])
ax1 = fig.add_subplot(gs[1, 1])
ax2 = fig.add_subplot(gs[1, 2])
ax3 = fig.add_subplot(gs[1, 3])
ax4 = fig.add_subplot(gs[3, 1])
ax5 = fig.add_subplot(gs[3, 2])
ax6 = fig.add_subplot(gs[3, 3])
ax0 = fig.add_subplot(gs[4, 1:3])
ax0.axis('off')
ax0 = fig.add_subplot(gs[0,0:5])
ax0.axis('off')
ax=[ax1, ax2, ax3, ax4, ax5, ax6]

x, y = np.meshgrid(lat, dataset.loc['depth'])
cs1=ax1.contourf(x,y,np.nanmean(dataset.loc['ttrend'], axis=2), cmap=cmap1, levels=np.linspace(-0.2, 0.2, 13), extend='both', zorder=0)
ax2.contourf(x,y,np.nanmean(dataset.loc['theave'], axis=2), cmap=cmap1, levels=np.linspace(-0.2, 0.2, 13), extend='both', zorder=0)
ax3.contourf(x,y,np.nanmean(dataset.loc['tspice'], axis=2), cmap=cmap1, levels=np.linspace(-0.2, 0.2, 13), extend='both', zorder=0)

cs2=ax4.contourf(x,y,np.nanmean(dataset.loc['strend'], axis=2), cmap=cmap2, levels=np.linspace(-0.02, 0.02, 9), extend='both', zorder=0)
ax5.contourf(x,y,np.nanmean(dataset.loc['sheave'], axis=2), cmap=cmap2, levels=np.linspace(-0.02, 0.02, 9), extend='both', zorder=0)
ax6.contourf(x,y,np.nanmean(dataset.loc['sspice'], axis=2), cmap=cmap2, levels=np.linspace(-0.02, 0.02, 9), extend='both', zorder=0)

skx, z0_stip, dz_stip, s_stip = 4, 50, 100, 100
zt = np.arange(z0_stip, 2001, dz_stip)
dep = np.asarray(dataset.loc['depth'], dtype=float)
rows = np.array([np.abs(dep - zz).argmin() for zz in zt])
cols = np.arange(0, pval[0].shape[1], skx)
xs, ys = np.meshgrid(np.asarray(lat)[cols], zt)
for i in ll(ax):
    sig = pval[i][np.ix_(rows, cols)] < 0.05
    ax[i].scatter(xs[sig], ys[sig], s=s_stip, c='k', marker='.', linewidths=0, zorder=4)
    cs=ax[i].contour(x,y,np.nanmean(dataset.loc['dens'], axis=2), levels=np.arange(27.2, 27.51, 0.1), colors='black', zorder=1)
    labels=ax[i].clabel(cs, inline=True, inline_spacing=-60, fontsize=25, fmt=lambda x: rf'$\sigma_0$={x:g}', manual=[(-12,700), (-8,800), (-12,1000), (-8,1200)])
    for txt in labels: txt.set_rotation(0)
    ax[i].axvspan(-30, -15, facecolor='none', hatch='//', edgecolor='black', linewidth=0, zorder=5)
    ax[i].axvspan(0, -5, facecolor='none', hatch='//', edgecolor='black', linewidth=0, zorder=5)
    ax[i].set_title('('+chr(97+i)+') '+title[i], fontsize=35, pad=20, loc='left', fontweight='bold')
    ax[i].set_ylim(2000,0)
    ax[i].set_xlim(-20,0)
    ax[i].grid(True)
    ax[i].plot([-5,-5], [0,6000], color='black'); ax[i].plot([-15,-15], [0,6000], color='black')
    ax[i].yaxis.set_minor_locator(FixedLocator(list(range(100,5600,100))))
    ax[i].grid(which='minor', lw=0.3, color='gray', linestyle=':')
    ax[i].tick_params(axis='both', labelsize=35, pad=10)
    ax[i].tick_params(axis='x')
    for spine in ax[i].spines.values(): spine.set_linewidth(2)
    ax[i].tick_params(axis='both', top=True, bottom=True, left=True, right=True, direction='in', length=3, width=2)
    ax[i].tick_params(axis='both', which='minor', top=True, bottom=True, left=True, right=True, direction='in', length=3, width=1)
    if i in [0, 3]:ax[i].set_ylabel('Depth [m]', fontsize=35)
    ax[i].set_yticks([0,500,1000,1500,2000])
    ax[i].xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: 'Equ' if x == 0 else f'{abs(int(x))}°S')); ax[i].set_xticks([-20,-15,-10,-5,0]); ax[i].tick_params(axis='x', labelrotation=-45)
    ax[i].set_aspect(1/130)

cbar_ax1 = fig.add_axes([0.35, 0.535, 0.4, 0.01])
cb1 = fig.colorbar(cs1, cax=cbar_ax1, orientation='horizontal')
cb1.ax.tick_params(labelsize=35, pad=10)
cb1.set_ticks([-0.2, -0.1, 0, 0.1, 0.2])
cb1.ax.set_xticklabels(['-2', '-1', '0', '1', '2'])
cbar_ax1.text(0.5, -2, r'Temperature Trend [$\times 10^{-1}$ °C decade$^{-1}$]', fontsize=35, va='top', ha='center', transform=cbar_ax1.transAxes)
for spine in cb1.ax.spines.values(): spine.set_linewidth(2)

cbar_ax2 = fig.add_axes([0.35, 0.275, 0.4, 0.01])
cb2 = fig.colorbar(cs2, cax=cbar_ax2, orientation='horizontal')
cb2.ax.tick_params(labelsize=35, pad=10)
cb2.set_ticks([-0.02, -0.01, 0, 0.01, 0.02])
cb2.ax.set_xticklabels(['-2', '-1', '0', '1', '2'])
cbar_ax2.text(0.5, -2, r'Salinity Trend [$\times 10^{-2}$ g kg$^{-1}$ decade$^{-1}$]', fontsize=35, va='top', ha='center', transform=cbar_ax2.transAxes)
for spine in cb2.ax.spines.values(): spine.set_linewidth(2)

plt.subplots_adjust(wspace=0.4)
plt.subplots_adjust(hspace=0.2)
fig.subplots_adjust(left=0.05, right=0.99, top=1, bottom=0)

plt.savefig(outDIR + '/fig_03.png', dpi=100, bbox_inches=None, transparent=True)

#%% Figure_4 Thickness, T, S
from functions import *
inDIR = ''
outDIR = ''
ARGO = inDIR + '/03_ARGO.nc'

dens_levels = np.array([27.2, 27.3, 27.4, 27.5])

ARGO = nctopd(ARGO)
ARGO._ds = ARGO._ds.sortby(['lat','lon']).sel(lat=slice(-70, 0), lon=slice(40, 120))
[setattr(v, '_ds', ARGO._ds) for _, v in ARGO.items() if hasattr(v, '_ds')]

res = interp_ARGO_to_density(ARGO, densmin=27.2, densmax=27.5, densinterval=0.1, compute=True, n_threads=os.cpu_count())

temp_band = density_band_average(res, 'temp', dens_levels)
sali_band = density_band_average(res, 'sali', dens_levels)
pb = res['pres'].sel(density=dens_levels, method='nearest')
thick_band = (pb.isel(density=-1) - pb.isel(density=0)).where(lambda d: d > 0)

temp_trend_da, _, _, temp_p_da, _, _ = litrend(temp_band.rename('temp'), 'temp', s='2004-01-01', f='2023-12-31', rm_season=True, ar1=False, return_stats=True)
sali_trend_da, _, _, sali_p_da, _, _ = litrend(sali_band.rename('sali'), 'sali', s='2004-01-01', f='2023-12-31', rm_season=True, ar1=False, return_stats=True)
thick_trend_da, _, _, thick_p_da, _, _ = litrend(thick_band.rename('thick'), 'thick', s='2004-01-01', f='2023-12-31', rm_season=True, ar1=False, return_stats=True)

thick_trend = thick_trend_da.transpose('lat','lon').values
temp_trend = temp_trend_da.transpose('lat','lon').values
sali_trend = sali_trend_da.transpose('lat','lon').values
p_list = [thick_p_da.transpose('lat','lon').values, temp_p_da.transpose('lat','lon').values, sali_p_da.transpose('lat','lon').values]

lon2d, lat2d = np.meshgrid(ARGO['lon']().values, ARGO['lat']().values)

plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['text.usetex'] = True

data_list = [thick_trend, temp_trend * 10.0, sali_trend * 100.0]
title_list = [r'(a) $\sigma_0$ 27.2--27.5 band', r'(b) $\sigma_0$ 27.2--27.5 average', r'(c) $\sigma_0$ 27.2--27.5 average']
levels_list = [np.arange(-40, 41, 1), np.arange(-4, 4.1, 0.1), np.arange(-2, 2.1, 0.1)]
cmap_list = [cmc.roma_r, cmc.vik, cmc.bam]
cbar_labels = ['Thickness Trend [m decade$^{-1}$]', r'Temperature Trend [$\times 10^{-1}$ $^\circ$C decade$^{-1}$]', r'Salinity Trend [$\times 10^{-2}$ g kg$^{-1}$ decade$^{-1}$]']
cbar_ticks = [[-40, -20, 0, 20, 40], [-4, -2, 0, 2, 4], [-2, -1, 0, 1, 2]]
cbar_ticklabels = [['-40', '-20', '0', '20', '40'], ['-4', '-2', '0', '2', '4'], ['-2', '-1', '0', '1', '2']]
proj = ccrs.SouthPolarStereo(central_longitude=80)
pc = ccrs.PlateCarree()
fig = plt.figure(figsize=(24, 8.8))
gs = gridspec.GridSpec(1, 3, width_ratios=[1, 1, 1])
ax1 = fig.add_subplot(gs[0, 0], projection=proj)
ax2 = fig.add_subplot(gs[0, 1], projection=proj)
ax3 = fig.add_subplot(gs[0, 2], projection=proj)
axes = [ax1, ax2, ax3]

mappables = []

for i in ll(axes):
    axes[i].set_extent([40, 120, -90, 0], crs=pc)
    make_annular_sector_boundary(axes[i], proj, lonmin=40, lonmax=120, inner_lat=-70, outer_lat=0)
    axes[i].set_facecolor('white')
    cs = axes[i].contourf(lon2d, lat2d, data_list[i], levels=levels_list[i], cmap=cmap_list[i], extend='both', transform=pc)
    k = p_list[i][::8, ::8] < 0.05
    axes[i].scatter(lon2d[::8, ::8][k], lat2d[::8, ::8][k], s=40, c='k', marker='.', linewidths=0, transform=pc, zorder=4)
    axes[i].add_feature(cfeature.LAND, facecolor='lightgray', edgecolor='none', zorder=2)
    axes[i].coastlines(linewidth=0.3, zorder=3)
    axes[i].gridlines(crs=pc, draw_labels=False, xlocs=[40,60,80,100,120], ylocs=[0,-20,-40,-60], linewidth=0.7, color='gray', linestyle=(0, (2, 2)), zorder=1)
    add_custom_geo_labels(axes[i], [60,80,100], [0,-20,-40,-60], 40, top_lat=1, side_offset=2.5, fs=35)
    add_custom_geo_labels(axes[i], [40,120], [], 40, top_lat=3, side_offset=2.5, fs=35)
    draw_box(axes[i], 50, 80, -15, -5, color='black', lw=3, zorder=8)
    axes[i].set_title(title_list[i], fontsize=35, pad=56)
    axes[i].spines['geo'].set_linewidth(2)
    mappables.append(cs)
plt.subplots_adjust(wspace=0.22)
fig.subplots_adjust(left=0.04, right=0.97, top=1, bottom=0)
fig.canvas.draw()

for i in ll(axes):
    pos = axes[i].get_position()
    cbar_width = pos.width * 0.90
    cbar_x0 = pos.x0 + 0.5 * (pos.width - cbar_width)
    cbar_y0 = pos.y0 - 0.006 - 0.04
    cax = fig.add_axes([cbar_x0, cbar_y0, cbar_width, 0.04])
    cb = fig.colorbar(mappables[i], cax=cax, orientation='horizontal')
    cb.set_label(cbar_labels[i], fontsize=35, labelpad=4)
    cb.set_ticks(cbar_ticks[i])
    cb.set_ticklabels(cbar_ticklabels[i])
    cb.ax.tick_params(labelsize=35, length=8, width=2)
    for spine in cb.ax.spines.values(): spine.set_linewidth(2)

plt.savefig(outDIR + '/fig_04.png', dpi=100, bbox_inches=None, transparent=True)
plt.show()
