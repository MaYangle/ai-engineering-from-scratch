"""What does the isinstance guard actually let through?

Prints n and buf AFTER EVERY iteration — that is the hand-trace the learner was
asked to write out and skipped. Run it to see the per-step values.

Run: python .workbuddy/explorations/phase13-l03/guard_probe.py
"""

chunks = ["ab", 7, None, "cd", b"ef"]

buf = ""
n = 0
for i, chunk in enumerate(chunks, 1):
    is_str = isinstance(chunk, str)
    if is_str:
        buf += chunk
        n += 1
    print(
        f"  第 {i} 轮  chunk={chunk!r:<8} "
        f"isinstance(chunk, str)={str(is_str):<5} -> n={n}  buf={buf!r}"
    )

print(f"\n最终输出 : {n} {buf!r}")
print(f"           {n} {buf!r}".replace(f"{n}", str(n)))

print("\n补充：就算你以为 7 能混进去，字符串拼接也不答应——")
try:
    "ab" + 7
except TypeError as e:
    print(f"  'ab' + 7  ->  TypeError: {e}")
print("  注意 bytes 也是 '不是 str'：", isinstance(b"ef", str), "(b'ef' 是 bytes)")
