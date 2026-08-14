import sys
import types
sys.modules['cgi'] = types.ModuleType('cgi')
sys.path.insert(0, r'C:\Users\clocatelli\web2py')

import glob
import os
import pickle

print("\n--- SPECIFIC TICKET DETAIL ---")
tpath = r'C:\Users\clocatelli\web2py\applications\Viveiro_Analises\errors\127.0.0.1.2026-08-10.14-01-46.de955503-d15f-418f-9d28-38e0cdfe0e97'
with open(tpath, 'rb') as f:
    tdata = pickle.load(f)
print("Traceback:")
print(tdata.get('traceback'))

snapshot = tdata.get('snapshot', {})
print("\n--- DUMPS IN FRAMES ---")
frames = snapshot.get('frames', [])
for i, frame in enumerate(frames):
    print(f"Frame {i}: file={frame.get('file')}, func={frame.get('func')}, lnum={frame.get('lnum')}")
    dump = frame.get('dump', {})
    print(f"  Dump keys: {list(dump.keys()) if hasattr(dump, 'keys') else 'Not a dict'}")
    if hasattr(dump, 'items'):
        for k, v in dump.items():
            if 'configuration' in k or 'app' in k or 'version' in k:
                print(f"    {k}: {repr(v)[:200]}")






