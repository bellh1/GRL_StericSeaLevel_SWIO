#%% Figure_S1 SSL, TSL, HSL Upper 300 & Mid-depth timeseries - all datasets
from functions import *
inDIR = ''
outDIR = ''
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'Times New Roman'

ARGO=nctopd(inDIR+'/05_ARGO.nc')
EN4=nctopd(inDIR+'/05_EN4.nc')
ORAS5=nctopd(inDIR+'/05_ORAS5.nc')
SODA=nctopd(inDIR+'/05_SODA.nc')
data=[ARGO, EN4, ORAS5, SODA]

dataset=pd.DataFrame(index=['ARGO', 'EN4', 'ORAS5', 'SODA'], columns=['ts_top','ts_bot', 't_top', 't_bot', 's_top', 's_bot'])
dataset_slope=pd.DataFrame(index=['ARGO', 'EN4', 'ORAS5', 'SODA'], columns=['ts_top','ts_bot', 't_top', 't_bot', 's_top', 's_bot'])
dataset_err=pd.DataFrame(index=['ARGO', 'EN4', 'ORAS5', 'SODA'], columns=['ts_top','ts_bot', 't_top', 't_bot', 's_top', 's_bot'])

for i in ll(dataset.index):
    dataset.loc[dataset.index[i], 'ts_top']=litrend(data[i], 'hei', s='2004-01-01', f='2023-12-31', rm_season=True, dmin=0, dmax=300, lonmin=50, lonmax=80, latmin=-15, latmax=-5, timeseries=True).values
    dataset.loc[dataset.index[i], 'ts_bot']=litrend(data[i], 'hei', s='2004-01-01', f='2023-12-31', rm_season=True, dmin=300, dmax=2000, lonmin=50, lonmax=80, latmin=-15, latmax=-5, timeseries=True).values
    dataset.loc[dataset.index[i], 't_top']=litrend(data[i], 'thei', s='2004-01-01', f='2023-12-31', rm_season=True, dmin=0, dmax=300, lonmin=50, lonmax=80, latmin=-15, latmax=-5, timeseries=True).values
    dataset.loc[dataset.index[i], 't_bot']=litrend(data[i], 'thei', s='2004-01-01', f='2023-12-31', rm_season=True, dmin=300, dmax=2000, lonmin=50, lonmax=80, latmin=-15, latmax=-5, timeseries=True).values
    dataset.loc[dataset.index[i], 's_top']=litrend(data[i], 'shei', s='2004-01-01', f='2023-12-31', rm_season=True, dmin=0, dmax=300, lonmin=50, lonmax=80, latmin=-15, latmax=-5, timeseries=True).values
    dataset.loc[dataset.index[i], 's_bot']=litrend(data[i], 'shei', s='2004-01-01', f='2023-12-31', rm_season=True, dmin=300, dmax=2000, lonmin=50, lonmax=80, latmin=-15, latmax=-5, timeseries=True).values

    for col, var, dmin, dmax in [('ts_top','hei',0,300), ('ts_bot','hei',300,2000), ('t_top','thei',0,300), ('t_bot','thei',300,2000), ('s_top','shei',0,300), ('s_bot','shei',300,2000)]:
        sl, _, _, _, se, dof = litrend(data[i], var, s='2004-01-01', f='2023-12-31', rm_season=True, dmin=dmin, dmax=dmax, lonmin=50, lonmax=80, latmin=-15, latmax=-5, ar1=False, return_stats=True)
        dataset_slope.loc[dataset.index[i], col] = round(float(sl), 2)
        dataset_err.loc[dataset.index[i], col] = round(float(2.0 * se), 2)

x=datacut(ARGO, 'hei', s='2004-01-01', f='2023-12-31', dmin=0, dmax=10, lonmin=50, lonmax=51, latmin=-15, latmax=-14)['time']

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

axx=[ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]
titles = ['Upper 300m ARGO', 'Mid-depth ARGO', 'Upper 300m EN4', 'Mid-depth EN4', 'Upper 300m ORAS5', 'Mid-depth ORAS5', 'Upper 300m SODA', 'Mid-depth SODA']

for i in ll(axx):
    if i%2==0:
        axx[i].plot(x, dataset.loc[dataset.index[int(i/2)], 'ts_top'], color='black', linewidth=4, zorder=4)
        axx[i].plot(x, dataset.loc[dataset.index[int(i/2)], 't_top'], color='red', linewidth=4, zorder=4)
        axx[i].plot(x, dataset.loc[dataset.index[int(i/2)], 's_top'], color='blue', linewidth=4, zorder=4)
        axx[i].plot(x, trend(x, dataset.loc[dataset.index[int(i/2)], 'ts_top']), color='black', linewidth=3, zorder=5, linestyle=(0, (3, 2)))
        axx[i].plot(x, trend(x, dataset.loc[dataset.index[int(i/2)], 't_top']), color='red', linewidth=3, zorder=5, linestyle=(0, (3, 2)))
        axx[i].plot(x, trend(x, dataset.loc[dataset.index[int(i/2)], 's_top']), color='blue', linewidth=3, zorder=5, linestyle=(0, (3, 2)))
        axx[i].set_ylim(-20,20)
        axx[i].set_yticks([-20,-10,0,10,20])
    else:
        axx[i].plot(x, dataset.loc[dataset.index[int(i/2)], 'ts_bot'], color='black', linewidth=4,zorder=4)
        axx[i].plot(x, dataset.loc[dataset.index[int(i/2)], 't_bot'], color='red', linewidth=4, zorder=4)
        axx[i].plot(x, dataset.loc[dataset.index[int(i/2)], 's_bot'], color='blue', linewidth=4, zorder=4)
        axx[i].plot(x, trend(x, dataset.loc[dataset.index[int(i/2)], 'ts_bot']), color='black', linewidth=3, zorder=5, linestyle=(0, (3, 2)))
        axx[i].plot(x, trend(x, dataset.loc[dataset.index[int(i/2)], 't_bot']), color='red', linewidth=3, zorder=5, linestyle=(0, (3, 2)))
        axx[i].plot(x, trend(x, dataset.loc[dataset.index[int(i/2)], 's_bot']), color='blue', linewidth=3, zorder=5, linestyle=(0, (3, 2)))
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
    for spine in axx[i].spines.values(): spine.set_linewidth(2)
    name=dataset.index[int(i/2)]
    layer='top' if i%2==0 else 'bot'
    items=[]
    for label, key, color in [('SSL', 'ts', 'black'), ('TSL', 't', 'red'), ('HSL', 's', 'blue')]:
        da=DrawingArea(42, 14, 0, 0)
        da.add_artist(Line2D([0, 34], [7, 7], color=color, linewidth=5))
        txt=TextArea(rf'{label} {float(dataset_slope.loc[name, key+"_"+layer]):.2f}$\pm${float(dataset_err.loc[name, key+"_"+layer]):.2f} cm decade$^{{-1}}$', textprops=dict(size=25, family='Times New Roman'))
        items.append(HPacker(children=[da, txt], align='center', pad=0, sep=7))
    anchored=AnchoredOffsetbox(loc='lower right', child=VPacker(children=items, align='left', pad=0, sep=4), pad=0.3, borderpad=0.5, frameon=False, bbox_to_anchor=(0.98, 0.04), bbox_transform=axx[i].transAxes)
    anchored.patch.set_facecolor('white')
    anchored.patch.set_alpha(0.65)
    anchored.patch.set_edgecolor('none')
    anchored.set_zorder(10)
    axx[i].add_artist(anchored)

    handles = [Line2D([0],[0], color='black', lw=6, ls='-', label='Monthly'), Line2D([0],[0], color='black', lw=6, label='Trend', linestyle=(0, (2, 1)))]
    axx[i].legend(handles=handles, loc='upper left', bbox_to_anchor=(0, 1.05), frameon=False, ncol=2, fontsize=35, handlelength=1.5, handletextpad=0.3, columnspacing=0.6)
plt.subplots_adjust(wspace=0.4)
plt.subplots_adjust(hspace=0.4)
fig.subplots_adjust(left=0.05, right=0.99, top=1, bottom=0)
plt.savefig(outDIR + '/fig_S01.png', dpi=100, bbox_inches=None, transparent=True)

#%% Figure_S2 T Trend Heave & Spice - all datasets
from functions import *
inDIR = ''
outDIR = ''

EN4=nctopd(inDIR+'/07_EN4.nc')
ORAS5=nctopd(inDIR+'/07_ORAS5.nc')
SODA=nctopd(inDIR+'/07_SODA.nc')
data=[EN4, ORAS5, SODA]

dataset=pd.DataFrame(index=['EN4', 'ORAS5', 'SODA'], columns=['trend', 'heave','spice', 'depth','dens'])

for i in ll(dataset.index):
    dataset.loc[dataset.index[i],'trend']=datacut(data[i],'trend_tr', lonmin=50, lonmax=80, latmin=-20, latmax=1, dmin=0, dmax=2500)['trend_tr'].values
    dataset.loc[dataset.index[i],'heave']=datacut(data[i],'heave_tr', lonmin=50, lonmax=80, latmin=-20, latmax=1, dmin=0, dmax=2500)['heave_tr'].values
    dataset.loc[dataset.index[i],'spice']=datacut(data[i],'spice_tr', lonmin=50, lonmax=80, latmin=-20, latmax=1, dmin=0, dmax=2500)['spice_tr'].values
    dataset.loc[dataset.index[i],'depth']=datacut(data[i],'heave_tr', lonmin=50, lonmax=80, latmin=-20, latmax=1, dmin=0, dmax=2500)['depth']
    dataset.loc[dataset.index[i],'dens']=datacut(data[i],'dens', lonmin=50, lonmax=80, latmin=-20, latmax=1, dmin=0, dmax=2500)['dens']
lon=datacut(EN4,'heave_tr', lonmin=50, lonmax=80, latmin=-20, latmax=1, dmin=0, dmax=2500)['lon']
lat=datacut(EN4,'heave_tr', lonmin=50, lonmax=80, latmin=-20, latmax=1, dmin=0, dmax=2500)['lat']

pval=[data[i]['p_'+v]().sel(lat=slice(-20, 1), depth=slice(0, 2500)).values for i in ll(dataset.index) for v in ['trend_tr','heave_tr','spice_tr']]

title=['EN4 Temp Trend','EN4 Heave Trend','EN4 Spice Trend', 'ORAS5 Temp Trend','ORAS5 Heave Trend','ORAS5 Spice Trend', 'SODA Temp Trend','SODA Heave Trend','SODA Spice Trend']

plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['hatch.linewidth'] = 1
cmap1 = cmc.vik

fig = plt.figure(figsize=(24, 33.936))
gs = gridspec.GridSpec(6, 5, height_ratios=[1,1,1,1,1,1.2], width_ratios=[0.2,1,1,1,0.5])
ax1 = fig.add_subplot(gs[1, 1])
ax2 = fig.add_subplot(gs[1, 2])
ax3 = fig.add_subplot(gs[1, 3])
ax4 = fig.add_subplot(gs[2, 1])
ax5 = fig.add_subplot(gs[2, 2])
ax6 = fig.add_subplot(gs[2, 3])
ax7 = fig.add_subplot(gs[3, 1])
ax8 = fig.add_subplot(gs[3, 2])
ax9 = fig.add_subplot(gs[3, 3])
ax0 = fig.add_subplot(gs[4, 0:4])
ax0.axis('off')
ax0 = fig.add_subplot(gs[5,0:4])
ax0.axis('off')
ax0 = fig.add_subplot(gs[0,0:5])
ax0.axis('off')
ax=[ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9]

for i in ll(dataset.index):
    x, y = np.meshgrid(lat, dataset.loc[dataset.index[i], 'depth'])
    cs=ax[i*3].contourf(x,y,np.nanmean(dataset.loc[dataset.index[i],'trend'], axis=2), cmap=cmap1, levels=np.linspace(-0.2, 0.2, 13), extend='both', zorder=0)
    ax[i*3+1].contourf(x,y,np.nanmean(dataset.loc[dataset.index[i],'heave'], axis=2), cmap=cmap1, levels=np.linspace(-0.2, 0.2, 13), extend='both', zorder=0)
    ax[i*3+2].contourf(x,y,np.nanmean(dataset.loc[dataset.index[i],'spice'], axis=2), cmap=cmap1, levels=np.linspace(-0.2, 0.2, 13), extend='both', zorder=0)

skx, z0_stip, dz_stip, s_stip = 4, 50, 100, 100
zt = np.arange(z0_stip, 2001, dz_stip)
for i in ll(ax):
    x, y = np.meshgrid(lat, dataset.loc[dataset.index[int(i/3)], 'depth'])
    dep = np.asarray(dataset.loc[dataset.index[int(i/3)], 'depth'], dtype=float)
    rows = np.array([np.abs(dep - zz).argmin() for zz in zt])
    cols = np.arange(0, pval[i].shape[1], skx)
    xs, ys = np.meshgrid(np.asarray(lat)[cols], zt)
    sig = pval[i][np.ix_(rows, cols)] < 0.05
    ax[i].scatter(xs[sig], ys[sig], s=s_stip, c='k', marker='.', linewidths=0, zorder=4)
    cs1=ax[i].contour(x,y,np.nanmean(dataset.loc[dataset.index[int(i/3)],'dens'], axis=2), levels=np.arange(27.2, 27.51, 0.1), colors='black', zorder=1)
    labels=ax[i].clabel(cs1, inline=True, inline_spacing=-20, fontsize=25, fmt=lambda x: rf'$\sigma_0$={x:g}', manual=[(-12,700), (-8,800), (-12,1000), (-8,1200)])
    for txt in labels: txt.set_rotation(0)
    ax[i].axvspan(-20, -15, facecolor='none', hatch='//', edgecolor='black', linewidth=0, zorder=5)
    ax[i].axvspan(0, -5, facecolor='none', hatch='//', edgecolor='black', linewidth=0, zorder=5)
    ax[i].set_title('('+chr(97+i)+') '+title[i], fontsize=35, pad=10, loc='left')
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
    if i in [0, 3, 6]: ax[i].set_ylabel('Depth [m]', fontsize=35); ax[i].set_yticks([0,500,1000,1500,2000])
    else: ax[i].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x,_: ''))

    if i in [6, 7, 8]: ax[i].xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: 'Equ' if x == 0 else f'{abs(int(x))}°S')); ax[i].set_xticks([-20,-15,-10,-5,0]); ax[i].tick_params(axis='x', labelrotation=-45)
    else: ax[i].xaxis.set_major_formatter(ticker.FuncFormatter(lambda x,_: ''))

    ax[i].set_aspect(1/140)
cbar_ax1 = fig.add_axes([0.875, 0.4, 0.03, 0.37])
cb1 = fig.colorbar(cs, cax=cbar_ax1, orientation='vertical')
cb1.ax.tick_params(labelsize=35, pad=10)
cb1.set_ticks([-0.2, -0.1, 0, 0.1, 0.2])
cb1.ax.set_yticklabels(['-2', '-1', '0', '1', '2'])
cbar_ax1.text(1.8, 1.14, 'Trend\n [°C/decade] ', fontsize=35, va='top', ha='center', transform=cbar_ax1.transAxes)
cbar_ax1.text(1.8, 1.04, r'$\times 10^{-1}$', fontsize=35, va='top', ha='left', transform=cbar_ax1.transAxes)
for spine in cb1.ax.spines.values(): spine.set_linewidth(2)
plt.subplots_adjust(wspace=0.2)
plt.subplots_adjust(hspace=-0.4)
fig.subplots_adjust(left=0.05, right=0.99, top=1, bottom=0)

plt.savefig(outDIR + '/fig_S02.png', dpi=100, bbox_inches=None, transparent=True)

#%% Figure_S3 S Trend Heave & Spice - all datasets
from functions import *
inDIR = ''
outDIR = ''

EN4=nctopd(inDIR+'/07_EN4.nc')
ORAS5=nctopd(inDIR+'/07_ORAS5.nc')
SODA=nctopd(inDIR+'/07_SODA.nc')
data=[EN4, ORAS5, SODA]

dataset=pd.DataFrame(index=['EN4', 'ORAS5', 'SODA'], columns=['trend', 'heave','spice', 'depth','dens'])

for i in ll(dataset.index):
    dataset.loc[dataset.index[i],'trend']=datacut(data[i],'trend_sr', lonmin=50, lonmax=80, latmin=-20, latmax=1, dmin=0, dmax=2500)['trend_sr'].values
    dataset.loc[dataset.index[i],'heave']=datacut(data[i],'heave_sr', lonmin=50, lonmax=80, latmin=-20, latmax=1, dmin=0, dmax=2500)['heave_sr'].values
    dataset.loc[dataset.index[i],'spice']=datacut(data[i],'spice_sr', lonmin=50, lonmax=80, latmin=-20, latmax=1, dmin=0, dmax=2500)['spice_sr'].values
    dataset.loc[dataset.index[i],'depth']=datacut(data[i],'heave_sr', lonmin=50, lonmax=80, latmin=-20, latmax=1, dmin=0, dmax=2500)['depth']
    dataset.loc[dataset.index[i],'dens']=datacut(data[i],'dens', lonmin=50, lonmax=80, latmin=-20, latmax=1, dmin=0, dmax=2500)['dens']
lon=datacut(EN4,'heave_sr', lonmin=50, lonmax=80, latmin=-20, latmax=1, dmin=0, dmax=2500)['lon']
lat=datacut(EN4,'heave_sr', lonmin=50, lonmax=80, latmin=-20, latmax=1, dmin=0, dmax=2500)['lat']

pval=[data[i]['p_'+v]().sel(lat=slice(-20, 1), depth=slice(0, 2500)).values for i in ll(dataset.index) for v in ['trend_sr','heave_sr','spice_sr']]

title=['EN4 Sali Trend','EN4 Heave Trend','EN4 Spice Trend', 'ORAS5 Sali Trend','ORAS5 Heave Trend','ORAS5 Spice Trend', 'SODA Sali Trend','SODA Heave Trend','SODA Spice Trend']

plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['hatch.linewidth'] = 1
cmap1 = cmc.bam

fig = plt.figure(figsize=(24, 33.936))
gs = gridspec.GridSpec(6, 5, height_ratios=[1,1,1,1,1,1.2], width_ratios=[0.2,1,1,1,0.5])
ax1 = fig.add_subplot(gs[1, 1])
ax2 = fig.add_subplot(gs[1, 2])
ax3 = fig.add_subplot(gs[1, 3])
ax4 = fig.add_subplot(gs[2, 1])
ax5 = fig.add_subplot(gs[2, 2])
ax6 = fig.add_subplot(gs[2, 3])
ax7 = fig.add_subplot(gs[3, 1])
ax8 = fig.add_subplot(gs[3, 2])
ax9 = fig.add_subplot(gs[3, 3])
ax0 = fig.add_subplot(gs[4, 0:4])
ax0.axis('off')
ax0 = fig.add_subplot(gs[5,0:4])
ax0.axis('off')
ax0 = fig.add_subplot(gs[0,0:5])
ax0.axis('off')
ax=[ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8, ax9]

for i in ll(dataset.index):
    x, y = np.meshgrid(lat, dataset.loc[dataset.index[i], 'depth'])
    cs=ax[i*3].contourf(x,y,np.nanmean(dataset.loc[dataset.index[i],'trend'], axis=2), cmap=cmap1, levels=np.linspace(-0.02, 0.02, 13), extend='both', zorder=0)
    ax[i*3+1].contourf(x,y,np.nanmean(dataset.loc[dataset.index[i],'heave'], axis=2), cmap=cmap1, levels=np.linspace(-0.02, 0.02, 13), extend='both', zorder=0)
    ax[i*3+2].contourf(x,y,np.nanmean(dataset.loc[dataset.index[i],'spice'], axis=2), cmap=cmap1, levels=np.linspace(-0.02, 0.02, 13), extend='both', zorder=0)
skx, z0_stip, dz_stip, s_stip = 4, 50, 100, 100
zt = np.arange(z0_stip, 2001, dz_stip)
for i in ll(ax):
    x, y = np.meshgrid(lat, dataset.loc[dataset.index[int(i/3)], 'depth'])
    dep = np.asarray(dataset.loc[dataset.index[int(i/3)], 'depth'], dtype=float)
    rows = np.array([np.abs(dep - zz).argmin() for zz in zt])
    cols = np.arange(0, pval[i].shape[1], skx)
    xs, ys = np.meshgrid(np.asarray(lat)[cols], zt)
    sig = pval[i][np.ix_(rows, cols)] < 0.05
    ax[i].scatter(xs[sig], ys[sig], s=s_stip, c='k', marker='.', linewidths=0, zorder=4)
    cs1=ax[i].contour(x,y,np.nanmean(dataset.loc[dataset.index[int(i/3)],'dens'], axis=2), levels=np.arange(27.2, 27.51, 0.1), colors='black', zorder=1)
    labels=ax[i].clabel(cs1, inline=True, inline_spacing=-20, fontsize=25, fmt=lambda x: rf'$\sigma_0$={x:g}', manual=[(-12,700), (-8,800), (-12,1000), (-8,1200)])
    for txt in labels: txt.set_rotation(0)
    ax[i].axvspan(-20, -15, facecolor='none', hatch='//', edgecolor='black', linewidth=0, zorder=5)
    ax[i].axvspan(0, -5, facecolor='none', hatch='//', edgecolor='black', linewidth=0, zorder=5)
    ax[i].set_title('('+chr(97+i)+') '+title[i], fontsize=35, pad=10, loc='left')
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
    if i in [0, 3, 6]: ax[i].set_ylabel('Depth [m]', fontsize=35); ax[i].set_yticks([0,500,1000,1500,2000])
    else: ax[i].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x,_: ''))

    if i in [6, 7, 8]: ax[i].xaxis.set_major_formatter(ticker.FuncFormatter(lambda x, pos: 'Equ' if x == 0 else f'{abs(int(x))}°S')); ax[i].set_xticks([-20,-15,-10,-5,0]); ax[i].tick_params(axis='x', labelrotation=-45)
    else: ax[i].xaxis.set_major_formatter(ticker.FuncFormatter(lambda x,_: ''))

    ax[i].set_aspect(1/140)
cbar_ax1 = fig.add_axes([0.875, 0.4, 0.03, 0.37])
cb1 = fig.colorbar(cs, cax=cbar_ax1, orientation='vertical')
cb1.ax.tick_params(labelsize=35, pad=10)
cb1.set_ticks([-0.02, -0.01, 0, 0.01, 0.02])
cb1.ax.set_yticklabels(['-2', '-1', '0', '1', '2'])
cbar_ax1.text(1.8, 1.14, 'Trend\n [g/kg·decade] ', fontsize=35, va='top', ha='center', transform=cbar_ax1.transAxes)
cbar_ax1.text(1.8, 1.04, r'$\times 10^{-2}$', fontsize=35, va='top', ha='left', transform=cbar_ax1.transAxes)
for spine in cb1.ax.spines.values(): spine.set_linewidth(2)
plt.subplots_adjust(wspace=0.2)
plt.subplots_adjust(hspace=-0.4)
fig.subplots_adjust(left=0.05, right=0.99, top=1, bottom=0)

plt.savefig(outDIR + '/fig_S03.png', dpi=100, bbox_inches=None, transparent=True)

#%% Figure_S4 T, S on AAIW density surfaces
from functions import *
inDIR = ''
outDIR = ''
ARGO = inDIR + '/03_ARGO.nc'

ARGO = nctopd(ARGO)
ARGO._ds = ARGO._ds.sortby(['lat','lon']).sel(lat=slice(-70, 0), lon=slice(40, 120))
[setattr(v, '_ds', ARGO._ds) for _, v in ARGO.items() if hasattr(v, '_ds')]

res = interp_ARGO_to_density(ARGO, densmin=27.2, densmax=27.5, densinterval=0.1, compute=True, n_threads=os.cpu_count())

plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'Times New Roman'
plt.rcParams['text.usetex'] = True

lon2d, lat2d = np.meshgrid(ARGO['lon']().values, ARGO['lat']().values)

data_list = []
p_list = []
for i in range(4):
    sl, _, _, pv, _, _ = litrend(res['temp'].isel(density=i).rename('temp'), 'temp', s='2004-01-01', f='2023-12-31', rm_season=True, ar1=False, return_stats=True)
    data_list.append(sl.transpose('lat','lon').values * 10.0); p_list.append(pv.transpose('lat','lon').values)
for i in range(4):
    sl, _, _, pv, _, _ = litrend(res['sali'].isel(density=i).rename('sali'), 'sali', s='2004-01-01', f='2023-12-31', rm_season=True, ar1=False, return_stats=True)
    data_list.append(sl.transpose('lat','lon').values * 100.0); p_list.append(pv.transpose('lat','lon').values)
title_list = [r'(a) $\sigma_0$ 27.2', r'(b) $\sigma_0$ 27.3', r'(c) $\sigma_0$ 27.4', r'(d) $\sigma_0$ 27.5', r'(e) $\sigma_0$ 27.2', r'(f) $\sigma_0$ 27.3', r'(g) $\sigma_0$ 27.4', r'(h) $\sigma_0$ 27.5']
levels_list = [np.arange(-4, 4.1, 0.1), np.arange(-2, 2.1, 0.1)]
cmap_list = [cmc.vik, cmc.bam]
cbar_labels = [r'Temperature Trend [$\times 10^{-1}$ $^\circ$C decade$^{-1}$]', r'Salinity Trend [$\times 10^{-2}$ g kg$^{-1}$ decade$^{-1}$]']
cbar_ticks = [[-4, -2, 0, 2, 4], [-2, -1, 0, 1, 2]]
cbar_ticklabels = [['-4', '-2', '0', '2', '4'], ['-2', '-1', '0', '1', '2']]

proj = ccrs.SouthPolarStereo(central_longitude=80)
pc = ccrs.PlateCarree()

fig = plt.figure(figsize=(24, 33.936))
gs = gridspec.GridSpec(4, 4, height_ratios=[1, 1, 1, 1], width_ratios=[1, 1, 1, 1])
ax1 = fig.add_subplot(gs[1, 0], projection=proj)
ax2 = fig.add_subplot(gs[1, 1], projection=proj)
ax3 = fig.add_subplot(gs[1, 2], projection=proj)
ax4 = fig.add_subplot(gs[1, 3], projection=proj)
ax5 = fig.add_subplot(gs[2, 0], projection=proj)
ax6 = fig.add_subplot(gs[2, 1], projection=proj)
ax7 = fig.add_subplot(gs[2, 2], projection=proj)
ax8 = fig.add_subplot(gs[2, 3], projection=proj)
axes = [ax1, ax2, ax3, ax4, ax5, ax6, ax7, ax8]

ax0 = fig.add_subplot(gs[0, 0:4])
ax0.axis('off')
ax0 = fig.add_subplot(gs[3, 0:4])
ax0.axis('off')

mappables = [None, None]
for i in ll(axes):
    axes[i].set_extent([40, 120, -90, 0], crs=pc)
    make_annular_sector_boundary(axes[i], proj, lonmin=40, lonmax=120, inner_lat=-70, outer_lat=0)
    axes[i].set_facecolor('white')
    cs = axes[i].contourf(lon2d, lat2d, data_list[i], levels=levels_list[int(i/4)], cmap=cmap_list[int(i/4)], extend='both', transform=pc)
    k = p_list[i][::8, ::8] < 0.05
    axes[i].scatter(lon2d[::8, ::8][k], lat2d[::8, ::8][k], s=40, c='k', marker='.', linewidths=0, transform=pc, zorder=4)
    axes[i].add_feature(cfeature.LAND, facecolor='lightgray', edgecolor='none', zorder=2)
    axes[i].coastlines(linewidth=0.3, zorder=3)
    axes[i].gridlines(crs=pc, draw_labels=False, xlocs=[40,60,80,100,120], ylocs=[0,-20,-40,-60], linewidth=0.7, color='gray', linestyle=(0, (2, 2)), zorder=1)
    add_custom_geo_labels(axes[i], [60,80,100], [0,-20,-40,-60], 40, top_lat=2.8, side_offset=2.5, fs=35)
    add_custom_geo_labels(axes[i], [40,120], [], 40, top_lat=5, side_offset=2.5, fs=35)
    draw_box(axes[i], 50, 80, -15, -5, color='black', lw=3, zorder=8)
    axes[i].set_title(title_list[i], fontsize=35, pad=68)
    axes[i].spines['geo'].set_linewidth(2)
    if mappables[int(i/4)] is None: mappables[int(i/4)] = cs

fig.canvas.draw()

pos00 = axes[0].get_position()
pos03 = axes[3].get_position()
pos10 = axes[4].get_position()
row_width = pos03.x1 - pos00.x0
cbar_width = row_width * 0.5
cbar_x0 = pos00.x0 + 0.5 * (row_width - cbar_width)
cax_temp = fig.add_axes([cbar_x0, pos00.y0 + 0 - 0.01, cbar_width, 0.01])
cax_sali = fig.add_axes([cbar_x0, pos10.y0 + -0.01 - 0.01, cbar_width, 0.01])
caxes = [cax_temp, cax_sali]

for i in range(2):
    cb = fig.colorbar(mappables[i], cax=caxes[i], orientation='horizontal')
    cb.set_label(cbar_labels[i], fontsize=35, labelpad=5)
    cb.set_ticks(cbar_ticks[i])
    cb.set_ticklabels(cbar_ticklabels[i])
    cb.ax.tick_params(labelsize=35, length=8, width=2)
    for spine in cb.ax.spines.values(): spine.set_linewidth(2)

plt.subplots_adjust(wspace=0.35)
plt.subplots_adjust(hspace=-0.45)
fig.subplots_adjust(left=0.05, right=0.98, top=1, bottom=0)
plt.savefig(outDIR + '/fig_S04.png', dpi=100, bbox_inches=None, transparent=True)
plt.show()

#%% Figure_S5 Sea-level budget monthly timeseries - SL, OMESL, SSL
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
plt.savefig(outDIR + '/fig_S05.png', dpi=100, bbox_inches=None, transparent=True)
