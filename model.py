
import numpy as np
from scipy.signal import find_peaks, peak_prominences, peak_widths
from scipy.ndimage import gaussian_filter

def evaluate(ts, fs):
    # df={'Info':[],'Peaks':[],'Peak_Widths':[],'Peak_Rise':[],'Peak_Fall':[],'Peak_Start':[],'Peak_Stop':[]}
    found = []
                
    g=gaussian_filter(fs, sigma=5)
    #plt.plot(table['TIME'],g)
    peaks, _ = find_peaks(g)
                
    prominences, _, _ = peak_prominences(g, peaks)
    if len(prominences) == 0:
        return []
                
    selected = prominences > 0.5 * (np.min(prominences) + np.max(prominences))
    if len(selected) == 0:
        return []
    #left = peaks[:-1][selected[1:]]
    #right = peaks[1:][selected[:-1]]
    top = peaks[selected]
    if len(top) > 10:
        return []
    eigth_peak_widths = peak_widths(g, top, rel_height = 0.8)        
                
    per=np.percentile(g,75)

    # df['Info'].extend(['filename' for i in range(len(top))])
    # df['Peaks'].extend(g[top])
    # df['Peak_Widths'].extend(list(eigth_peak_widths[0]))
    # df['Peak_Rise'].extend(list(np.array(top) - np.array(eigth_peak_widths[2])))
    # df['Peak_Fall'].extend(list(np.array(eigth_peak_widths[3]) - np.array(top)))
    # df['Peak_Start'].extend(list(eigth_peak_widths[2]))
    # df['Peak_Stop'].extend(list(eigth_peak_widths[3]))
    print(eigth_peak_widths, g[top], g, top)
    for i in range(len(g[top])):
        print(eigth_peak_widths[2][i], type(eigth_peak_widths[2][i]))
        found.append({
            'start_time':ts[int(eigth_peak_widths[2][i])],
            'end_time':ts[int(eigth_peak_widths[3][i])],
            'max_time':ts[int(g[top][i])],
            'peak_width':eigth_peak_widths[0][i],
            'peak_risetime' : top[i] - eigth_peak_widths[2][i],
            'peak_falltime' : eigth_peak_widths[3][i] - top[i],
        })
    print(*found, sep='\n')
    return found

# detected = []
# for i in range(len(t_strt)):
#     b = {
#         'start_time':t_strt[i],
#         'end_time':t_end[i],
#         'max_time':t_peak[i],
#         'rise_duration':t_peak[i]-t_strt[i],
#         'decay_duration':t_end[i]-t_peak[i],
#         'width':t_rise[-1]+t_decay[-1],
#     }
    
#     detected.append(b)