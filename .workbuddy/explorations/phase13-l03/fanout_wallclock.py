"""as-soon-as-complete vs wait-for-all: which clock actually changes?

T[i]   = when call i's `arguments` finish streaming
LAT[i] = executor latency of call i

Strategy A (this lesson's replay_and_execute): submit call i the moment its
           args complete          -> finish[i] = T[i] + LAT[i]
Strategy B (wait, then submit all): one barrier at max(T)
                                   -> finish[i] = max(T) + LAT[i]

Run: python .workbuddy/explorations/phase13-l03/fanout_wallclock.py
"""

SCENARIOS = [
    ("等长 executor（题面给的数字）", [1.0, 2.0, 3.0], [0.4, 0.4, 0.4]),
    ("第一条的 executor 特别慢", [1.0, 2.0, 3.0], [5.0, 0.1, 0.1]),
    ("最后一条的 executor 特别慢", [1.0, 2.0, 3.0], [0.1, 0.1, 5.0]),
]

for name, T, LAT in SCENARIOS:
    a = [t + l for t, l in zip(T, LAT)]
    b = [max(T) + l for l in LAT]
    print(f"\n=== {name} ===")
    print(f"  args 完成时刻 T   : {T}")
    print(f"  executor 延迟 LAT : {LAT}")
    print(f"  A 各调用完成      : {[round(x, 2) for x in a]}")
    print(f"  B 各调用完成      : {[round(x, 2) for x in b]}")
    print(f"  第一个结果  A={round(min(a), 2)}s  B={round(min(b), 2)}s"
          f"   -> 提前 {round(min(b) - min(a), 2)}s")
    print(f"  全部收工    A={round(max(a), 2)}s  B={round(max(b), 2)}s"
          f"   -> 差 {round(max(b) - max(a), 2)}s")
