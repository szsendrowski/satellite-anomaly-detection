import numpy as np
import matplotlib.pyplot as plt
from scipy import ndimage

# friendly import checks
try:
    from sunpy.map import Map
    from sunpy.net import Fido
    from sunpy.net import attrs as a
except Exception as e:
    print("Missing required solar-science packages:", e)
    print("Install them in the active environment, e.g.:")
    print("  pip install sunpy astropy numpy scipy matplotlib")
    raise

from astropy.time import Time, TimeDelta
from datetime import datetime
import numpy as _np
import ast
from pathlib import Path

def _to_py_datetime(t):
    if isinstance(t, datetime):
        dt = t
    else:
        tt = Time(t)
        try:
            dt = tt.to_datetime()
        except Exception:
            dt = tt.datetime
    if getattr(dt, "tzinfo", None) is not None:
        dt = dt.replace(tzinfo=None)
    return dt

def fetch_two_sequential_maps(time_start='2011-06-07 06:30:00', time_end='2011-06-07 06:40:00',
                              instrument=a.Instrument.lasco, detector=a.Detector.c2,
                              step_seconds=600, max_attempts=5):
    """
    Prosty fetcher: przesuwa okno czasowe i akumuluje pliki aż znajdzie >=2 użytecznych Map.
    Zwraca (map1, map2) - dwie kolejne mapy o najmniejszej różnicy czasowej.
    """
    t_start = Time(time_start)
    t_end = Time(time_end)
    if t_end <= t_start:
        t_end = t_start + TimeDelta(60, format='sec')

    collected_files = []
    attempt = 0
    while True:
        attempt += 1
        t_start_dt = _to_py_datetime(t_start)
        t_end_dt = _to_py_datetime(t_end)
        print(f"[Attempt {attempt}] Searching {t_start_dt.isoformat()} -> {t_end_dt.isoformat()}")
        try:
            result = Fido.search(a.Time(t_start_dt, t_end_dt), instrument, detector)
            fetched = Fido.fetch(result)
        except Exception as e:
            raise RuntimeError(f"Fido.search/fetch nie powiódł się: {e}")

        # flatten + normalize fetched -> list of strings
        files = []
        def _append_item(it):
            if it is None:
                return
            if isinstance(it, (list, tuple)):
                for sub in it:
                    _append_item(sub)
                return
            if isinstance(it, _np.ndarray):
                for sub in it.tolist():
                    _append_item(sub)
                return
            s = str(it).strip()
            # handle repr like "['C:\\path\\file']"
            if (s.startswith('[') and s.endswith(']')) or (s.startswith('(') and s.endswith(')')):
                try:
                    val = ast.literal_eval(s)
                    if isinstance(val, (list, tuple)):
                        for sub in val:
                            _append_item(sub)
                        return
                except Exception:
                    pass
            # strip surrounding quotes
            if (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
                s = s[1:-1].strip()
            if s:
                files.append(s)
        _append_item(fetched)

        # add unique files
        for p in files:
            if p not in collected_files:
                collected_files.append(p)

        print(f"  This window: found={len(files)}; total collected unique files={len(collected_files)}")

        # filter only existing files (some returned entries may be reprs that don't exist)
        collected_existing = []
        skipped = []
        for p in collected_files:
            if Path(p).exists():
                collected_existing.append(p)
            else:
                skipped.append(p)
        if skipped:
            print(f"  Skipped (not found) examples: {skipped[:5]} (total skipped {len(skipped)})")

        if len(collected_existing) >= 2:
            maps = []
            for p in collected_existing:
                try:
                    m = Map(p)
                except Exception as e:
                    print(f"  Warning: Map() failed for {p}: {e}")
                    continue
                print(f"  Loaded Map: {p}  date={m.date.iso}  shape={m.data.shape}")
                maps.append(m)

            if len(maps) >= 2:
                maps_sorted = sorted(maps, key=lambda m: m.date)
                # choose consecutive pair with smallest dt
                min_dt = None
                best_idx = 0
                for i in range(len(maps_sorted)-1):
                    dt = (maps_sorted[i+1].date - maps_sorted[i].date).sec
                    if (min_dt is None) or (dt < min_dt):
                        min_dt = dt
                        best_idx = i
                map1 = maps_sorted[best_idx]
                map2 = maps_sorted[best_idx+1]
                print(f"Selected maps:\n 1) {map1.filepath} ({map1.date.iso})\n 2) {map2.filepath} ({map2.date.iso})  delta={min_dt}s")
                return map1, map2
            else:
                print("  After Map() filtering less than 2 maps, continue collecting.")

        # check attempt limit
        if (max_attempts is not None) and (attempt >= max_attempts):
            raise RuntimeError(f"Nie znaleziono 2 użytecznych plików po {attempt} próbach (ostatnie okno {t_start_dt.isoformat()} -> {t_end_dt.isoformat()}).")

        # shift window forward
        t_start = t_start + TimeDelta(step_seconds, format='sec')
        t_end = t_end + TimeDelta(step_seconds, format='sec')

def fetch_two_sequential_maps_by_windows(start_time='2011-06-07 06:30:00',
                                         window_duration_seconds=900,
                                         step_seconds=900,
                                         n_windows=10,
                                         instrument=a.Instrument.lasco,
                                         detector=a.Detector.c2):
    """
    Przeszukuje kolejno n_windows okien:
      for i in range(n_windows):
        window_start = start_time + i*step_seconds
        window_end   = window_start + window_duration_seconds
      zbiera pliki z każdego okna (accumulate), filtruje istniejące pliki,
      ładuje Map() i wybiera parę dwóch kolejnych map o najmniejszym dt.
    Zwraca (map1, map2) albo rzuca wyjątek jeśli nie uda się zebrać 2 użytecznych map.
    """
    t0 = Time(start_time)
    collected_files = []

    for i in range(int(n_windows)):
        ws = t0 + TimeDelta(i * step_seconds, format='sec')
        we = ws + TimeDelta(window_duration_seconds, format='sec')
        ws_dt = _to_py_datetime(ws)
        we_dt = _to_py_datetime(we)
        print(f"[Window {i+1}/{n_windows}] Searching {ws_dt.isoformat()} -> {we_dt.isoformat()}")
        try:
            result = Fido.search(a.Time(ws_dt, we_dt), instrument, detector)
            fetched = Fido.fetch(result)
        except Exception as e:
            print(f"  Fido.search/fetch failed for window {i+1}: {e}")
            continue

        # tu użyj tej samej normalizacji co masz (flattens, ast.literal_eval, strip quotes)
        files = []
        def _append_item(it):
            if it is None:
                return
            if isinstance(it, (list, tuple)):
                for sub in it:
                    _append_item(sub)
                return
            if isinstance(it, _np.ndarray):
                for sub in it.tolist():
                    _append_item(sub)
                return
            s = str(it).strip()
            if (s.startswith('[') and s.endswith(']')) or (s.startswith('(') and s.endswith(')')):
                try:
                    val = ast.literal_eval(s)
                    if isinstance(val, (list, tuple)):
                        for sub in val:
                            _append_item(sub)
                        return
                except Exception:
                    pass
            if (s.startswith("'") and s.endswith("'")) or (s.startswith('"') and s.endswith('"')):
                s = s[1:-1].strip()
            if s:
                files.append(s)
        _append_item(fetched)

        # add unique
        for p in files:
            if p not in collected_files:
                collected_files.append(p)

        print(f"  Window found {len(files)} items; total collected unique files={len(collected_files)}")

    # po przejrzeniu wszystkich okien: filtruj istniejące pliki i próbuj Map()
    collected_existing = [p for p in collected_files if Path(p).exists()]
    print(f"Total existing files after scanning windows: {len(collected_existing)} (collected {len(collected_files)})")
    if len(collected_existing) < 2:
        raise RuntimeError("Nie znaleziono >=2 istniejących plików po przeskanowaniu okien.")

    maps = []
    bad = []
    for p in collected_existing:
        try:
            m = Map(p)
            maps.append(m)
            print(f" Loaded Map: {p} date={m.date.iso} shape={m.data.shape}")
        except Exception as e:
            bad.append((p, str(e)))
    if len(maps) < 2:
        raise RuntimeError("Po filtrowaniu Map() pozostało <2 map.")

    maps_sorted = sorted(maps, key=lambda m: m.date)
    min_dt = None
    best_idx = 0
    for i in range(len(maps_sorted)-1):
        dt = (maps_sorted[i+1].date - maps_sorted[i].date).sec
        if (min_dt is None) or (dt < min_dt):
            min_dt = dt
            best_idx = i
    map1 = maps_sorted[best_idx]
    map2 = maps_sorted[best_idx+1]
    return map1, map2

def main():
    import traceback
    import sys
    debug_path = Path("coronadata_error_debug.txt")
    try:
        # ustawienia czasu (zmieniaj wedle potrzeby)
        START_TIME = '2011-06-07 06:30:00'
        END_TIME   = '2011-06-07 06:40:00'
        STEP_SECONDS = 600
        MAX_ATTEMPTS = 5

        # pobierz mapy (może rzucić)
        map1, map2 = fetch_two_sequential_maps(START_TIME, END_TIME,
                                               instrument=a.Instrument.lasco, detector=a.Detector.c2,
                                               step_seconds=STEP_SECONDS, max_attempts=MAX_ATTEMPTS)

        # jeżeli trzeba, reprojektuj map2 do gridu map1
        if map1.data.shape != map2.data.shape:
            print("Różne rozmiary: próbuję reproject_to")
            try:
                map2 = map2.reproject_to(map1)
                print("Reprojekcja OK")
            except Exception as e:
                print("Reprojekcja nie powiodła się:", e)
                if map1.data.shape != map2.data.shape:
                    raise RuntimeError("map1 i map2 różne rozmiary i reproject_to nie powiodło się")

        # ---- tutaj stosujemy maskę którą podałeś ----
        mask_low = map2.data < (map2.data.max() * 0.10)   # True = low values to be masked out
        preserved = map2.data * (~mask_low)

        # wygładzenie i progowanie (jak w twoim wcześniejszym kodzie)
        smooth_sigma = 14
        processed = ndimage.gaussian_filter(preserved, smooth_sigma)
        abs_threshold = 100
        processed[processed < abs_threshold] = 0

        labels, n_regions = ndimage.label(processed > 0)

        diff = np.zeros_like(map1.data, dtype=float)
        if n_regions > 0:
            region_mask_total = (labels > 0)
            diff[region_mask_total] = map2.data[region_mask_total] - map1.data[region_mask_total]

        diff_map = Map(diff, map1.meta)

        # Rysowanie (jak wcześniej)...
        fig = plt.figure(figsize=(15,5))

        ax1 = fig.add_subplot(1,3,1, projection=map1)
        map1.plot(axes=ax1, title=f"Map 1\n{map1.date.iso}")
        map1.draw_grid(axes=ax1, color='white', alpha=0.3)

        ax2 = fig.add_subplot(1,3,2, projection=map2)
        map2.plot(axes=ax2, title=f"Map 2\n{map2.date.iso}")

        mask_labels = (labels > 0).astype(int)
        try:
            map2.draw_contours(mask_labels, levels=[0.5], colors='red', axes=ax2, linewidths=1.2, alpha=0.8)
        except Exception:
            ax2.contour(mask_labels, levels=[0.5], colors='red', origin='lower', linewidths=1.2, alpha=0.8)

        ax3 = fig.add_subplot(1,3,3, projection=diff_map)
        vmax = np.nanmax(np.abs(diff)) if np.any(diff) else 1.0
        artist = diff_map.plot(axes=ax3, cmap='seismic', vmin=-vmax, vmax=vmax,
                               title="Difference (map2 - map1) in detected regions")
        plt.colorbar(artist, ax=ax3, orientation='vertical', fraction=0.046, pad=0.04)

        plt.tight_layout()
        # Save a PNG so we can inspect output even if display is not available
        out_png = Path("coronadata_output.png")
        try:
            fig.savefig(out_png, dpi=150, bbox_inches='tight')
            print(f"Saved figure to {out_png.resolve()}")
        except Exception as e:
            print("Could not save figure:", e)
        # Show only if running with a display (this will block in GUI sessions)
        try:
            plt.show()
        except Exception:
            # headless backend may raise - in that case we've already saved the PNG
            pass
    except Exception as exc:
        # Zapisz pełny traceback + diagnostykę do pliku, oraz wypisz krótkie info na stdout
        tb = traceback.format_exc()
        with open(debug_path, "w", encoding="utf-8") as fh:
            fh.write("coronadata.py error debug\n\n")
            fh.write("Python version: " + sys.version + "\n\n")
            try:
                import sunpy
                fh.write("SunPy version: " + str(sunpy.__version__) + "\n\n")
            except Exception:
                fh.write("SunPy import failed\n\n")
            fh.write("Traceback:\n")
            fh.write(tb)
            fh.write("\n\n")
            # jeżeli mapy istnieją, spróbuj wypisać parę pomocnych info
            try:
                fh.write("Map1 summary:\n")
                fh.write(f"  map1: {map1.filepath} date={map1.date.iso} shape={getattr(map1,'data').shape}\n")
            except Exception:
                fh.write("  map1: not available\n")
            try:
                fh.write("Map2 summary:\n")
                fh.write(f"  map2: {map2.filepath} date={map2.date.iso} shape={getattr(map2,'data').shape}\n")
            except Exception:
                fh.write("  map2: not available\n")
        print("Wystąpił błąd — zapisałem szczegóły do coronadata_error_debug.txt")
        print(tb)