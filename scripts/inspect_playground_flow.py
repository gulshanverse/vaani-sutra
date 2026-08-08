import inspect
import pathlib
import re
import videosdk.agents as va
from videosdk.agents import RoomOptions, JobContext, WorkerJob, Options, AgentSession, Worker
from videosdk.agents.worker import WorkerOptions
import videosdk.agents.backend as backend

print('videosdk.agents file:', va.__file__)
for name, obj in [
    ('RoomOptions', RoomOptions),
    ('JobContext', JobContext),
    ('WorkerJob', WorkerJob),
    ('Options', Options),
    ('AgentSession', AgentSession),
    ('Worker', Worker),
    ('WorkerOptions', WorkerOptions),
]:
    mod = inspect.getmodule(obj)
    print(f'\n=== {name} ===')
    print('module:', mod.__file__ if mod else 'unknown')
    try:
        print('signature:', inspect.signature(obj.__init__))
    except Exception as e:
        print('signature error:', e)
    try:
        src = inspect.getsource(obj)
        print('source lines:', len(src.splitlines()))
    except Exception as e:
        print('source error:', e)

print('\n=== backend classes ===')
for name in ['BackendConnection','JobAssignment','JobTermination','AvailabilityRequest','AvailabilityResponse','JobUpdate']:
    obj = getattr(backend, name, None)
    print(name, 'found' if obj else 'missing', 'module', inspect.getmodule(obj).__file__ if obj else None)
    if obj:
        try:
            src = inspect.getsource(obj)
            print('src lines:', len(src.splitlines()))
        except Exception as e:
            print('source error:', e)

root = pathlib.Path(va.__file__).parent
patterns = ['playground', 'join_meeting', 'room_id', 'meeting_id', 'jobctx', 'WorkerJob', 'roomOptions', 'RoomOptions']
for p in patterns:
    print(f'\n== pattern {p} ==')
    matches = []
    for f in root.rglob('*.py'):
        try:
            text = f.read_text(errors='ignore')
        except Exception:
            continue
        if re.search(p, text, re.I):
            matches.append(str(f.relative_to(root)))
    print(len(matches), 'files')
    for m in matches[:20]:
        print(' ', m)
