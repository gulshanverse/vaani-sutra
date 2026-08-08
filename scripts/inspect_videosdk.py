import inspect
import re
import pathlib
import videosdk.agents as va
from videosdk.agents.job import RoomOptions, JobContext, WorkerJob, Options
from videosdk.agents import AgentSession

print('videosdk.agents package file:', va.__file__)

for cls in (RoomOptions, JobContext, WorkerJob, Options, AgentSession):
    try:
        mod = inspect.getmodule(cls)
        print('\n---', cls.__name__, 'module:', mod.__file__)
        if hasattr(cls, '__init__'):
            try:
                print(cls.__name__, '.__init__ signature:', inspect.signature(cls.__init__))
            except Exception as e:
                print('Could not get signature for', cls.__name__, e)
        if hasattr(cls, 'start'):
            try:
                print(cls.__name__, '.start signature:', inspect.signature(getattr(cls, 'start')))
            except Exception as e:
                pass
    except Exception as e:
        print('Error inspecting', cls, e)

# Search package files for 'playground'
print('\nSearching for "playground" in package files...')
root = pathlib.Path(va.__file__).parent
found = []
for f in root.rglob('*.py'):
    try:
        txt = f.read_text(errors='ignore')
    except Exception:
        continue
    if re.search(r'playground', txt, re.I):
        # show a few matching lines
        lines = txt.splitlines()
        for i,l in enumerate(lines):
            if re.search(r'playground', l, re.I):
                context = '\n'.join(lines[max(0,i-2):i+3])
                print('\nFOUND in', f, 'line', i+1)
                print(context)
        found.append(f)

if not found:
    print('No playground references found in videosdk.agents package')
else:
    print('\nSummary: playground references in', len(found), 'files')

print('\nDone')
