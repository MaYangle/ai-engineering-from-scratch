"""The parse-early trap.

One call's `arguments` arriving as three chunks. Same buffer, three moments,
three different outcomes. The point: "完整" is not something you eyeball — it is
a signal the provider sends.

Run: python .workbuddy/explorations/phase13-l03/parse_early_trap.py
"""

import json

CHUNKS = ['{"city"', ':"Beng', 'aluru"}']

print("模型发出的三个 arguments 分片:", CHUNKS)

buf = ""
for i, chunk in enumerate(CHUNKS, 1):
    buf += chunk
    print(f"\n收完第 {i} 片后  buf = {buf!r}")
    try:
        print("  json.loads ->", json.loads(buf))
    except json.JSONDecodeError as e:
        print(f"  json.loads 抛异常: {type(e).__name__} - {e.msg} (pos {e.pos})")

print("\n三片收齐后 parse ->", json.loads(buf))
print("\n所以结束判据不是'看起来完整了'，而是 provider 的结束信号：")
print("  OpenAI   finish_reason == 'tool_calls'")
print("  Anthropic content_block_stop")
print("  Gemini   stream-end")
