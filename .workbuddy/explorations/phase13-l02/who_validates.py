"""What does "who owns the validation authority" actually mean?

Same schema, same model output, three worlds. The only thing that changes is
WHERE the checker sits — on the provider/host boundary, nowhere, or inside the
host. Watch what happens to one out-of-enum value.

Run: python .workbuddy/explorations/phase13-l02/who_validates.py
"""

import json

SCHEMA = {
    "type": "object",
    "properties": {
        "city": {"type": "string"},
        "units": {"type": "string", "enum": ["celsius", "fahrenheit"]},
    },
    "required": ["city", "units"],
    "additionalProperties": False,
}

# what the model "wants" to emit this turn: units is outside the enum
RAW = '{"city": "Bengaluru", "units": "Kelvin"}'


def validate(args, schema):
    errs = []
    for k in schema["required"]:
        if k not in args:
            errs.append(f"缺少必填字段 {k}")
    for k, v in args.items():
        spec = schema["properties"].get(k)
        if spec is None:
            if schema.get("additionalProperties") is False:
                errs.append(f"多余字段 {k}")
            continue
        if "enum" in spec and v not in spec["enum"]:
            errs.append(f"{k}={v!r} 不在 enum {spec['enum']} 里")
    return errs


def provider_strict(raw):
    args = json.loads(raw)
    errs = validate(args, SCHEMA)      # 校验器站在 provider 这一侧
    return args, errs


def provider_lax(raw):
    return json.loads(raw), []         # 边界上没人


def host_execute(args):
    units = args["units"]
    if units == "celsius":
        return "Bengaluru 31C"
    if units == "fahrenheit":
        return "Bengaluru 88F"
    return f"Bengaluru ??? (units={units!r} 不认识)"


print("模型本轮想发出的参数 :", RAW)
print("schema 只允许 units =", SCHEMA["properties"]["units"]["enum"])

print("\n--- 世界 A：有 strict，校验站站在 provider 和 host 之间 ---")
args, errs = provider_strict(RAW)
if errs:
    print("  provider 侧校验 :", errs)
    print("  provider 拒收   : 参数根本出不了门，模型必须重采样")
    print("  结果            : host 一行代码都没跑到，永远不知道有过一个 Kelvin")
else:
    print("  host 执行 :", host_execute(args))

print("\n--- 世界 B：无 strict，这条边界上没有任何校验器 ---")
args, errs = provider_lax(RAW)
print("  边界校验 : 无，直接放行")
print("  host 收到的字典 :", args)
print("  host 直接执行   :", host_execute(args))
print("  <- 越界值一路穿进业务代码，全程没有任何一行报错")

print("\n--- 世界 B 打补丁：host 自己建校验站，把校验权搬回来 ---")
args = json.loads(RAW)
errs = validate(args, SCHEMA)
print("  host 侧校验 :", errs)
print("  回注 tool result:", json.dumps({"error": errs}, ensure_ascii=False))
print("  <- 越界值在 host 边界被拦下，模型拿到错误消息后重试")
