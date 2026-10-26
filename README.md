# Agent Foundation

可复用的应用起步仓库。它提供固定版本 DeerFlow 2.1.0、服务端模型配置、按用户隔离的 Markdown Wiki、可选语音接口，以及可组合的 Docker Compose 部署。应用仍需要自行定义业务工具、账户体系和产品界面。

## 已抽出的共同层

| 能力 | 本仓库提供 | 新应用需要接入 |
| --- | --- | --- |
| DeerFlow | 固定源码归档、配置生成、每次请求的运行入口 | 业务提示词、工具、授权、持久任务状态 |
| 模型与 API Key | `MODEL_CONFIG_JSON`、`PRIMARY_MODEL`、`api_key_env`、严格校验；生成配置只引用环境变量名 | 选择有权限的模型服务并在私密 `.env` 填 Key |
| LLM Wiki 记忆 | owner 隔离、Markdown 页面、检索、来源、哈希冲突保护 | 自动摘要/归档策略、保留期限、业务事实有效性规则 |
| 语音 | 可选 OpenAI 兼容 STT/TTS 服务端端点；浏览器可调用上传/播放 | 实时流式协议、VAD、打断、业务话轮控制和所选语音供应商适配 |
| 部署 | `compose.yaml` 与本地/外部模型叠加文件、健康检查、持久卷、部署时设置的单用户账号 | 域名、HTTPS、生产身份鉴权、备份与监控 |

仓库使用公开发布的 DeerFlow 提交 `e9074b7126833b5ca4739bcedcbbed01b211246c`。业务队列、业务权限、实时会议协议，以及领域工具和数据约束应由具体应用实现并测试。

## 快速开始

需要 Docker Compose。第一次运行：

```bash
./scripts/init.sh
# 在 .env 中填写 APP_ADMIN_USERNAME、APP_ADMIN_PASSWORD，配置模型与可选语音服务。不要提交 .env。
./scripts/up.sh local
```

`local` 会启动 Ollama 并拉取 `.env` 中 `OLLAMA_MODEL`（默认 `qwen2.5:3b`）。若使用外部 OpenAI 兼容模型，将 `.env` 改成下面的格式，然后运行 `./scripts/up.sh external`：

```dotenv
MODEL_CONFIG_JSON='[{"provider":"openai","model":"your-model-id","base_url":"https://your-provider.example/v1","api_key_env":"MODEL_API_KEY"}]'
PRIMARY_MODEL=your-model-id
MODEL_API_KEY=
```

`MODEL_CONFIG_JSON` 只写密钥变量名，不写密钥内容。生成的 DeerFlow YAML 使用 `$AGENT_RUNTIME_MODEL_KEY` 引用运行时变量。`/v1/status` 只报告配置状态，不回传 Key，也不声称外部端点已实际连通。Docker 只把 API 绑定到宿主机 `127.0.0.1`。

API 默认是单用户起步模式。部署时必须在私密 `.env` 中填写 `APP_ADMIN_USERNAME` 和至少 12 字符的 `APP_ADMIN_PASSWORD`；仓库不提供默认账号或密码。缺少任一项时，部署检查和 `/readyz` 都会失败。所有 `/v1/*` 路由使用 HTTP Basic 认证。例如：

```bash
curl --basic --user 'your-username' http://127.0.0.1:8787/v1/status
curl --basic --user 'your-username' -H 'Content-Type: application/json' \
  -d '{"message":"总结我已经保存的偏好"}' http://127.0.0.1:8787/v1/chat
```

保存 Wiki 页面：

```bash
curl -X PUT --basic --user 'your-username' -H 'Content-Type: application/json' \
  -d '{"text":"# 偏好\n回答请简洁。","expected_sha256":null,"source":"user-confirmed"}' \
  http://127.0.0.1:8787/v1/wiki/long-term/preferences.md
```

后续修改需要带上 GET 返回的 `sha256`。相同 owner 的相关页面会被检索并作为历史语境送入 Agent；这些内容不代表实时事实，也不会扩大工具权限。首次使用没有自动写入长期记忆，应用应按自己的确认、来源与过期规则添加自动归档。

## 扩展应用

入口是 `agent_foundation.app.create_app(identity_resolver=...)`。默认 resolver 使用服务端配置的管理员用户名作为 Wiki owner，只适合个人本机使用。多用户应用必须从自己的登录态解析 owner，不接受客户端传入的 owner ID，并为角色权限和隔离编写测试。HTTP Basic 凭证每次请求都会发送；对外提供服务前必须接入 HTTPS 和正式认证。

`agent_foundation.deerflow.build_config()` 可传业务工具清单、授权 provider 和提示词。提供工具时若缺少授权 provider 会直接报错。业务工具应在每个调用时重新校验 owner、run 和操作权限。起步 API 默认没有业务工具，DeerFlow 的每次 chat 是独立运行；需要持续线程、队列、checkpoint 的应用应在自己的数据层接入。

`agent_foundation.wiki.WikiStore` 是可运行的基础记忆存储。若需要每日归档、留存或权威业务记录，可以在其上层写 projector，或替换存储实现。语音接口支持文件转写和 MP3 合成；低延迟流式通话应由独立语音适配器接入，不能把上传接口当成实时协议。

## 验证

```bash
# 在 Python 3.12 虚拟环境中先安装依赖：python3.12 -m venv .venv && .venv/bin/pip install -e '.[test]'
PYTHONPATH=src .venv/bin/python -m unittest discover -s tests -v
docker compose --env-file .env -f compose.yaml -f compose.local.yaml config --quiet
```

仓库中的 `vendor/deerflow/provenance.json` 保存公开源码提交和归档 SHA-256。DeerFlow 归档保留其上游 MIT 许可。私密 `.env`、运行状态与 Wiki 都在 Git 忽略范围内。

## 许可与公开发布

本项目原创部分使用 [MIT 许可](LICENSE)，允许个人和商业使用、修改及再分发，并要求保留版权与许可声明。仓库内的 DeerFlow 归档继续遵循其上游 MIT 许可及版权声明。

发布前请按 [公开发布检查](docs/PUBLISHING.md) 核对代码权属、凭证与 Git 历史。
