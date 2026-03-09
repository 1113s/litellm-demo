# Demo Architecture: Providers, Logical Routes, and Fallbacks

This demo uses **LiteLLM as a gateway router** over three upstream providers:

- GLM (Zhipu)
- DeepSeek
- Qwen (DashScope)

## 1) Provider Layer

Configured upstream provider credentials are all read from environment variables:

- `ZHIPU_API_KEY`
- `DEEPSEEK_API_KEY`
- `DASHSCOPE_API_KEY`

No provider key is hardcoded in repo.

## 2) Logical Model Aliases

We expose two **logical** model aliases to northbound clients:

## `router/default-fast`

Purpose:
- low-latency default for chat-heavy demo requests
- lower-cost profile for iterative interactions

Deployments behind this alias:
- `zhipuai/glm-4-flash`
- `deepseek/deepseek-chat`

Expected behavior:
- router picks one deployment using `simple-shuffle`
- if this logical route fails, it falls back to `router/default-balanced`

## `router/default-balanced`

Purpose:
- better quality/stability balance for “primary” demo route
- cross-provider redundancy

Deployments behind this alias:
- `zhipuai/glm-4-plus`
- `dashscope/qwen-plus`
- `deepseek/deepseek-chat`

Expected behavior:
- router picks one deployment using `simple-shuffle`
- acts as fallback target for `router/default-fast`

## 3) Fallback Policy

Configured fallback chain:

- `router/default-fast` -> `router/default-balanced`

Meaning:
- if all active deployments under `router/default-fast` fail, LiteLLM retries via `router/default-balanced`

## 4) Observability and Logging

- `success_callback: ["prometheus"]`
- `failure_callback: ["prometheus"]`
- `json_logs: true`
- `set_verbose: true`

This gives demo-friendly routing visibility and metrics without adding external agents.

## 5) Privacy Defaults

- `turn_off_message_logging: true`

This prevents default persistence of prompt/response content in message logs, suitable for demo environments that should avoid storing user content.
