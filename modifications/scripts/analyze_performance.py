#!/usr/bin/env python3
"""Summarize real native JSONL frame captures without substituting UI timestamps.
Usage: python3 analyze_performance.py capture.jsonl [capture2.jsonl ...]
Native capture files can contain short ring-buffer windows, not a whole session.
"""
from pathlib import Path
import sys,json,math,statistics,collections
def summarize(paths):
    frames=[];unique=set();invalid=0;classifications=collections.Counter()
    for path in paths:
        if path.stat().st_size>256*1024*1024:raise ValueError('Capture exceeds 256 MiB')
        with path.open(encoding='utf-8') as stream:
            for line in stream:
                try:row=json.loads(line)
                except json.JSONDecodeError:invalid+=1;continue
                if row.get('type')!='frame':continue
                value=row.get('frame_ms');key=(row.get('monotonic_ns'),row.get('frame'))
                if key in unique:continue
                if isinstance(value,bool) or not isinstance(value,(int,float)) or not math.isfinite(value) or value<=0:invalid+=1;continue
                unique.add(key);frames.append(float(value));labels=row.get('classification',['unknown']);classifications.update(labels if isinstance(labels,list) else [str(labels)])
    if not frames:raise ValueError('No valid native frame_ms records; five-second session averages are not frame times')
    ordered=sorted(frames)
    def percentile(p):return ordered[min(len(ordered)-1,max(0,math.ceil(p*len(ordered))-1))]
    slowest=ordered[-max(1,math.ceil(len(ordered)*0.01)):]
    bounds=[8.333,16.667,25,33.334,50,100];histogram=collections.Counter()
    for value in frames:histogram[next((f'<= {bound:g} ms' for bound in bounds if value<=bound),'> 100 ms')]+=1
    return {'sample_frames':len(frames),'sample_duration_s':sum(frames)/1000,'mean_fps':1000/statistics.mean(frames),'frame_ms_p50':percentile(.5),'frame_ms_p95':percentile(.95),'frame_ms_p99':percentile(.99),'percentile_method':'nearest rank','one_percent_low_fps':1000/statistics.mean(slowest),'histogram':dict(histogram),'classification_counts':dict(classifications),'invalid_or_truncated_records':invalid,'scope':'Captured native frame windows only; not necessarily the whole 10-minute session. Overlapping frames are deduplicated by timestamp and frame number.'}
if __name__=='__main__':
    if len(sys.argv)<2:raise SystemExit('Pass one or more native performance JSONL captures')
    print(json.dumps(summarize([Path(p) for p in sys.argv[1:]]),indent=2))
