# DoneWitness

**AI 说完成了，让应用行为和证据来回答。**

[English](../README.md) · [v0.2.0 发布说明](https://github.com/Drippinblood333/DoneWitness/releases/tag/v0.2.0) · [PyPI](https://pypi.org/project/donewitness/)

DoneWitness 是面向本地 Web 应用的独立验收 CLI。它执行你预先审阅的验收计划，
运行真实 Chromium，并生成可检查的 **PASS / FAIL / UNKNOWN** 回执。
运行时不需要大模型、账号或云服务。

## 页面说“保存成功”，真的保存了吗？

项目自带一个小型记账示例。同一份验收计划，对三种实现得到不同结果：

| 实现 | 输入校验 | 金额与表单状态 | 返回页面后数据仍在 |
| --- | --- | --- | --- |
| 正常应用 | PASS | PASS | PASS |
| 金额算错 | PASS | **FAIL** | PASS |
| 假保存 | PASS | PASS | **FAIL** |

这是实际浏览器执行的受控故障演示。示例使用 localStorage，证明的是这些检查能发现
相应故障，不代表验证了生产数据库，也不代表能够发现所有问题。

## 开始使用

准备 Python 3.12–3.14，建议在虚拟环境中安装：

```console
python -m pip install donewitness==0.2.0
python -m playwright install chromium
donewitness --version
```

下载与版本匹配的示例，然后校验计划格式：

```console
git clone --depth 1 --branch v0.2.0 https://github.com/Drippinblood333/DoneWitness.git
cd DoneWitness
donewitness validate --plan examples/expenses.plan.json
```

运行正常应用并检查证据完整性：

```console
donewitness verify --plan examples/expenses.plan.json --base-url http://127.0.0.1:8765 --run-dir .donewitness/expenses --app-command python examples/expenses_app.py
donewitness inspect --run-dir .donewitness/expenses
```

用同一份计划检测“假保存”：

```console
donewitness verify --plan examples/expenses.plan.json --base-url http://127.0.0.1:8765 --run-dir .donewitness/fake-save --app-command python examples/expenses_app.py --fault fake-save
```

持久化检查应返回 **FAIL**，命令退出码为 1。每次执行需使用新的运行目录。
`--app-command` 必须是最后一个 DoneWitness 参数，之后的内容全部属于应用启动命令。
Linux 可能需要额外安装 Chromium 系统依赖，参见 [CLI 指南](CLI_REFERENCE.md)。

## v0.2.0 的改进

- 新增文本、输入值、元素数量和隐藏状态四类断言，使用显式 Plan v3。
- 离线 `validate` 在启动应用前检查格式和摘要；格式有效不等于应用验收通过。
- 延迟加载执行依赖。本机帮助/版本查询启动中位耗时分别约为 **416→130 ms**、
  **420→120 ms**；仅指 CLI 启动，不代表浏览器验证整体提速。
- 应用启动阶段被中断时，仍保存不完整的 UNKNOWN 回执。
- 保持既有 Plan v1/v2 契约和摘要，不增加运行依赖。

性能数据来自 Windows/Python 3.14.3，同环境交替执行，每条命令每个版本测量 15 次。
[原始数据与验证记录](releases/v0.2.0-evidence.md)公开了测量方式与限制。

## 用到自己的项目

先审阅验收标准，再修改 [示例计划](../examples/expenses.plan.json)中的操作和断言。
依次执行 `validate`、`verify`、`inspect`，查看每项结果及其证据。

| 退出码 | 含义 |
| --- | --- |
| 0 | PASS：声明的检查全部通过 |
| 1 | FAIL：检查发现行为与预期矛盾 |
| 2 | 参数或计划无效 |
| 3 | UNKNOWN / 不完整：执行或证据不足以得出结论 |

PASS 只覆盖你写下的检查，遗漏需求不会自动补全。默认直接执行模式使用你的用户权限；
可选 Docker 模式也不构成恶意代码安全保证。截图和 trace 属于可选库级捕获，默认不会开启。
证据摘要用于发现不一致，不是防伪签名。

[计划格式](PLANS.md) · [完整 CLI](CLI_REFERENCE.md) · [安全与隐私](SECURITY_AND_PRIVACY.md) · [贡献指南](../CONTRIBUTING.md)

欢迎通过 [Issues](https://github.com/Drippinblood333/DoneWitness/issues) 分享可复现的问题，
尤其是漏掉的故障或难以理解的 UNKNOWN。请去除敏感信息；漏洞使用[私密报告渠道](../SECURITY.md)。
