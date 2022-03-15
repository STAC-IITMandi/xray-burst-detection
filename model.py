# Implement statistical algorithm here
import time

def evaluate(ts, fs):
    # Dummy temporary value for testing UI
    # At least return start, end, max times for each burst detected
    # everything else is optional
    time.sleep(1)
    return [
        {
        'start_time':ts[5120],
        'end_time':ts[5870],
        'max_time':ts[5301],
        'bg_mean_flux':950.32187,
        'class':'B',
        },{
        'start_time':ts[13100],
        'end_time':ts[14200],
        'max_time':ts[14088],
        'bg_mean_flux':450.32187,
        'class':'A',
        },
    ]
