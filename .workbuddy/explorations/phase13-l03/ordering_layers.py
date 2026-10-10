"""Three different "order" questions hide in L03's demo 2. Only one is real disorder.

  layer 1: what order do the call_stop events arrive in?
  layer 2: where do each call's delta chunks land on the single stream?
  layer 3: in what order do the executors actually finish (wall clock)?

Run: python .workbuddy/explorations/phase13-l03/ordering_layers.py
"""

import importlib.util
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "phases/13-tools-and-protocols/03-parallel-and-streaming-tool-calls/code/main.py"

spec = importlib.util.spec_from_file_location("l03_main", SRC)
m = importlib.util.module_from_spec(spec)
sys.modules["l03_main"] = m
spec.loader.exec_module(m)

stream = list(m.fake_openai_stream())

print("完整事件序列：")
for i, e in enumerate(stream, 1):
    print(f"  {i:>2}. {e['type']:<10} {e.get('id', ''):<7} {e.get('chunk', '')!r}")

stops = [e["id"] for e in stream if e["type"] == "call_stop"]
print("\n[层 1] call_stop 出现顺序 :", " -> ".join(stops))

for cid in ("call_A", "call_B", "call_C"):
    pos = [i for i, e in enumerate(stream, 1)
           if e["type"] == "args_delta" and e.get("id") == cid]
    print(f"        {cid} 的分片落在事件 {pos}")
print("        -> 三条线交错在同一条流上，但每条线内部的分片仍严格有序")

print("\n[层 3] executor 真实完成顺序（用 as_completed 观察）：")
for label, lat in (
    ("原始延迟 400/600/800", {"Bengaluru": 400, "Tokyo": 600, "Zurich": 800}),
    ("翻转延迟 800/600/400", {"Bengaluru": 800, "Tokyo": 600, "Zurich": 400}),
):
    m.SIMULATED_LATENCY_MS.update(lat)
    cities = ["Bengaluru", "Tokyo", "Zurich"]
    with ThreadPoolExecutor(max_workers=3) as pool:
        futs = {c: pool.submit(m.executor_weather, c) for c in cities}
        rev = {f: c for c, f in futs.items()}
        done = [rev[f] for f in as_completed(futs.values())]
        results = {c: f.result() for c, f in futs.items()}
    print(f"        {label}: 完成顺序 {' -> '.join(done)}")
    print(f"          结果仍按 id 归位 : "
          f"{ {c: results[c]['temp_c'] for c in cities} }")
