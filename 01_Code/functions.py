import pandas as pd
import os
import numpy as np
import numpy.ma as ma
from mpl_toolkits.basemap import Basemap
import matplotlib.path as mpath
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import gsw
import warnings
import matplotlib.cm as cm
from datetime import datetime, timedelta
import copy
from scipy.stats import linregress
from scipy.stats import t as student_t
import xarray as xr
from IPython import get_ipython
from numba import njit, prange, set_num_threads
from joblib import Parallel, delayed
from scipy.sparse import coo_matrix
import multiprocessing as mp
import dask
from matplotlib.lines import Line2D
from matplotlib import colors
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import dates, colorbar, rc, scale, transforms, colormaps
import matplotlib
from matplotlib.ticker import FixedLocator
import matplotlib.ticker as ticker
import matplotlib.gridspec as gridspec
import cmcrameri.cm as cmc
from matplotlib.gridspec import GridSpec
from matplotlib.path import Path
from matplotlib.offsetbox import AnchoredOffsetbox, DrawingArea, TextArea, HPacker, VPacker
matplotlib.rcParams['text.usetex'] = True
warnings.filterwarnings("ignore", message="Calling a ufunc on non-aligned DataFrames.*")
warnings.filterwarnings("ignore", category=RuntimeWarning)
os.environ.setdefault("MKL_NUM_THREADS","1")
os.environ.setdefault("OPENBLAS_NUM_THREADS","1")
os.environ.setdefault("OMP_NUM_THREADS","1")
matplotlib.rcParams.update({"text.usetex": True, "font.family": "serif", "text.latex.preamble": r"\usepackage{amsmath}\usepackage{newtxtext}\usepackage{newtxmath}"})
class _LazyRef:
    def __init__(self, ds, key):
        self._ds = ds
        self._key = key
    def __call__(self):
        return self._ds[self._key]
    def __repr__(self):
        return f"<lazy:{self._key}>"
def mbox(m, s_lon,b_lon,s_lat,b_lat,color,linewidth,z):
    m=m
    a = m(s_lon, s_lat)
    b = m(b_lon, s_lat)
    d = m(s_lon, b_lat)
    c = m(b_lon, b_lat)
    box_x = [a[0], b[0], c[0], d[0], a[0]]
    box_y = [a[1], b[1], c[1], d[1], a[1]]
    m.plot(box_x, box_y, color=color, linewidth=linewidth, zorder=z, clip_on=False)
def ll(a):
    return list(range(len(a)))
def trend(x,y):
    try:
        mask = ~np.isnan(x) & ~np.isnan(y)
        x = x[mask]
        y = y[mask]
        slope, intercept, r_value, p_value, std_err = linregress(x, y)
    except:
        x = mdates.date2num(x)
        mask = ~np.isnan(x) & ~np.isnan(y)
        x = x[mask]
        y = y[mask]
        slope, intercept, r_value, p_value, std_err = linregress(x, y)
    trend = slope * x + intercept
    return trend
def grace_month(var3d, time_bounds, tgt_index, max_gap=2):
    tb = np.asarray(time_bounds, dtype='datetime64[ns]')
    b0 = pd.DatetimeIndex(tb[:, 0]); b1 = pd.DatetimeIndex(tb[:, 1])
    mid = b0 + (b1 - b0) / 2
    mon = pd.DatetimeIndex(np.asarray(pd.PeriodIndex(mid, freq='M').to_timestamp().values, dtype='datetime64[ns]'))
    tgt = pd.DatetimeIndex(np.asarray(pd.DatetimeIndex(tgt_index).values, dtype='datetime64[ns]'))
    arr = np.asarray(var3d, dtype='float64')
    nt = tgt.size
    out = np.full((nt,) + arr.shape[1:], np.nan)
    ep = np.full(nt, np.datetime64('NaT'), dtype='datetime64[ns]')
    pos = {t: i for i, t in enumerate(tgt)}
    for t in pd.DatetimeIndex(np.unique(mon)):
        i = pos.get(t)
        if i is None:
            continue
        k = np.where(mon == t)[0]
        out[i] = np.nanmean(arr[k], axis=0)
        ep[i] = mid[k].values.astype('datetime64[ns]').astype('int64').mean().astype('int64').astype('datetime64[ns]')
    have = ~np.isnat(ep)
    if max_gap and have.sum() >= 2:
        xi = np.arange(nt)
        vi = xi[have]
        li = np.searchsorted(vi, xi, side='right') - 1
        inside = (~have) & (li >= 0) & (li + 1 < vi.size)
        if inside.any():
            L = vi[li[inside]]; R = vi[li[inside] + 1]
            w = ((xi[inside] - L) / (R - L)).reshape((-1,) + (1,) * (arr.ndim - 1))
            out[inside] = out[L] * (1.0 - w) + out[R] * w
        run = 0
        for i in range(nt):
            if have[i]:
                if run > max_gap:
                    out[i - run:i] = np.nan
                run = 0
            else:
                run += 1
        if run > max_gap:
            out[nt - run:] = np.nan
    cen = np.asarray((tgt + pd.to_timedelta(tgt.days_in_month / 2.0, unit='D')).values, dtype='datetime64[ns]')
    epoch = pd.DatetimeIndex(np.where(have, ep, cen))
    return out, epoch
def nctopd(filepath, drop_bounds=True, decode_times=True, align_chunks=True, fallback_chunks=None):
    dask.config.set({"array.slicing.split_large_chunks": True})
    drop_vars = ["time_bnds","time_bounds","depth_bnds","depth_bounds","lat_bounds","lon_bounds"] if drop_bounds else None
    ds = xr.open_dataset(filepath, engine=None, chunks=None, cache=False, mask_and_scale=True, decode_times=decode_times, drop_variables=drop_vars)
    if align_chunks:
        votes = {}
        for v in ds.data_vars.values():
            cs = v.encoding.get("chunksizes", None)
            if cs is None: continue
            for d, c in zip(v.dims, cs):
                if c is None: continue
                votes.setdefault(d, []).append(int(c))
        ck = {}
        for d, arr in votes.items():
            s = pd.Series(arr)
            ck[d] = int(s.mode().iloc[0]) if not s.mode().empty else int(s.iloc[0])
        if ck:
            ds = ds.chunk(ck)
        elif fallback_chunks:
            ds = ds.chunk({k:int(v) for k,v in fallback_chunks.items()})
    elif fallback_chunks:
        ds = ds.chunk({k:int(v) for k,v in fallback_chunks.items()})
    keys = list(ds.coords) + list(ds.data_vars)
    s = pd.Series({k: _LazyRef(ds, k) for k in keys}, dtype=object)
    s._ds = ds
    ip = get_ipython()
    if ip is not None:
        base = os.path.splitext(os.path.basename(filepath))[0]
        safe = "idx_" + "".join(c if c.isalnum() or c=="_" else "_" for c in base)
        ip.user_ns[safe] = list(s.keys())
    return s
_load_cache = {}
def load(n, inDIR):
    key = (inDIR, n)
    if key not in _load_cache:
        _load_cache[key] = nctopd(inDIR + '/05_' + n + '.nc')
    return _load_cache[key]
def pdtonc(series, filepath, coord_names=None, mode="w", engine="h5netcdf", compress=False, complevel=1, time_chunk=24, depth_chunk=None, lat_chunk=None, lon_chunk=None, use_threads=True):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    if coord_names is None:
        coord_names = {"time","lon","lat","depth", "time_bnds","time_bounds","depth_bnds","depth_bounds","lat_bounds","lon_bounds", "xt_ocean","yt_ocean","xu_ocean","yu_ocean","st_ocean","sw_ocean", "time_counter","nav_lon","nav_lat","level","longitude","latitude", "date","timePlot","deptht", "pressure"}
    if ("dept" in series) and ("depth" not in series):
        series["depth"] = series.pop("dept")
    def _resolve(v):
        if callable(v) and hasattr(v, "_ds"):
            return v()
        return v
    def _as_array(v):
        if isinstance(v, xr.DataArray):
            return v
        if isinstance(v, pd.Series):
            return np.asarray(v.to_numpy())
        if isinstance(v, (pd.DatetimeIndex,)):
            return np.asarray(v)
        return np.asarray(v)
    coords, data_vars = {}, {}
    for k, v in series.items():
        vv = _resolve(v)
        if k in coord_names:
            if isinstance(vv, xr.DataArray):
                coords[k] = vv
            else:
                aa = _as_array(vv)
                if aa.ndim == 0:
                    aa = aa.reshape((1,))
                coords[k] = xr.DataArray(aa, dims=(k,) if aa.ndim==1 else tuple(f"{k}_dim{i}" for i in range(aa.ndim)))
        else:
            aa = _as_array(vv)
            if isinstance(vv, xr.DataArray):
                data_vars[k] = vv
            else:
                if aa.ndim == 4:
                    data_vars[k] = xr.DataArray(aa, dims=("time","depth","lat","lon"))
                elif aa.ndim == 3:
                    try:
                        data_vars[k] = xr.DataArray(aa, dims=("time","lat","lon"))
                    except ValueError:
                        data_vars[k] = xr.DataArray(aa, dims=("depth","lat","lon"))
                elif aa.ndim == 2:
                    data_vars[k] = xr.DataArray(aa, dims=("lat","lon"))
                elif aa.ndim == 1:
                    target = None
                    for c in ("time","depth","lat","lon"):
                        if c in series and _as_array(series[c]).shape[:1]==aa.shape[:1]:
                            target = c; break
                    data_vars[k] = xr.DataArray(aa, dims=(target if target else f"{k}_dim0",))
                else:
                    data_vars[k] = xr.DataArray(aa, dims=(f"{k}_dim0",))

    ds = xr.Dataset(data_vars=data_vars, coords=coords)

    if "lon" in ds:
        lonv = np.asarray(ds["lon"].values, dtype="float64")
        lonv = ((lonv + 180) % 360) - 180
        ds = ds.assign_coords(lon=lonv)
        ds["lon"].attrs.update({"units":"degrees_east","standard_name":"longitude"})
    if "lat" in ds:
        latv = np.asarray(ds["lat"].values, dtype="float64")
        ds = ds.assign_coords(lat=latv)
        ds = ds.sortby(["lat","lon"])
        ds["lat"].attrs.update({"units":"degrees_north","standard_name":"latitude"})
    if "depth" in ds:
        ds = ds.assign_coords(depth=ds["depth"].astype("float32"))
        ds["depth"].attrs.update({"standard_name":"depth","positive":"down"})
    if "time" in ds:
        if not np.issubdtype(ds["time"].dtype, np.datetime64):
            ds = ds.assign_coords(time=pd.DatetimeIndex(np.asarray(ds["time"].values)))
        ds["time"].attrs.update({"standard_name":"time"})
        ds["time"].encoding.update({"units":"days since 1970-01-01","calendar":"standard"})

    for k in list(ds.data_vars):
        v = ds[k]
        if set(v.dims)=={"time","depth","lat","lon"}:
            ds[k] = v.transpose("time","depth","lat","lon", missing_dims="ignore").astype("float32")
        elif set(v.dims)=={"time","lat","lon"}:
            ds[k] = v.transpose("time","lat","lon", missing_dims="ignore").astype("float32")
        elif set(v.dims)=={"lat","lon"}:
            ds[k] = v.transpose("lat","lon", missing_dims="ignore").astype("float32")
        else:
            ds[k] = v.astype("float32")
        ds[k].attrs.pop("_FillValue", None)

    if use_threads:
        dask.config.set(scheduler="threads", num_workers=min(32, mp.cpu_count()))

    dims = ds.sizes
    tN = int(dims.get("time", 1))
    dN = int(dims.get("depth", 1))
    yN = int(dims.get("lat", 1))
    xN = int(dims.get("lon", 1))

    tc = min(time_chunk, tN) if tN>1 and time_chunk else tN
    dc = min(depth_chunk if depth_chunk else dN, dN)
    yc = min(lat_chunk if lat_chunk else yN, yN)
    lc = min(lon_chunk if lon_chunk else xN, xN)

    ds = ds.chunk({k: v for k, v in [("time", tc), ("depth", dc), ("lat", yc), ("lon", lc)] if k in dims})

    for k in list(ds.data_vars):

        v = ds[k]
        enc = {"_FillValue": np.float32(1e20)}
        if compress:
            enc.update({"zlib": True, "complevel": int(complevel)})
        else:
            enc.update({"zlib": False})
        if set(v.dims)=={"time","depth","lat","lon"}:
            enc.update({"chunksizes": (tc if "time" in dims else 1, dc if "depth" in dims else 1, yc if "lat" in dims else 1, lc if "lon" in dims else 1)})
        elif set(v.dims)=={"time","lat","lon"}:
            enc.update({"chunksizes": (tc if "time" in dims else 1, yc if "lat" in dims else 1, lc if "lon" in dims else 1)})
        elif set(v.dims)=={"lat","lon"}:
            enc.update({"chunksizes": (yc if "lat" in dims else 1, lc if "lon" in dims else 1)})
        ds[k].encoding.update(enc)
    if "depth" in ds.dims:
        depN = ds.sizes["depth"]
        for k in list(ds.data_vars):
            v = ds[k]
            if v.ndim == 1 and ("depth" not in v.dims):
                d0 = v.dims[0]
                if v.sizes[d0] == depN:
                    ds[k] = v.rename({d0: "depth"}).assign_coords(depth=ds["depth"])
    ds.to_netcdf(filepath, engine="netcdf4", mode=mode, compute=True)
    ds.close()
def regrid(*, data=None, data1=None, latfrom=None, lonfrom=None, latto=None, lonto=None, n_jobs=-1, backend='threading'):
    def ensure_ascending(ax_vals, fld, kind):
        if fld is None:
            return ax_vals, None
        if kind == "lat":
            if np.any(np.diff(ax_vals) < 0):
                ax_vals = ax_vals[::-1]
                fld = fld[..., ::-1, :]
        else:
            if np.any(np.diff(ax_vals) < 0):
                ax_vals = ax_vals[::-1]
                fld = fld[..., :, ::-1]
        return ax_vals, fld

    def edges_from_centers(centers):
        centers = np.asarray(centers)
        e = np.empty(centers.size + 1, dtype=float)
        e[1:-1] = 0.5 * (centers[:-1] + centers[1:])
        e[0] = centers[0] - 0.5 * (centers[1] - centers[0])
        e[-1] = centers[-1] + 0.5 * (centers[-1] - centers[-2])
        return e

    def align_var_axes(var, nlat, nlon):
        var = np.asarray(var)
        if var.ndim >= 2:
            if var.shape[-2] == nlon and var.shape[-1] == nlat:
                var = np.swapaxes(var, -1, -2)
        return var

    def build_area_weight_matrix(latf, lonf, latt, lont, R=6371000.0):
        latf_b = edges_from_centers(latf)
        lonf_b = edges_from_centers(lonf)
        latt_b = edges_from_centers(latt)
        lont_b = edges_from_centers(lont)
        s_dst = np.sin(np.deg2rad(latt_b))
        A_dst = (R**2) * np.diff(s_dst)[:, None] * np.deg2rad(np.diff(lont_b))[None, :]
        rows, cols, data_w = [], [], []
        n_latt, n_lont = len(latt), len(lont)
        n_latf, n_lonf = len(latf), len(lonf)
        for j in range(n_latt):
            lat0, lat1 = latt_b[j], latt_b[j+1]
            i0 = np.searchsorted(latf_b, lat0, side='right') - 1
            i1 = np.searchsorted(latf_b, lat1, side='left')
            for i in range(max(i0,0), min(i1, n_latf-1)+1):
                olat0 = max(lat0, latf_b[i]); olat1 = min(lat1, latf_b[i+1])
                if olat1 <= olat0:
                    continue
                s_olat = np.sin(np.deg2rad([olat0, olat1])); dA_lat = s_olat[1] - s_olat[0]
                for l in range(n_lont):
                    lon0, lon1 = lont_b[l], lont_b[l+1]
                    k0 = np.searchsorted(lonf_b, lon0, side='right') - 1
                    k1 = np.searchsorted(lonf_b, lon1, side='left')
                    for k in range(max(k0,0), min(k1, n_lonf-1)+1):
                        olon0 = max(lon0, lonf_b[k]); olon1 = min(lon1, lonf_b[k+1])
                        if olon1 <= olon0:
                            continue
                        dA_lon = np.deg2rad(olon1 - olon0)
                        w = (R**2) * dA_lon * dA_lat / A_dst[j, l]
                        rows.append(j*n_lont + l); cols.append(i*n_lonf + k); data_w.append(w)
        W = coo_matrix((data_w, (rows, cols)), shape=(n_latt*n_lont, n_latf*n_lonf)).tocsr()
        return W

    def apply_W_stack(var, W, nlat, nlon):
        if var is None:
            return None
        var = align_var_axes(var, len(latfrom), len(lonfrom))
        squeezed = False
        if var.ndim == 2:
            var = var[np.newaxis, ...]
            squeezed = True
        lead = var.shape[:-2]
        stack = int(np.prod(lead)) if lead else 1
        arr = var.reshape((stack, var.shape[-2], var.shape[-1]))
        def _apply(i):
            return (W @ arr[i].ravel()).reshape(nlat, nlon)
        out = Parallel(n_jobs=n_jobs, backend=backend, require='sharedmem')(delayed(_apply)(i) for i in range(stack))
        out = np.asarray(out).reshape((*lead, nlat, nlon))
        if squeezed:
            out = out[0]
        return out

    latfrom, data = ensure_ascending(latfrom, data, "lat") if data is not None else (latfrom, None)
    lonfrom, data = ensure_ascending(lonfrom, data, "lon") if data is not None else (lonfrom, None)
    if data1 is not None:
        latfrom, data1 = ensure_ascending(latfrom, data1, "lat")
        lonfrom, data1 = ensure_ascending(lonfrom, data1, "lon")

    W = build_area_weight_matrix(latfrom, lonfrom, latto, lonto)
    out0 = apply_W_stack(data, W, len(latto), len(lonto))
    out1 = apply_W_stack(data1, W, len(latto), len(lonto)) if data1 is not None else None

    if out0 is not None and out1 is not None:
        return out0, out1
    return out0 if out0 is not None else out1
def pdlabel(data, mode, a, a1=None, *args):
    ds = data._ds

    def _listify(x):
        return [x] if isinstance(x, str) else list(x)

    def _as_da(v, dims=None):
        if hasattr(v, "_ds"):
            v = v()
        if isinstance(v, xr.DataArray):
            return v
        arr = np.asarray(v)
        if arr.ndim == 0:
            arr = arr.reshape((1,))
        if dims is None:
            dims = tuple(f"dim{i}" for i in range(arr.ndim))
        return xr.DataArray(arr, dims=dims)

    def _coord_da(v, name):
        if hasattr(v, "_ds"):
            v = v()
        if isinstance(v, xr.DataArray):
            out = v.copy(deep=False)
            if out.ndim == 0:
                out = xr.DataArray(np.asarray(out.values).reshape((1,)), dims=(name,))
            elif out.ndim == 1:
                if out.dims != (name,):
                    out = out.rename({out.dims[0]: name})
            return out
        arr = np.asarray(v)
        if arr.ndim == 0:
            arr = arr.reshape((1,))
        if arr.ndim != 1:
            return xr.DataArray(arr, dims=tuple(f"{name}_dim{i}" for i in range(arr.ndim)))
        return xr.DataArray(arr, dims=(name,))

    if mode == "fix":
        olds = _listify(a)
        news = _listify(a1)
        ds = ds.rename({o: n for o, n in zip(olds, news)})

    elif mode == "del":
        targets = _listify(a)
        dv = [n for n in targets if n in ds.data_vars]
        dc = [n for n in targets if n in ds.coords]
        if dv:
            ds = ds.drop_vars(dv)
        if dc:
            ds = ds.drop_vars(dc)

    elif mode == "data":

        pairs = [(a, a1)]
        if args:
            pairs.extend([(args[i], args[i + 1]) for i in range(0, len(args), 2)])

        coord_pairs = [(n, v) for n, v in pairs if n in ds.coords]

        for name, val0 in coord_pairs:
            v_da = _coord_da(val0, name)
            cur = ds.coords[name]
            if cur.ndim != 1 or v_da.ndim != 1:
                continue
            cur_vals = np.asarray(cur.values)
            new_vals = np.asarray(v_da.values)
            same_size = new_vals.size == cur_vals.size
            same_value = same_size and np.array_equal(new_vals, cur_vals)
            if not same_value:
                mask = cur.isin(v_da)
                ds = ds.isel({name: mask})

        for name, val0 in coord_pairs:
            ds = ds.assign_coords({name: _coord_da(val0, name)})

        KNOWN = {"time", "depth", "lat", "lon"}
        LENS = {d: int(ds.sizes[d]) for d in ds.sizes if d in KNOWN}

        def _infer_dims(shape, L, varname):
            prefer = ["time", "depth", "lat", "lon"]
            used = set()
            out = []
            for s in shape:
                cand = [n for n in prefer if (n in L and L[n] == s and n not in used)]
                if not cand:
                    cand = [n for n, ln in L.items() if ln == s and n not in used]
                pick = cand[0] if cand else f"{varname}_dim{len(out)}"
                out.append(pick)
                if cand:
                    used.add(pick)
            return tuple(out)

        for name, val0 in pairs:
            if name in ds.coords:
                continue

            if hasattr(val0, "_ds"):
                val0 = val0()

            if isinstance(val0, xr.DataArray):
                if set(val0.dims).issubset(KNOWN):
                    val = val0.copy(deep=False)
                else:
                    val = xr.DataArray(val0.data, dims=_infer_dims(val0.shape, LENS, name), attrs=val0.attrs)
            else:
                arr = np.asarray(val0)
                if arr.ndim == 0:
                    arr = arr.reshape((1,))
                dims = tuple(ds[name].dims) if name in ds else _infer_dims(arr.shape, LENS, name)
                val = xr.DataArray(arr, dims=dims)

            if name in ds:
                tgt = ds[name]
                val = val.transpose(*tgt.dims, missing_dims="ignore")
                for d in tgt.dims:
                    if d in ds.coords:
                        val = val.assign_coords({d: ds.coords[d]})
                if hasattr(tgt, "dtype") and val.dtype != tgt.dtype:
                    val = val.astype(tgt.dtype, copy=False)
                attrs = dict(tgt.attrs)
                ds = ds.drop_vars(name)
                ds[name] = val
                ds[name].attrs.update(attrs)
            else:
                for d in val.dims:
                    if d in ds.coords:
                        val = val.assign_coords({d: ds.coords[d]})
                ds[name] = val

    keys = list(ds.coords) + list(ds.data_vars)
    out = pd.Series({k: _LazyRef(ds, k) for k in keys}, dtype=object)
    out._ds = ds
    return out
def ctas(data, temptype="c", salitype="ps", chunks=None, workers=None):

    T = data["temp"]() if hasattr(data["temp"], "_ds") else data["temp"]
    S = data["sali"]() if hasattr(data["sali"], "_ds") else data["sali"]
    depth = data["depth"]() if hasattr(data["depth"], "_ds") else data["depth"]
    lat = data["lat"]() if hasattr(data["lat"], "_ds") else data["lat"]
    lon = data["lon"]() if hasattr(data["lon"], "_ds") else data["lon"]

    if not isinstance(T, xr.DataArray): T = xr.DataArray(np.asarray(T), dims=("time","depth","lat","lon"))
    if not isinstance(S, xr.DataArray): S = xr.DataArray(np.asarray(S), dims=("time","depth","lat","lon"))
    if not isinstance(depth, xr.DataArray): depth = xr.DataArray(np.asarray(depth), dims=("depth",))
    if not isinstance(lat, xr.DataArray): lat = xr.DataArray(np.asarray(lat), dims=("lat",))
    if not isinstance(lon, xr.DataArray): lon = xr.DataArray(np.asarray(lon), dims=("lon",))

    if chunks is None:
        tN = int(T.sizes.get("time", 1)); dN = int(T.sizes.get("depth", 1))
        yN = int(T.sizes.get("lat", 1)); xN = int(T.sizes.get("lon", 1))
        chunks = {"time": min(16, max(4, tN)), "depth": min(16, max(4, dN)), "lat": min(256, max(64, yN)), "lon": min(256, max(64, xN))}
    T = T.astype("float32").chunk(chunks)
    S = S.astype("float32").chunk(chunks)

    depth = depth.astype("float64").chunk({"depth": -1})
    lat = lat.astype("float64").chunk({"lat": -1})
    lon = lon.astype("float64").chunk({"lon": -1})

    if temptype.lower() == "k": T = T - 273.15

    for v in (T, S):
        fv = v.encoding.get("_FillValue", None)
        if fv is not None: v.data = xr.where(xr.ufuncs.isfinite(v), v, np.nan)
    S = xr.where((S>=0) & (S<1e4), S, np.nan)

    z1d = xr.where(depth > 0, -depth, depth)
    z4d = xr.broadcast(z1d, T)[0]
    lat4d = xr.broadcast(lat, T)[0]
    lon4d = xr.broadcast(lon, T)[0]

    guf = {"allow_rechunk": True}

    P = xr.apply_ufunc(gsw.p_from_z, z4d, lat4d, input_core_dims=[[],[]], output_core_dims=[[]], dask="parallelized", vectorize=False, output_dtypes=[np.float64], dask_gufunc_kwargs=guf)

    if salitype.lower() == "ps":
        SA = xr.apply_ufunc(gsw.SA_from_SP, S, P, lon4d, lat4d, input_core_dims=[[],[],[],[]], output_core_dims=[[]], dask="parallelized", vectorize=False, output_dtypes=[np.float32], dask_gufunc_kwargs=guf)
    elif salitype.lower() == "as":
        SA = S.astype("float32")

    CT = xr.apply_ufunc(gsw.CT_from_pt, SA, T, input_core_dims=[[],[]], output_core_dims=[[]], dask="parallelized", vectorize=False, output_dtypes=[np.float32], dask_gufunc_kwargs=guf)

    CT = CT.transpose("time","depth","lat","lon", missing_dims="ignore")
    SA = SA.transpose("time","depth","lat","lon", missing_dims="ignore")
    return CT, SA
def specvol(data, chunks=None, return_pressure=False):

    ct_name='temp'
    sa_name="sali"
    CT = data[ct_name]() if hasattr(data[ct_name], "_ds") else data[ct_name]
    SA = data[sa_name]() if hasattr(data[sa_name], "_ds") else data[sa_name]
    depth = data["depth"]() if hasattr(data["depth"], "_ds") else data["depth"]
    lat = data["lat"]() if hasattr(data["lat"], "_ds") else data["lat"]
    lon = data["lon"]() if hasattr(data["lon"], "_ds") else data["lon"]

    if not isinstance(CT, xr.DataArray): CT = xr.DataArray(np.asarray(CT), dims=("time","depth","lat","lon"))
    if not isinstance(SA, xr.DataArray): SA = xr.DataArray(np.asarray(SA), dims=("time","depth","lat","lon"))
    if not isinstance(depth, xr.DataArray): depth = xr.DataArray(np.asarray(depth), dims=("depth",))
    if not isinstance(lat, xr.DataArray): lat = xr.DataArray(np.asarray(lat), dims=("lat",))
    if not isinstance(lon, xr.DataArray): lon = xr.DataArray(np.asarray(lon), dims=("lon",))

    if chunks is None:
        tN = int(CT.sizes.get("time", 1)); dN = int(CT.sizes.get("depth", 1))
        yN = int(CT.sizes.get("lat", 1)); xN = int(CT.sizes.get("lon", 1))
        chunks = {"time": min(16, max(4, tN)), "depth": min(16, max(4, dN)), "lat": min(256, max(64, yN)), "lon": min(256, max(64, xN))}
    CT = CT.astype("float32").chunk(chunks)
    SA = SA.astype("float32").chunk(chunks)
    depth = depth.astype("float64").chunk({"depth": -1})
    lat = lat.astype("float64").chunk({"lat": -1})
    lon = lon.astype("float64").chunk({"lon": -1})

    for v in (CT, SA):
        fv = v.encoding.get("_FillValue", None)
        if fv is not None:
            v.data = xr.where(xr.ufuncs.isfinite(v), v, np.nan)
    SA = xr.where((SA>=0) & (SA<1e4), SA, np.nan)

    z1d = xr.where(depth > 0, -depth, depth)
    z4d = xr.broadcast(z1d, CT)[0]
    lat4 = xr.broadcast(lat, CT)[0]

    guf = {"allow_rechunk": True}
    P = xr.apply_ufunc(gsw.p_from_z, z4d, lat4, input_core_dims=[[],[]], output_core_dims=[[]], dask="parallelized", vectorize=False, output_dtypes=[np.float64], dask_gufunc_kwargs=guf)

    sv = xr.apply_ufunc(gsw.specvol, SA.astype("float64"), CT.astype("float64"), P, input_core_dims=[[],[],[]], output_core_dims=[[]], dask="parallelized", vectorize=False, output_dtypes=[np.float64], dask_gufunc_kwargs=guf).astype("float32")

    sv = sv.transpose("time","depth","lat","lon", missing_dims="ignore")
    sv.name = "specvol"
    sv.attrs.update({"units":"m^3 kg^-1", "standard_name":"specific_volume", "long_name":"Specific volume (TEOS-10)"})

    return (sv, P) if return_pressure else sv
def specvolts(data, mode, profile, chunks=None, return_pressure=False):
    def _get(obj):
        return obj() if hasattr(obj, "_ds") else obj

    def _coord_to_da(obj, name):
        obj = _get(obj)
        if isinstance(obj, xr.DataArray):
            da = obj.squeeze(drop=True)
            if da.dims[0] != name:
                da = da.rename({da.dims[0]: name})
        else:
            da = xr.DataArray(np.asarray(obj), dims=(name,))
        return da.astype("float64")

    def _field_to_da(obj, name, depth, lat, lon):
        obj = _get(obj)
        if isinstance(obj, xr.DataArray):
            da = obj
            da = da.transpose("time", "depth", "lat", "lon")
            da = da.assign_coords(depth=depth, lat=lat, lon=lon)
        else:
            arr = np.asarray(obj)
            da = xr.DataArray(arr, dims=("time", "depth", "lat", "lon"), coords={"depth": depth, "lat": lat, "lon": lon})
        return da

    def _profile_to_da(profile, depth, lat, lon, chunks):
        if isinstance(profile, xr.DataArray):
            prof = profile.squeeze(drop=True)

            if prof.ndim == 1:
                if "depth" not in prof.dims:
                    if len(prof.dims) == 1 and prof.sizes[prof.dims[0]] == depth.size:
                        prof = prof.rename({prof.dims[0]: "depth"})
                prof = prof.transpose("depth")
                prof = prof.assign_coords(depth=depth)
                prof = prof.chunk({"depth": chunks["depth"]})

            elif prof.ndim == 3:
                prof = prof.transpose("depth", "lat", "lon")
                prof = prof.assign_coords(depth=depth, lat=lat, lon=lon)
                prof = prof.chunk({"depth": chunks["depth"], "lat": chunks["lat"], "lon": chunks["lon"]})

        else:
            arr = np.asarray(profile)

            if arr.ndim == 1:
                prof = xr.DataArray(arr, dims=("depth",), coords={"depth": depth})
                prof = prof.chunk({"depth": chunks["depth"]})

            elif arr.ndim == 3:
                prof = xr.DataArray(arr, dims=("depth", "lat", "lon"), coords={"depth": depth, "lat": lat, "lon": lon})
                prof = prof.chunk({"depth": chunks["depth"], "lat": chunks["lat"], "lon": chunks["lon"]})

        return prof.astype("float64")

    depth = _coord_to_da(data["depth"], "depth")
    lat = _coord_to_da(data["lat"], "lat")
    lon = _coord_to_da(data["lon"], "lon")

    CT = _field_to_da(data["temp"], "temp", depth, lat, lon)
    SA = _field_to_da(data["sali"], "sali", depth, lat, lon)

    if chunks is None:
        tN = int(CT.sizes.get("time", 1))
        dN = int(CT.sizes.get("depth", 1))
        yN = int(CT.sizes.get("lat", 1))
        xN = int(CT.sizes.get("lon", 1))
        chunks = {"time": min(16, max(4, tN)), "depth": min(16, max(4, dN)), "lat": min(256, max(64, yN)), "lon": min(256, max(64, xN))}

    CT = CT.astype("float32").chunk(chunks)
    SA = SA.astype("float32").chunk(chunks)
    depth = depth.astype("float64").chunk({"depth": -1})
    lat = lat.astype("float64").chunk({"lat": -1})

    prof = _profile_to_da(profile, depth, lat, lon, chunks)

    m = str(mode).lower()
    if m == "temp":
        CT = xr.broadcast(prof, CT)[0].astype("float32").chunk(chunks)
        out_name = "tvol"
        out_long = "Specific volume with CT=profile, SA=original"
    elif m == "sali":
        SA = xr.broadcast(prof, SA)[0].astype("float32").chunk(chunks)
        out_name = "svol"
        out_long = "Specific volume with SA=profile, CT=original"

    z1d = xr.where(depth > 0, -depth, depth)
    z4d = xr.broadcast(z1d, CT)[0].chunk(chunks)
    lat4 = xr.broadcast(lat, CT)[0].chunk(chunks)

    guf = {"allow_rechunk": False}

    P = xr.apply_ufunc(gsw.p_from_z, z4d, lat4, input_core_dims=[[], []], output_core_dims=[[]], dask="parallelized", vectorize=False, output_dtypes=[np.float64], dask_gufunc_kwargs=guf)

    sv = xr.apply_ufunc(gsw.specvol, SA.astype("float64"), CT.astype("float64"), P, input_core_dims=[[], [], []], output_core_dims=[[]], dask="parallelized", vectorize=False, output_dtypes=[np.float64], dask_gufunc_kwargs=guf).astype("float32")

    sv = sv.transpose("time", "depth", "lat", "lon", missing_dims="ignore")
    sv.name = out_name
    sv.attrs.update({"units": "m^3 kg^-1", "standard_name": "specific_volume", "long_name": out_long})

    return (sv, P) if return_pressure else sv
def dz(depth):
    d0 = xr.DataArray([depth[0]], dims="border")
    mids = (depth[:-1] + depth[1:]) / 2
    mids = xr.DataArray(mids, dims="border")
    dN = xr.DataArray([depth[-1]], dims="border")
    zb = xr.concat([d0, mids, dN], dim="border")
    dz = zb[1:].values - zb[:-1].values

    return dz.astype("float64")
def pres2depth_w(pres, lat, lat_ref=None, dim='pres', clamp=25.0):
    pres = np.asarray(pres, dtype='float64')
    lat = np.asarray(lat, dtype='float64')
    if lat_ref is None:
        lat_ref = float(np.mean(lat))
    depth_tgt = -gsw.z_from_p(pres, lat_ref)
    depth_src = -gsw.z_from_p(pres[:, None], lat[None, :])
    W = np.zeros((lat.size, depth_tgt.size, pres.size), dtype='float32')
    k = np.arange(depth_tgt.size)
    for j in range(lat.size):
        zs = depth_src[:, j]
        f = np.interp(depth_tgt, zs, np.arange(pres.size, dtype='float64'))
        i0 = np.clip(np.floor(f).astype('int64'), 0, pres.size - 2)
        w1 = f - i0
        inside = (depth_tgt >= zs[0]) & (depth_tgt <= zs[-1])
        W[j, k[inside], i0[inside]] = (1.0 - w1[inside])
        W[j, k[inside], i0[inside] + 1] += w1[inside]
        lo = (~inside) & (depth_tgt < zs[0]) & (depth_tgt >= zs[0] - clamp)
        hi = (~inside) & (depth_tgt > zs[-1]) & (depth_tgt <= zs[-1] + clamp)
        W[j, k[lo], 0] = 1.0
        W[j, k[hi], -1] = 1.0
    W = xr.DataArray(W, dims=('lat', 'depth', dim), coords={'lat': lat, 'depth': depth_tgt})
    return W, depth_tgt
def p2z(da, W, dim='pres', out_dims=('time', 'depth', 'lat', 'lon')):
    def _dot(a, b):
        try: return xr.dot(a, b, dim=dim)
        except TypeError: return xr.dot(a, b, dims=dim)
    da = da.chunk({dim: -1})
    num = _dot(W, da.fillna(0.0))
    den = _dot(W, da.notnull().astype('float32'))
    out = (num / den.where(den > 0)).where(den >= 1.0 - 1e-4)
    return out.transpose(*out_dims)
def density_band_average(res, var_name, dens_levels, dens_dim='density'):
    x = res[var_name].sel({dens_dim: dens_levels}, method="nearest").drop_vars(dens_dim)
    p = res["pres"].sel({dens_dim: dens_levels}, method="nearest").drop_vars(dens_dim)
    lo, hi = {dens_dim: slice(0, -1)}, {dens_dim: slice(1, None)}
    dp = p.isel(hi) - p.isel(lo)
    x_mid = 0.5 * (x.isel(lo) + x.isel(hi))
    w = dp.where(np.isfinite(x_mid) & (dp > 0))
    return ((x_mid * w).sum(dens_dim) / w.sum(dens_dim)).where(w.notnull().all(dens_dim))
def polygon_mask(lon2d, lat2d, polygon_lonlat):
    points = np.column_stack([lon2d.ravel(), lat2d.ravel()])
    path = Path(polygon_lonlat)
    inside = path.contains_points(points)
    return inside.reshape(lon2d.shape)
def stip_sig(mm, pv, msk, lon, lat, sk=8):
    k = (pv[::sk, ::sk] < 0.05) & msk[::sk, ::sk]
    xx, yy = mm(lon[::sk, ::sk][k], lat[::sk, ::sk][k])
    mm.scatter(xx, yy, s=40, c='k', marker='.', linewidths=0, zorder=3)
def bser(obj, var, s0, f0, box, dmin=None, dmax=None, rs=True):
    ts = litrend(obj, var, s=s0, f=f0, rm_season=rs, dmin=dmin, dmax=dmax, timeseries=True, **box)
    tm = pd.PeriodIndex(pd.to_datetime(ts['time'].values), freq='M').to_timestamp()
    return pd.Series(np.asarray(ts.values, dtype=float), index=tm)
def tline(t, v, s0, f0):
    t = pd.DatetimeIndex(t)
    Y = xr.DataArray(np.asarray(v, dtype=float), dims=('time',), coords={'time': t}, name='y')
    sl, itc, _, _, _, _ = litrend(Y, 'y', s=s0, f=f0, rm_season=False, ar1=False, return_stats=True)
    yr = np.asarray(t - t[0]) / np.timedelta64(1, 'D') / 365.2425
    return float(itc) + (float(sl) / 10.0) * yr
def draw_series(ax, ser, c, lb, xt, s0, f0, lw=3):
    v = ser.reindex(xt).values
    ax.plot(xt, v, color=c, linewidth=lw, zorder=4, label=lb)
    ax.plot(xt, tline(xt, v, s0, f0), color=c, linewidth=lw, zorder=6, linestyle=(0, (3, 2)))
def fit_series(ser, s0, f0, mask=None):
    v = ser.copy()
    if mask is not None:
        m = mask.reindex(v.index).fillna(False).values.astype(bool)
        v[~m] = np.nan
    Y = xr.DataArray(v.values, dims=('time',), coords={'time': pd.DatetimeIndex(v.index)}, name='y')
    sl, _, _, _, se, _ = litrend(Y, 'y', s=s0, f=f0, rm_season=False, ar1=False, return_stats=True)
    return '%.2f ± %.2f' % (float(sl), 2.0 * float(se)), int(np.isfinite(v.values).sum())
def cell_trend(obj, var, dmin, dmax, s0, f0, box):
    sl, _, _, _, se, _ = litrend(obj, var, s=s0, f=f0, rm_season=True, dmin=dmin, dmax=dmax, ar1=False, return_stats=True, **box)
    ts = litrend(obj, var, s=s0, f=f0, rm_season=True, dmin=dmin, dmax=dmax, timeseries=True, **box)
    return '%.2f ± %.2f' % (float(sl), 2.0 * float(se)), int(np.asarray(ts.values).size)
def tr_trend(obj, var, ws, wf, d1, d2, box):
    sl, _, _, _, se, _ = litrend(obj, var, s=ws, f=wf, rm_season=True, dmin=d1, dmax=d2, ar1=False, return_stats=True, **box)
    return float(sl), 2.0 * float(se)
def grace_gap_runs(obs):
    runs, i = [], 0
    while i < len(obs):
        if not obs[i]:
            j = i
            while j < len(obs) and not obs[j]:
                j += 1
            runs.append((i, j - 1))
            i = j
        else:
            i += 1
    return sorted(runs, key=lambda r: r[1] - r[0], reverse=True)
def layer_dz(z_all, d1, d2):
    z_all = np.asarray(z_all, dtype='float64')
    order = np.argsort(z_all)
    z_srt = z_all[order]
    zb = np.concatenate([[z_srt[0]], 0.5 * (z_srt[:-1] + z_srt[1:]), [z_srt[-1]]])
    cell = zb[1:] - zb[:-1]
    ov = np.clip(np.minimum(zb[1:], float(d2)) - np.maximum(zb[:-1], float(d1)), 0.0, None)
    frac = np.divide(ov, cell, out=np.zeros_like(ov), where=cell > 0)
    return order[frac > 0], cell[frac > 0] * frac[frac > 0]
def box_layer_mean(ds, var, box, dmin, dmax):
    d = datacut(ds, var, **box)[var]
    keep, dzv = layer_dz(d['depth'].values, dmin, dmax)
    d = d.isel(depth=keep)
    w = xr.DataArray(dzv, dims=('depth',), coords={'depth': d['depth']}) * np.cos(np.deg2rad(d['lat']))
    return float(d.weighted(w).mean(dim=('depth', 'lat', 'lon'), skipna=True).values)
def box_layer_integral(ds, var, box, dmin, dmax):
    d = datacut(ds, var, **box)[var]
    keep, dzv = layer_dz(d['depth'].values, dmin, dmax)
    d = d.isel(depth=keep)
    dzw = xr.DataArray(dzv, dims=('depth',), coords={'depth': d['depth']})
    col = (d * dzw).sum(dim='depth')
    return float(col.weighted(np.cos(np.deg2rad(col['lat']))).mean(dim=('lat', 'lon')).values)
def ar1_ci(ser, s0, f0):
    Y = xr.DataArray(ser.values, dims=('time',), coords={'time': pd.DatetimeIndex(ser.index)}, name='y')
    sl, _, _, _, se, dof = litrend(Y, 'y', s=s0, f=f0, rm_season=False, ar1=True, return_stats=True)
    return float(sl), float(ci95(se, dof))
def mbb_ratios(b):
    fT = np.abs(b['T_heave']) / (np.abs(b['T_heave']) + np.abs(b['T_spice'])) * 100.0
    fS = np.abs(b['S_heave']) / (np.abs(b['S_heave']) + np.abs(b['S_spice'])) * 100.0
    return {'comp_HSL_over_TSL_%': -b['HSL'] / b['TSL'] * 100.0, 'T_heave_%': fT, 'T_spice_%': 100.0 - fT, 'S_heave_%': fS, 'S_spice_%': 100.0 - fS, 'spiceS_minus_spiceT_pp': (100.0 - fS) - (100.0 - fT)}
def ensemble_mean(objs, var, ws, wf, d1, d2, box):
    v = np.array([tr_trend(o, var, ws, wf, d1, d2, box)[0] for o in objs])
    return v.mean(), v.std(ddof=1)
def make_annular_sector_boundary(ax, proj, lonmin=40, lonmax=120, inner_lat=-70, outer_lat=0, n=721):
    pc = ccrs.PlateCarree()
    lo, la = np.linspace(lonmin, lonmax, n), np.linspace(inner_lat, outer_lat, n)
    lons = np.concatenate([np.full(n, lonmin), lo, np.full(n, lonmax), lo[::-1]])
    lats = np.concatenate([la, np.full(n, outer_lat), la[::-1], np.full(n, inner_lat)])
    xy = proj.transform_points(pc, lons, lats)[:, :2]
    xy = xy[np.isfinite(xy).all(axis=1)]
    codes = np.full(len(xy), mpath.Path.LINETO, dtype=np.uint8); codes[0] = mpath.Path.MOVETO; codes[-1] = mpath.Path.CLOSEPOLY
    ax.set_boundary(mpath.Path(xy, codes), transform=ax.transData)
def draw_box(ax, lonmin, lonmax, latmin, latmax, color="black", lw=3, zorder=8, n=400):
    pc = ccrs.PlateCarree()
    lo, la = np.linspace(lonmin, lonmax, n), np.linspace(latmin, latmax, n)
    lons = np.concatenate([lo, np.full(n, lonmax), lo[::-1], np.full(n, lonmin)])
    lats = np.concatenate([np.full(n, latmin), la, np.full(n, latmax), la[::-1]])
    ax.plot(lons, lats, color=color, linewidth=lw, transform=pc, zorder=zorder)
def add_custom_geo_labels(ax, lon_ticks, lat_ticks, lon_min, top_lat=2.8, side_offset=2.5, fs=30):
    pc = ccrs.PlateCarree()
    for lon in lon_ticks: ax.text(lon, top_lat, rf"{int(lon)}$^\circ$E", transform=pc, ha="center", va="bottom", fontsize=fs, clip_on=False, zorder=20)
    for lat in lat_ticks: ax.text(lon_min - side_offset, lat, "Equ" if np.isclose(lat, 0) else rf"{abs(int(lat))}$^\circ$S", transform=pc, ha="right", va="center", fontsize=fs, clip_on=False, zorder=20)
def rm_season(time1d, data, *, lon=None, lat=None, lonmin=None, lonmax=None, latmin=None, latmax=None, dtype=np.float32, n_jobs=os.cpu_count(), return_climatology=True, min_valid=1, s=None, f=None):
    def _to_array(x):
        return x() if callable(x) else (x.values if hasattr(x, "values") else x)
    def _to_dtindex(t):
        return pd.to_datetime(_to_array(t))
    def _infer_axis(shape_rest, ref_len, prefer_last=True, exclude=None):
        cand = [i+1 for i,s in enumerate(shape_rest) if s == ref_len and (exclude is None or (i+1) != exclude)]
        return (max(cand) if prefer_last else min(cand)) if cand else None
    def _make_lon_mask(lon_arr, lo, hi):
        if lo is None or hi is None:
            return None
        v = _to_array(lon_arr).ravel()
        return ((v >= lo) & (v <= hi)) if hi >= lo else ((v >= lo) | (v <= hi))
    def _make_lat_mask(lat_arr, lo, hi):
        if lo is None or hi is None:
            return None
        v = _to_array(lat_arr).ravel()
        return (v >= lo) & (v <= hi)

    t = _to_dtindex(time1d)
    a = np.asarray(_to_array(data), dtype=dtype)
    idx = (t.month.values if isinstance(t, pd.DatetimeIndex) else pd.DatetimeIndex(t).month.values) - 1
    T = a.shape[0]
    if s is not None or f is not None:
        s_ = pd.to_datetime(s) if s is not None else t.min()
        f_ = pd.to_datetime(f) if f is not None else t.max()
        clim_mask = (t >= s_) & (t <= f_)
    else:
        clim_mask = np.ones(T, dtype=bool)

    indexers = [slice(None)] * a.ndim
    lon_axis = lat_axis = None
    if lon is not None:
        lon_axis = _infer_axis(a.shape[1:], _to_array(lon).size, prefer_last=True)
    if lat is not None:
        lat_axis = _infer_axis(a.shape[1:], _to_array(lat).size, prefer_last=True, exclude=lon_axis)

    if lon is not None and lon_axis is not None:
        m_lon = _make_lon_mask(lon, lonmin, lonmax)
        if m_lon is not None and m_lon.any():
            indexers[lon_axis] = m_lon
    if lat is not None and lat_axis is not None:
        m_lat = _make_lat_mask(lat, latmin, latmax)
        if m_lat is not None and m_lat.any():
            indexers[lat_axis] = m_lat

    a = a[tuple(indexers)]
    rest_shape = a.shape[1:]
    clim = np.full((12,) + rest_shape, np.nan, dtype=dtype)

    def _clim_m(m):
        msel = (idx == m) & clim_mask
        if not np.any(msel):
            return np.full(rest_shape, np.nan, dtype=dtype)
        sel = a[msel]
        cnt = np.sum(~np.isnan(sel), axis=0, dtype=np.int64)
        ssum = np.nansum(sel, axis=0)
        outm = np.full(rest_shape, np.nan, dtype=dtype)
        ok = cnt >= min_valid
        np.divide(ssum, cnt, out=outm, where=ok)
        return outm

    parts = Parallel(n_jobs=n_jobs, prefer="processes")(delayed(_clim_m)(m) for m in range(12))
    for m in range(12):
        clim[m] = parts[m]

    out = np.empty_like(a)
    for m in range(12):
        tsel = np.where(idx == m)[0]
        if tsel.size:
            out[tsel] = a[tsel] - clim[m]

    if return_climatology:
        return out, clim
    return out
def litrend(data, var_name, *, s=None, f=None, dmin=None, dmax=None, lonmin=None, lonmax=None, latmin=None, latmax=None, time_name=None, depth_name=None, lat_name="lat", lon_name="lon", dz_title=None, rm_season=False, timeseries=False, ar1=False, annual=False, annual_min=6, to_per_decade=True, scale=1.0, return_stats=False):
    R_EARTH = 6371000.0
    def _unwrap(v):
        return v() if hasattr(v, "_ds") and callable(v) else (v() if hasattr(v, "_ds") else v)
    def _get_var(obj, name):
        if isinstance(obj, xr.DataArray):
            if obj.name == name or name is None:
                return obj
        if isinstance(obj, xr.Dataset):
            if name in obj.data_vars or name in obj.variables:
                return obj[name]
            low = {k.lower(): k for k in obj.variables}
            if name.lower() in low:
                return obj[low[name.lower()]]
        try:
            v = obj[name]
        except Exception:
            keys = list(getattr(obj, "keys", lambda: [])())
            low = {str(k).lower(): k for k in keys}
            if name.lower() in low:
                v = obj[low[name.lower()]]
        v = _unwrap(v)
        if isinstance(v, xr.DataArray):
            return v
        def _get_first(o, cand):
            for k in cand:
                try:
                    w = _unwrap(o[k]); return w, k
                except Exception:
                    pass
            return None, None
        t_val, t_name = _get_first(obj, ["time","time_counter","t","Time","TIME","dates","date","month"])
        y_val, y_name = _get_first(obj, ["lat","latitude","yt_ocean","nav_lat","y","LAT"])
        x_val, x_name = _get_first(obj, ["lon","longitude","xt_ocean","nav_lon","x","LON"])
        arr = np.asarray(v)
        if arr.ndim == 3 and t_val is not None and y_val is not None and x_val is not None:
            if arr.shape == (np.size(t_val), np.size(y_val), np.size(x_val)):
                return xr.DataArray(arr, dims=(t_name, y_name, x_name), coords={t_name: np.asarray(t_val), y_name: np.asarray(y_val), x_name: np.asarray(x_val)})
        if arr.ndim == 2 and y_val is not None and x_val is not None:
            if arr.shape == (np.size(y_val), np.size(x_val)):
                return xr.DataArray(arr, dims=(y_name, x_name), coords={y_name: np.asarray(y_val), x_name: np.asarray(x_val)})
        if arr.ndim == 1 and t_val is not None and arr.shape[0] == np.size(t_val):
            return xr.DataArray(arr, dims=(t_name,), coords={t_name: np.asarray(t_val)})
        return xr.DataArray(arr)
    def _find_dim(A, cands):
        for c in cands:
            if c in A.dims:
                return c
        return None
    def _to_years(t):
        if np.issubdtype(t.dtype, np.datetime64):
            return (t - t[0]) / np.timedelta64(1, "D") / 365.2425
        return xr.DataArray(np.arange(t.size), dims=t.dims) / 12.0
    def _dz(depth_1d):
        d0 = xr.DataArray([depth_1d[0]], dims="border")
        mid = (depth_1d[:-1] + depth_1d[1:]) / 2
        mid = xr.DataArray(mid, dims="border")
        dN = xr.DataArray([depth_1d[-1]], dims="border")
        zb = xr.concat([d0, mid, dN], dim="border")
        out = (zb[1:].values - zb[:-1].values).astype("float64")
        return out
    def _lon_slice(A, lon_name, lon_min, lon_max):
        lon = A[lon_name]
        lo_min = float(lon.min())
        lo_max = float(lon.max())
        if lon_min <= lon_max:
            return A.sel({lon_name: slice(lon_min, lon_max)})
        A1 = A.sel({lon_name: slice(lon_min, lo_max)})
        A2 = A.sel({lon_name: slice(lo_min, lon_max)})
        out = xr.concat([A1, A2], dim=lon_name)
        return out
    def _cell_areas(lat_1d, lon_1d, latn, lonn):
        lat = np.asarray(lat_1d, dtype=float)
        lon = np.asarray(lon_1d, dtype=float)
        def edges(v):
            mid = (v[:-1] + v[1:]) / 2.0
            e = np.concatenate([[v[0] - (mid[0]-v[0])], mid, [v[-1] + (v[-1]-mid[-1])]])
            return e
        lat_e = np.deg2rad(edges(lat))
        lon_e = np.deg2rad(edges(lon))
        dlon = np.diff(lon_e)[None, :]
        sin_lat = np.sin(lat_e)
        dphi = (sin_lat[1:] - sin_lat[:-1])[:, None]
        area = (R_EARTH**2) * dlon * dphi
        out = xr.DataArray(area, dims=(latn, lonn), coords={latn: lat_1d, lonn: lon_1d})
        return out
    def _avg_both(A, latn, lonn):
        area = _cell_areas(A[latn], A[lonn], latn, lonn)
        w = area / area.sum()
        out = (A * w).sum(dim=(latn, lonn))
        return out
    def _avg_lat_only(A, latn, lonn):
        area = _cell_areas(A[latn], A[lonn], latn, lonn)
        w = area / area.sum(dim=latn)
        out = (A * w).sum(dim=latn)
        return out
    def _avg_lon_only(A, latn, lonn):
        area = _cell_areas(A[latn], A[lonn], latn, lonn)
        w = area / area.sum(dim=lonn)
        out = (A * w).sum(dim=lonn)
        return out
    def _regress_apply(Y, tname):
        t_years = _to_years(Y[tname])
        def _reg(y, t=t_years.values):
            m = np.isfinite(y) & np.isfinite(t)
            if m.sum() < 2:
                return (np.nan, np.nan, np.nan, np.nan, np.nan, np.nan)
            sl, itc, r, p, se = linregress(t[m], y[m])
            dof = float(m.sum() - 2)
            if ar1:
                res = y[m] - (sl * t[m] + itc)
                n = res.size
                if n > 4 and np.std(res) > 0:
                    r1 = float(np.corrcoef(res[:-1], res[1:])[0, 1])
                    r1 = 0.0 if not np.isfinite(r1) else min(max(r1, 0.0), 0.99)
                    neff = n * (1.0 - r1) / (1.0 + r1)
                    if neff > 4:
                        se = se * np.sqrt((n - 2.0) / (neff - 2.0))
                        dof = neff - 2.0
                        p = 2.0 * student_t.sf(abs(sl / se), dof) if se > 0 else np.nan
            return (sl, itc, r, p, se, dof)
        out = xr.apply_ufunc(_reg, Y, input_core_dims=[[tname]], output_core_dims=[[], [], [], [], [], []], vectorize=True, dask="parallelized", dask_gufunc_kwargs={"allow_rechunk": True}, output_dtypes=[float, float, float, float, float, float])
        return out

    A = _get_var(data, var_name)

    if time_name is None:
        time_name = _find_dim(A, ("time","time_counter","t","date","dates","month","Time","TIME"))
        if time_name is None:
            for d in A.dims:
                try:
                    if np.issubdtype(A[d].dtype, np.datetime64):
                        time_name = d
                        break
                except Exception:
                    pass
    if depth_name is None:
        depth_name = _find_dim(A, ("depth","deptht","lev","z"))

    if s is not None or f is not None:
        A = A.sel({time_name: slice(s, f)})

    has_depth = (depth_name in A.dims) if depth_name else False

    if latmin is not None or latmax is not None:
        if latmin is None: latmin = float(A[lat_name].min())
        if latmax is None: latmax = float(A[lat_name].max())
        A = A.sel({lat_name: slice(latmin, latmax)})

    if lonmin is not None or lonmax is not None:
        if lonmin is None: lonmin = float(A[lon_name].min())
        if lonmax is None: lonmax = float(A[lon_name].max())
        A = _lon_slice(A, lon_name, lonmin, lonmax)

    use_depth_range = has_depth and (dmin is not None or dmax is not None)
    if use_depth_range:
        z_all = np.asarray(A[depth_name].values, dtype='float64')
        order = np.argsort(z_all)
        z_srt = z_all[order]
        zb = np.concatenate([[z_srt[0]], 0.5 * (z_srt[:-1] + z_srt[1:]), [z_srt[-1]]])
        cell = zb[1:] - zb[:-1]
        d1 = -np.inf if dmin is None else float(dmin)
        d2 = np.inf if dmax is None else float(dmax)
        ov = np.clip(np.minimum(zb[1:], d2) - np.maximum(zb[:-1], d1), 0.0, None)
        frac = np.divide(ov, cell, out=np.zeros_like(ov), where=cell > 0)
        keep = order[frac > 0]
        if dz_title is not None:
            if isinstance(data, xr.Dataset):
                Z = data[dz_title]
            elif isinstance(data, xr.DataArray):
                Z = data.coords.get(dz_title, None)
            else:
                Z = _unwrap(data[dz_title])
            base = np.asarray(Z.values, dtype='float64')[keep]
        else:
            base = cell[frac > 0]
        A = A.isel({depth_name: keep})
        dzv = xr.DataArray(base * frac[frac > 0], dims=(depth_name,), coords={depth_name: A[depth_name]})
        A_depthop = (A * dzv).sum(dim=depth_name)
    else:
        A_depthop = A

    want_avg_lat = (latmin is not None or latmax is not None) and (lat_name in A_depthop.dims)
    want_avg_lon = (lonmin is not None or lonmax is not None) and (lon_name in A_depthop.dims)

    if want_avg_lat and want_avg_lon:
        A_pre = _avg_both(A_depthop, lat_name, lon_name)
    elif want_avg_lat and not want_avg_lon:
        A_pre = _avg_lat_only(A_depthop, lat_name, lon_name)
    elif want_avg_lon and not want_avg_lat:
        A_pre = _avg_lon_only(A_depthop, lat_name, lon_name)
    else:
        A_pre = A_depthop

    if rm_season:
        func_rm = globals().get("rm_season", None)
        lon_ref = A_pre.coords.get(lon_name) if lon_name in A_pre.dims else None
        lat_ref = A_pre.coords.get(lat_name) if lat_name in A_pre.dims else None
        A_pre_arr = func_rm(A_pre[time_name], A_pre.data, lon=lon_ref, lat=lat_ref, return_climatology=False)
        A_ready = xr.DataArray(A_pre_arr, dims=A_pre.dims, coords=A_pre.coords, attrs=A_pre.attrs)
    else:
        A_ready = A_pre

    if timeseries:
        out_ts = A_ready
        return out_ts

    if annual:
        grp = A_ready.groupby(f"{time_name}.year")
        cnt = grp.count(time_name)
        A_ready = grp.mean(time_name, skipna=True).where(cnt >= annual_min)
        yv = np.asarray(A_ready['year'].values, dtype=int)
        A_ready = A_ready.rename({'year': time_name}).assign_coords({time_name: pd.to_datetime([f'{y}-07-01' for y in yv])})

    A_ready = A_ready.chunk({time_name: -1})
    slope, intercept, r, p, stderr, dof = _regress_apply(A_ready, time_name)

    factor = scale * (10.0 if to_per_decade else 1.0)
    slope = slope * factor
    stderr = stderr * factor
    slope.name = f"{var_name}_trend"
    slope.attrs["units"] = "per_decade" if to_per_decade else "per_year"
    slope = slope.where(slope != 0)

    if return_stats:
        return slope, intercept, r, p, stderr, dof
    return slope
def ci95(se, dof, level=0.95):
    return student_t.ppf(0.5 + level / 2.0, dof) * se
def steric_h(DATA, sv='vol', mt='mean_t', ms='mean_s', dz='d_ran'):
    depth = DATA['depth']().astype('float64').chunk({'depth': -1})
    lat = DATA['lat']().astype('float64')

    p = xr.apply_ufunc(gsw.p_from_z, -depth, lat, input_core_dims=[['depth'], []], output_core_dims=[['depth']], dask='parallelized', vectorize=True, output_dtypes=[np.float64])

    sref = DATA[ms]().astype('float64').chunk({'depth': -1})
    tref = DATA[mt]().astype('float64').chunk({'depth': -1})
    p = p.chunk({'depth': -1})

    alpha_ref = xr.apply_ufunc(gsw.specvol, sref, tref, p, input_core_dims=[['depth'], ['depth'], ['depth']], output_core_dims=[['depth']], dask='parallelized', vectorize=True, output_dtypes=[np.float64])

    I = -(DATA[sv]().astype('float64') / xr.broadcast(alpha_ref, DATA[sv]())[0] - 1.0) * -100

    I.name = 'steric_integrand'
    I.attrs.update(units='cm', long_name='Steric height anomaly integrand')

    return I
def datacut(ds, var=None, *args, s=None, f=None, lonmin=None, lonmax=None, latmin=None, latmax=None, dmin=None, dmax=None, lon=None, lat=None, depth=None, time=None, tag=None, dim='series', return_series=True):

    var_in = var

    def _unwrap_var(v):
        return v() if hasattr(v, "_ds") and callable(v) else v

    def _find(obj, keys):
        for c in getattr(obj, "coords", {}):
            cl = c.lower()
            if any(cl.startswith(k) or k in cl for k in keys):
                return c
        for c in getattr(obj, "variables", {}):
            cl = c.lower()
            if any(cl.startswith(k) or k in cl for k in keys):
                return c
        return None

    def _is0360(da, ln):
        v = np.asarray(da[ln].values, float)
        return np.nanmin(v) >= 0 and np.nanmax(v) <= 360

    def _to_dt(x):
        if x is None:
            return None
        if isinstance(x, (np.datetime64, datetime)):
            return np.datetime64(x)
        try:
            return np.datetime64(x)
        except:
            return np.datetime64('NaT')

    if len(args) == 1 and isinstance(args[0], str):
        tag = args[0]
        args = tuple()
    elif len(args) == 4:
        lon = (float(args[0]), float(args[1]))
        lat = (float(args[2]), float(args[3]))
    elif len(args) == 2:
        a, b = args
        ta, tb = _to_dt(a), _to_dt(b)
        time = (ta, tb) if str(ta) != 'NaT' and str(tb) != 'NaT' else None
        if time is None:
            depth = (float(a), float(b))

    if isinstance(var_in, (list, tuple, set)):
        vars_list = list(var_in)
    else:
        vars_list = [var_in] if var_in is not None else None

    if vars_list is None and isinstance(ds, pd.Series):
        kk = next((k for k, v in ds.items() if isinstance(v, xr.DataArray)), None)
        vars_list = [kk]

    if isinstance(ds, xr.Dataset):
        base = ds if vars_list is None else ds
    elif isinstance(ds, xr.DataArray):
        base = ds
    elif isinstance(ds, pd.Series):
        base = _unwrap_var(ds[vars_list[0]])

    lon_name = _find(base, ["lon", "longitude", "nav_lon", "x"])
    lat_name = _find(base, ["lat", "latitude", "nav_lat", "y"])
    time_name = _find(base, ["time", "time_counter", "t"])
    depth_name = _find(base, ["depth", "deptht", "lev", "level", "z", "deptho"])

    if time is None and (s is not None or f is not None):
        time = (s, f)

    if lon is None and (lonmin is not None and lonmax is not None):
        lon = (float(lonmin), float(lonmax))
    if lat is None and (latmin is not None and latmax is not None):
        lat = (float(latmin), float(latmax))
    if depth is None and (dmin is not None or dmax is not None):
        d1 = -np.inf if dmin is None else float(dmin)
        d2 = np.inf if dmax is None else float(dmax)
        depth = (d1, d2)

    out = base

    if time is not None and time_name is not None:
        t1, t2 = _to_dt(time[0]), _to_dt(time[1])
        out = out.sel({time_name: slice(t1, t2)})

    if lon is not None and lon_name is not None:
        x1, x2 = map(float, lon)
        if _is0360(out, lon_name):
            out = out.assign_coords({lon_name: np.mod(out[lon_name], 360.0)})
            L1, L2 = np.mod(x1, 360.0), np.mod(x2, 360.0)
            if L1 <= L2:
                out = out.sel({lon_name: slice(L1, L2)})
            else:
                left = out.sel({lon_name: slice(L1, 360.0)})
                right = out.sel({lon_name: slice(0.0, L2)})
                out = xr.concat([left, right], dim=lon_name)
        else:
            to180 = lambda v: ((v + 180.0) % 360.0) - 180.0
            out = out.assign_coords({lon_name: to180(out[lon_name])})
            L1, L2 = to180(x1), to180(x2)
            if L1 <= L2:
                out = out.sel({lon_name: slice(L1, L2)})
            else:
                left = out.sel({lon_name: slice(L1, 180.0)})
                right = out.sel({lon_name: slice(-180.0, L2)})
                out = xr.concat([left, right], dim=lon_name)

    if lat is not None and lat_name is not None:
        y1, y2 = map(float, lat)
        yv = np.asarray(out[lat_name].values, float)
        asc = np.nanmean(np.diff(yv)) > 0
        out = out.sel({lat_name: slice(y1, y2) if asc else slice(y2, y1)})

    if depth is not None and depth_name is not None:
        d1, d2 = map(float, depth)
        dv = np.asarray(out[depth_name].values, float)
        asc = np.nanmean(np.diff(dv)) > 0
        out = out.sel({depth_name: slice(d1, d2) if asc else slice(d2, d1)})

    if not return_series:
        return out if isinstance(out, xr.Dataset) else out

    payload = {}

    if isinstance(ds, xr.Dataset):
        targets = list(ds.data_vars) if vars_list is None else vars_list
        for k in targets:
            if k in out:
                payload[k] = out[k]
    elif isinstance(ds, pd.Series):
        targets = vars_list
        for k in targets:
            payload[k] = out if k == targets[0] and isinstance(out, xr.DataArray) else _unwrap_var(ds[k])
    else:
        payload[vars_list[0] if vars_list else 'data'] = out

    payload.update({"lon": out.coords[lon_name].values if (lon_name and (lon_name in getattr(out, "coords", {}))) else None, "lat": out.coords[lat_name].values if (lat_name and (lat_name in getattr(out, "coords", {}))) else None, "time": out.coords[time_name].values if (time_name and (time_name in getattr(out, "coords", {}))) else None, "depth": out.coords[depth_name].values if (depth_name and (depth_name in getattr(out, "coords", {}))) else None})

    s_out = pd.Series(payload, name=tag if tag is not None else (vars_list[0] if vars_list else None))
    return s_out
def heave_trend(series, s=None, f=None, rm_season=True, return_dzdt=False, depth='m', sigma0=None, z_sigma=None, return_series=False):
    SEC_PER_DECADE = 10.0 * 365.2425 * 24.0 * 3600.0
    G_STD = 9.80665

    def _unwrap(v):
        try:
            return v() if callable(v) else v
        except Exception:
            return v

    def _as_da(v, name):
        v = _unwrap(v)
        if isinstance(v, xr.DataArray):
            return v
        coords = {"time": _unwrap(series.get("time")), "depth": _unwrap(series.get("depth")), "lat": _unwrap(series.get("lat")), "lon": _unwrap(series.get("lon"))}
        return xr.DataArray(v, dims=("time","depth","lat","lon"), coords=coords, name=name).chunk("auto")

    def _coord_at_sigma_profile(sig, coord1d, sig_targets):
        sig = np.asarray(sig, float)
        coord1d = np.asarray(coord1d, float)
        sig_targets = np.asarray(sig_targets, float)
        if sig.ndim == 1:
            m = np.isfinite(sig) & np.isfinite(coord1d)
            n = int(m.sum())
            if n == 0:
                return np.full_like(sig_targets, np.nan, dtype=float)
            if n == 1:
                return np.full_like(sig_targets, float(coord1d[m][0]), dtype=float)
            s = sig[m]; cc = coord1d[m]
            o = np.argsort(s); s = s[o]; cc = cc[o]
            s_u, idx = np.unique(s, return_index=True)
            c_u = cc[idx]
            return np.interp(sig_targets, s_u, c_u, left=c_u[0], right=c_u[-1])
        lead = int(np.prod(sig.shape[:-1])); D = sig.shape[-1]
        out = np.empty_like(sig_targets, dtype=float)
        sig_f = sig.reshape(lead, D)
        tgt_f = sig_targets.reshape(lead, D)
        if coord1d.ndim == 1:
            cc_base = coord1d
            out_f = out.reshape(lead, D)
            for i in range(lead):
                s1 = sig_f[i]
                m = np.isfinite(s1) & np.isfinite(cc_base)
                n = int(m.sum())
                if n == 0:
                    out_f[i].fill(np.nan); continue
                if n == 1:
                    out_f[i].fill(float(cc_base[m][0])); continue
                s = s1[m]; cc = cc_base[m]
                o = np.argsort(s); s = s[o]; cc = cc[o]
                s_u, idx = np.unique(s, return_index=True)
                c_u = cc[idx]
                out_f[i] = np.interp(tgt_f[i], s_u, c_u, left=c_u[0], right=c_u[-1])
        else:
            coord1d_f = coord1d.reshape(lead, D)
            out_f = out.reshape(lead, D)
            for i in range(lead):
                s1 = sig_f[i]; cc1 = coord1d_f[i]
                m = np.isfinite(s1) & np.isfinite(cc1)
                n = int(m.sum())
                if n == 0:
                    out_f[i].fill(np.nan); continue
                if n == 1:
                    out_f[i].fill(float(cc1[m][0])); continue
                s = s1[m]; cc = cc1[m]
                o = np.argsort(s); s = s[o]; cc = cc[o]
                s_u, idx = np.unique(s, return_index=True)
                c_u = cc[idx]
                out_f[i] = np.interp(tgt_f[i], s_u, c_u, left=c_u[0], right=c_u[-1])
        return out

    CT = _as_da(series["temp"], "CT").sortby("time").sortby("depth")
    SA = _as_da(series["sali"], "SA").sortby("time").sortby("depth")
    if s is not None or f is not None:
        CT = CT.sel(time=slice(s, f)); SA = SA.sel(time=slice(s, f))

    CH = {"time": min(24, CT.sizes.get("time", 24)), "depth": -1, "lat": min(128, CT.sizes.get("lat", 128)), "lon": min(128, CT.sizes.get("lon", 128))}
    CT = CT.chunk(CH); SA = SA.chunk(CH)

    axis1d = CT["depth"].astype(float)
    D = int(axis1d.sizes.get("depth", axis1d.size))

    if sigma0 is None:
        sigma0 = xr.apply_ufunc(gsw.sigma0, SA, CT, dask="parallelized", output_dtypes=[float]).chunk(CH)
    sigma_star = sigma0.mean("time").chunk({"depth": -1})
    sigma_star = xr.broadcast(sigma0, sigma_star)[1].chunk(CH)

    if z_sigma is None:
        z_sigma = xr.apply_ufunc(_coord_at_sigma_profile, sigma0, axis1d, sigma_star, input_core_dims=[["depth"],["depth"],["depth"]], output_core_dims=[["depth"]], dask="parallelized", dask_gufunc_kwargs={"output_sizes": {"depth": D}, "allow_rechunk": False}, output_dtypes=[float]).chunk(CH).rename("z_sigma")

    t = z_sigma["time"]
    tsec = xr.DataArray((t - t.mean()) / np.timedelta64(1,"s"), dims="time", coords={"time": t})
    if rm_season:
        mon_z = xr.DataArray(np.arange(1,13, dtype=int), dims="month", coords={"month": np.arange(1,13, dtype=int)})
        z_used = z_sigma.groupby("time.month") - z_sigma.groupby("time.month").mean("time").reindex(month=mon_z).ffill("month").bfill("month")
    else:
        z_used = z_sigma
    y_dm = z_used - z_used.mean("time")
    den = (tsec**2).sum("time", skipna=True)
    slope_per_sec = xr.where(den > 0, (y_dm * tsec).sum("time", skipna=True) / den, np.nan)

    if depth == 'm':
        dz_dt = (slope_per_sec * SEC_PER_DECADE).rename("dz_dt"); dz_dt.attrs["units"] = "m/decade"
    else:
        dp_dt = (slope_per_sec * SEC_PER_DECADE).rename("dp_dt"); dp_dt.attrs["units"] = "dbar/decade"

    if rm_season:
        months = xr.DataArray(np.arange(1,13, dtype=int), dims="month", coords={"month": np.arange(1,13, dtype=int)})
        CTm = CT.groupby("time.month").mean("time").reindex(month=months).ffill("month").bfill("month")
        SAm = SA.groupby("time.month").mean("time").reindex(month=months).ffill("month").bfill("month")
        dCT = CTm.differentiate("depth").mean("month")
        dSA = SAm.differentiate("depth").mean("month")
    else:
        dCT = CT.mean("time").differentiate("depth")
        dSA = SA.mean("time").differentiate("depth")

    if depth == 'm':
        dCT = dCT.rename("dCT_dz"); dSA = dSA.rename("dSA_dz")
        dCT.attrs["units"] = "degC/m"; dSA.attrs["units"] = "g kg-1/m"
        heave_CT = -(dCT * dz_dt).rename("heave_CT_trend")
        heave_SA = -(dSA * dz_dt).rename("heave_SA_trend")
    else:
        dCT = dCT.rename("dCT_dp"); dSA = dSA.rename("dSA_dp")
        dCT.attrs["units"] = "degC/dbar"; dSA.attrs["units"] = "g kg-1/dbar"
        heave_CT = -(dCT * dp_dt).rename("heave_CT_trend")
        heave_SA = -(dSA * dp_dt).rename("heave_SA_trend")

    if return_series:
        return (-(dCT * y_dm)).rename("heave_CT_series").transpose("time","depth","lat","lon"), (-(dSA * y_dm)).rename("heave_SA_series").transpose("time","depth","lat","lon")

    heave_CT = heave_CT.transpose("depth","lat","lon")
    heave_SA = heave_SA.transpose("depth","lat","lon")
    heave_CT.attrs["units"] = "degC/decade"
    heave_SA.attrs["units"] = "g kg-1/decade"

    if return_dzdt:
        if depth == 'm':
            return heave_CT, heave_SA, dz_dt.transpose("depth","lat","lon")
        else:
            SA_bar = SA.mean("time"); CT_bar = CT.mean("time")
            p1d = axis1d if axis1d.ndim == 1 else axis1d.isel(time=0, lat=0, lon=0)
            p3d = xr.broadcast(SA_bar, p1d)[1]
            rho = xr.apply_ufunc(gsw.rho, SA_bar, CT_bar, p3d, dask="parallelized", output_dtypes=[float])
            dz_dt = ((dp_dt * 1e4) / (rho * G_STD)).rename("dz_dt").transpose("depth","lat","lon")
            dz_dt.attrs["units"] = "m/decade"
            return heave_CT, heave_SA, dz_dt
    return heave_CT, heave_SA
def spice_trend(series, s=None, f=None, rm_season=True, return_zsigma=False, depth='m', return_series=False, sigma0=None, z_sigma=None):
    SEC_PER_DECADE = 10.0 * 365.2425 * 24.0 * 3600.0

    def _unwrap(v):
        try:
            return v() if callable(v) else v
        except Exception:
            return v

    def _as_da(v, name):
        v = _unwrap(v)
        if isinstance(v, xr.DataArray):
            return v
        coords = {"time": _unwrap(series.get("time")), "depth": _unwrap(series.get("depth")), "lat": _unwrap(series.get("lat")), "lon": _unwrap(series.get("lon"))}
        return xr.DataArray(v, dims=("time","depth","lat","lon"), coords=coords, name=name).chunk("auto")

    def _coord_at_sigma_profile(sig, coord1d, sig_targets):
        sig = np.asarray(sig, float)
        coord1d = np.asarray(coord1d, float)
        sig_targets = np.asarray(sig_targets, float)
        if sig.ndim == 1:
            m = np.isfinite(sig) & np.isfinite(coord1d)
            n = int(m.sum())
            if n == 0:
                return np.full_like(sig_targets, np.nan, dtype=float)
            if n == 1:
                return np.full_like(sig_targets, float(coord1d[m][0]), dtype=float)
            s = sig[m]; cc = coord1d[m]
            o = np.argsort(s); s = s[o]; cc = cc[o]
            s_u, idx = np.unique(s, return_index=True)
            c_u = cc[idx]
            return np.interp(sig_targets, s_u, c_u, left=c_u[0], right=c_u[-1])
        lead = int(np.prod(sig.shape[:-1])); D = sig.shape[-1]
        out = np.empty_like(sig_targets, dtype=float)
        sig_f = sig.reshape(lead, D)
        tgt_f = sig_targets.reshape(lead, D)
        if coord1d.ndim == 1:
            cc_base = coord1d
            out_f = out.reshape(lead, D)
            for i in range(lead):
                s1 = sig_f[i]
                m = np.isfinite(s1) & np.isfinite(cc_base)
                n = int(m.sum())
                if n == 0:
                    out_f[i].fill(np.nan); continue
                if n == 1:
                    out_f[i].fill(float(cc_base[m][0])); continue
                s = s1[m]; cc = cc_base[m]
                o = np.argsort(s); s = s[o]; cc = cc[o]
                s_u, idx = np.unique(s, return_index=True)
                c_u = cc[idx]
                out_f[i] = np.interp(tgt_f[i], s_u, c_u, left=c_u[0], right=c_u[-1])
        else:
            coord1d_f = coord1d.reshape(lead, D)
            out_f = out.reshape(lead, D)
            for i in range(lead):
                s1 = sig_f[i]; cc1 = coord1d_f[i]
                m = np.isfinite(s1) & np.isfinite(cc1)
                n = int(m.sum())
                if n == 0:
                    out_f[i].fill(np.nan); continue
                if n == 1:
                    out_f[i].fill(float(cc1[m][0])); continue
                s = s1[m]; cc = cc1[m]
                o = np.argsort(s); s = s[o]; cc = cc[o]
                s_u, idx = np.unique(s, return_index=True)
                c_u = cc[idx]
                out_f[i] = np.interp(tgt_f[i], s_u, c_u, left=c_u[0], right=c_u[-1])
        return out

    def _interp_profile(xprof, coord1d, coord_tgt):
        xprof = np.asarray(xprof, float)
        coord1d = np.asarray(coord1d, float)
        coord_tgt = np.asarray(coord_tgt, float)
        if xprof.ndim == 1:
            m = np.isfinite(xprof) & np.isfinite(coord1d)
            if m.sum() < 2:
                return np.full_like(coord_tgt, np.nan, dtype=float)
            return np.interp(coord_tgt, coord1d[m], xprof[m], left=xprof[m][0], right=xprof[m][-1])
        lead = int(np.prod(xprof.shape[:-1])); D = xprof.shape[-1]
        out = np.empty_like(coord_tgt, dtype=float)
        xp_f = xprof.reshape(lead, D)
        tgt_f = coord_tgt.reshape(lead, D)
        out_f = out.reshape(lead, D)
        for i in range(lead):
            xp = xp_f[i]
            m = np.isfinite(xp) & np.isfinite(coord1d)
            if m.sum() < 2:
                out_f[i].fill(np.nan); continue
            out_f[i] = np.interp(tgt_f[i], coord1d[m], xp[m], left=xp[m][0], right=xp[m][-1])
        return out

    CT = _as_da(series["temp"], "CT").sortby("time").sortby("depth")
    SA = _as_da(series["sali"], "SA").sortby("time").sortby("depth")
    if s is not None or f is not None:
        CT = CT.sel(time=slice(s, f)); SA = SA.sel(time=slice(s, f))

    CH = {"time": min(24, CT.sizes.get("time", 24)), "depth": -1, "lat": min(128, CT.sizes.get("lat", 128)), "lon": min(128, CT.sizes.get("lon", 128))}
    CT = CT.chunk(CH); SA = SA.chunk(CH)

    axis1d = CT["depth"].astype(float)
    D = int(axis1d.sizes.get("depth", axis1d.size))

    if sigma0 is None:
        sigma0 = xr.apply_ufunc(gsw.sigma0, SA, CT, dask="parallelized", output_dtypes=[float]).chunk(CH)
    sigma_star = sigma0.mean("time").chunk({"depth": -1})
    sigma_star = xr.broadcast(sigma0, sigma_star)[1].chunk(CH)

    if z_sigma is None:
        z_sigma = xr.apply_ufunc(_coord_at_sigma_profile, sigma0, axis1d, sigma_star, input_core_dims=[["depth"],["depth"],["depth"]], output_core_dims=[["depth"]], dask="parallelized", dask_gufunc_kwargs={"output_sizes": {"depth": D}, "allow_rechunk": False}, output_dtypes=[float]).chunk(CH).rename("z_sigma")

    CT_on_sigma = xr.apply_ufunc(_interp_profile, CT, axis1d, z_sigma, input_core_dims=[["depth"],["depth"],["depth"]], output_core_dims=[["depth"]], dask="parallelized", dask_gufunc_kwargs={"output_sizes": {"depth": D}, "allow_rechunk": False}, output_dtypes=[float]).rename("CT_sigma")

    SA_on_sigma = xr.apply_ufunc(_interp_profile, SA, axis1d, z_sigma, input_core_dims=[["depth"],["depth"],["depth"]], output_core_dims=[["depth"]], dask="parallelized", dask_gufunc_kwargs={"output_sizes": {"depth": D}, "allow_rechunk": False}, output_dtypes=[float]).rename("SA_sigma")

    t = CT_on_sigma["time"]
    tsec = xr.DataArray((t - t.mean()) / np.timedelta64(1,"s"), dims="time", coords={"time": t})

    mon = xr.DataArray(np.arange(1,13, dtype=int), dims="month", coords={"month": np.arange(1,13, dtype=int)})
    if rm_season:
        CTc = CT_on_sigma.groupby("time.month") - CT_on_sigma.groupby("time.month").mean("time").reindex(month=mon).ffill("month").bfill("month")
        SAc = SA_on_sigma.groupby("time.month") - SA_on_sigma.groupby("time.month").mean("time").reindex(month=mon).ffill("month").bfill("month")
    else:
        CTc = CT_on_sigma; SAc = SA_on_sigma

    def _ols_per_decade(y):
        ydm = y - y.mean("time")
        den = (tsec**2).sum("time", skipna=True)
        return xr.where(den > 0, (ydm * tsec).sum("time", skipna=True) / den, np.nan) * SEC_PER_DECADE

    if return_series:
        return CTc.rename("spice_CT_series").transpose("time","depth","lat","lon"), SAc.rename("spice_SA_series").transpose("time","depth","lat","lon")

    spice_CT = _ols_per_decade(CTc).rename("spice_CT_trend").transpose("depth","lat","lon")
    spice_SA = _ols_per_decade(SAc).rename("spice_SA_trend").transpose("depth","lat","lon")
    spice_CT.attrs["units"] = "degC/decade"
    spice_SA.attrs["units"] = "g kg-1/decade"

    if return_zsigma:
        return spice_CT, spice_SA, z_sigma.transpose("time","depth","lat","lon")
    return spice_CT, spice_SA
def _make_density_levels(densmin, densmax, densinterval):
    levels = np.arange(densmin, densmax + densinterval * 0.5, densinterval, dtype=np.float64)
    return np.round(levels, 10).astype(np.float32)
@njit(cache=True)
def _interp_one_profile(d, t, s, p, sigma, out_t, out_s, out_p):
    nz = d.size
    ns = sigma.size

    count = 0
    for k in range(nz):
        if np.isfinite(d[k]) and np.isfinite(t[k]) and np.isfinite(s[k]) and np.isfinite(p[k]):
            count += 1
    if count < 2:
        return

    dv = np.empty(count, np.float64)
    tv = np.empty(count, np.float64)
    sv = np.empty(count, np.float64)
    pv = np.empty(count, np.float64)

    ii = 0
    for k in range(nz):
        if np.isfinite(d[k]) and np.isfinite(t[k]) and np.isfinite(s[k]) and np.isfinite(p[k]):
            dv[ii] = d[k]
            tv[ii] = t[k]
            sv[ii] = s[k]
            pv[ii] = p[k]
            ii += 1

    order = np.argsort(dv)
    d1 = dv[order]
    t1 = tv[order]
    s1 = sv[order]
    p1 = pv[order]

    ndu = 1
    for k in range(1, count):
        if d1[k] != d1[k - 1]:
            ndu += 1
    if ndu < 2:
        return

    du = np.empty(ndu, np.float64)
    tu = np.empty(ndu, np.float64)
    su = np.empty(ndu, np.float64)
    pu = np.empty(ndu, np.float64)

    j = 0
    curd = d1[0]
    tsum = t1[0]
    ssum = s1[0]
    psum = p1[0]
    csum = 1

    for k in range(1, count):
        if d1[k] == curd:
            tsum += t1[k]
            ssum += s1[k]
            psum += p1[k]
            csum += 1
        else:
            du[j] = curd
            tu[j] = tsum / csum
            su[j] = ssum / csum
            pu[j] = psum / csum
            j += 1
            curd = d1[k]
            tsum = t1[k]
            ssum = s1[k]
            psum = p1[k]
            csum = 1

    du[j] = curd
    tu[j] = tsum / csum
    su[j] = ssum / csum
    pu[j] = psum / csum

    dmin = du[0]
    dmax = du[ndu - 1]

    for m in range(ns):
        sig = sigma[m]
        if sig < dmin or sig > dmax:
            continue

        lo = 0
        hi = ndu - 1
        while hi - lo > 1:
            mid = (lo + hi) // 2
            if du[mid] <= sig:
                lo = mid
            else:
                hi = mid

        x0 = du[lo]
        x1 = du[hi]
        if x1 == x0:
            continue

        w = (sig - x0) / (x1 - x0)
        out_t[m] = tu[lo] + w * (tu[hi] - tu[lo])
        out_s[m] = su[lo] + w * (su[hi] - su[lo])
        out_p[m] = pu[lo] + w * (pu[hi] - pu[lo])
@njit(parallel=True, cache=True)
def _interp_density_block_numba(dens, temp, sali, pres, sigma):
    shape_out = dens.shape[:-1]
    nz = dens.shape[-1]
    ns = sigma.size
    nprof = 1
    for v in shape_out:
        nprof *= v

    dens2 = dens.reshape(nprof, nz)
    temp2 = temp.reshape(nprof, nz)
    sali2 = sali.reshape(nprof, nz)

    if pres.ndim == 1:
        pres2 = np.empty((nprof, nz), np.float32)
        for i in prange(nprof):
            for k in range(nz):
                pres2[i, k] = pres[k]
    else:
        pres2 = pres.reshape(nprof, nz)

    out_temp = np.full((nprof, ns), np.nan, np.float32)
    out_sali = np.full((nprof, ns), np.nan, np.float32)
    out_pres = np.full((nprof, ns), np.nan, np.float32)

    for i in prange(nprof):
        _interp_one_profile(dens2[i], temp2[i], sali2[i], pres2[i], sigma, out_temp[i], out_sali[i], out_pres[i])

    return (out_temp.reshape(shape_out + (ns,)), out_sali.reshape(shape_out + (ns,)), out_pres.reshape(shape_out + (ns,)))
def interp_ARGO_to_density(ARGO, densmin, densmax, densinterval, compute=False, n_threads=None):
    if n_threads is None:
        n_threads = os.cpu_count() or 1

    sigma = _make_density_levels(densmin, densmax, densinterval)

    time = pd.to_datetime(ARGO["time"]().values)
    lon = ARGO["lon"]()
    lat = ARGO["lat"]()
    pres = ARGO["depth"]().astype(np.float32)

    chunks = {"time": 2, "depth": -1, "lat": 45, "lon": 90}

    temp = ARGO["temp"]().transpose("time", "depth", "lat", "lon").chunk(chunks)
    sali = ARGO["sali"]().transpose("time", "depth", "lat", "lon").chunk(chunks)
    dens = ARGO["dens"]().transpose("time", "depth", "lat", "lon").chunk(chunks)

    sigma_da = xr.DataArray(sigma, dims=("density",), coords={"density": sigma})

    temp_i, sali_i, pres_i = xr.apply_ufunc(_interp_density_block_numba, dens, temp, sali, pres, sigma_da, input_core_dims=[["depth"], ["depth"], ["depth"], ["depth"], ["density"]], output_core_dims=[["density"], ["density"], ["density"]], exclude_dims={"depth"}, vectorize=False, dask="parallelized", output_dtypes=[np.float32, np.float32, np.float32], dask_gufunc_kwargs={"allow_rechunk": True, "output_sizes": {"density": len(sigma)}})

    temp_i = temp_i.transpose("time", "density", "lat", "lon")
    sali_i = sali_i.transpose("time", "density", "lat", "lon")
    pres_i = pres_i.transpose("time", "density", "lat", "lon")

    res = xr.Dataset(data_vars={"temp": temp_i, "sali": sali_i, "pres": pres_i}, coords={"time": time, "density": sigma, "lat": lat.values, "lon": lon.values})

    if compute:
        with dask.config.set(scheduler="threads", num_workers=n_threads):
            res = res.compute()

    return res
def mbb(series, nboot=10000, block=None, level=0.95, seed=1234, stats_fn=None, batch=500, to_per_decade=True):
    SEC_PER_DECADE = 10.0 * 365.2425 * 24.0 * 3600.0
    names = list(series)
    t = pd.DatetimeIndex(pd.Series(series[names[0]]).index)
    td = (t - t[0]).total_seconds().to_numpy() / (SEC_PER_DECADE if to_per_decade else SEC_PER_DECADE / 10.0)
    Y = np.column_stack([np.asarray(pd.Series(series[k]).reindex(t).values, dtype=float) for k in names])
    n, k = Y.shape

    b0 = np.full(k, np.nan)
    a0 = np.full(k, np.nan)
    R = np.full_like(Y, np.nan)
    r1s = []
    for j in range(k):
        m = np.isfinite(Y[:, j])
        b0[j], a0[j] = np.polyfit(td[m], Y[m, j], 1)
        R[m, j] = Y[m, j] - (b0[j] * td[m] + a0[j])
        res = R[m, j]
        r1 = np.corrcoef(res[:-1], res[1:])[0, 1] if res.size > 4 else 0.0
        r1s.append(0.0 if not np.isfinite(r1) else min(max(float(r1), 0.0), 0.99))
    r1max = max(r1s)

    if block is None:
        block = int(np.ceil(2.0 * (1.0 + r1max) / (1.0 - r1max)))
    L = int(min(max(block, 6), max(n // 5, 6)))
    nblk = int(np.ceil(n / L))

    rng = np.random.default_rng(seed)
    bb = np.empty((nboot, k), dtype=float)
    for i0 in range(0, nboot, batch):
        i1 = min(i0 + batch, nboot)
        st = rng.integers(0, n, size=(i1 - i0, nblk))
        idx = (st[:, :, None] + np.arange(L)[None, None, :]) % n
        idx = idx.reshape(i1 - i0, nblk * L)[:, :n]
        Rs = R[idx, :]
        Ys = b0[None, None, :] * td[None, :, None] + a0[None, None, :] + Rs
        w = np.isfinite(Ys).astype(float)
        Sw = w.sum(axis=1)
        St = (w * td[None, :, None]).sum(axis=1)
        Stt = (w * (td ** 2)[None, :, None]).sum(axis=1)
        Yf = np.where(np.isfinite(Ys), Ys, 0.0)
        Sy = (w * Yf).sum(axis=1)
        Sty = (w * td[None, :, None] * Yf).sum(axis=1)
        den = Stt - St ** 2 / np.where(Sw == 0, np.nan, Sw)
        bb[i0:i1, :] = (Sty - St * Sy / np.where(Sw == 0, np.nan, Sw)) / np.where(den == 0, np.nan, den)

    est = {nm: float(b0[j]) for j, nm in enumerate(names)}
    boot = {nm: bb[:, j] for j, nm in enumerate(names)}
    if stats_fn is not None:
        for nm, v in stats_fn({nm2: np.array([b0[j2]]) for j2, nm2 in enumerate(names)}).items():
            est[nm] = float(np.asarray(v).ravel()[0])
        for nm, v in stats_fn(boot).items():
            boot[nm] = np.asarray(v, dtype=float)

    q = [(1.0 - level) / 2.0 * 100.0, (1.0 + level) / 2.0 * 100.0]
    keys = list(est)
    lo = pd.Series({nm: float(np.nanpercentile(boot[nm], q[0])) for nm in keys})
    hi = pd.Series({nm: float(np.nanpercentile(boot[nm], q[1])) for nm in keys})
    info = {'n': int(n), 'block': int(L), 'nboot': int(nboot), 'r1max': float(r1max), 'level': float(level), 'seed': int(seed)}
    return pd.Series(est)[keys], lo, hi, pd.DataFrame(boot), info
