# Remote Providers

Remote Providers allow you to connect Orchestrator to external APIs (OpenAI, Anthropic, OpenRouter, and compatible endpoints), giving you access to cloud models alongside your local Ollama models.

---

## Overview

With Remote Providers, you can:

- Access cloud models (ChatGPT, Claude via OpenRouter, etc.) through Orchestrator
- Use multiple inference backends simultaneously
- Switch between local and remote models seamlessly
- Keep API keys stored securely in your local configuration

---

## Adding a Provider

### Via the UI

1. Open the Settings dialog (`Ctrl + ,`) or Management window (`Ctrl + Shift + M`)
2. Navigate to the **Models** or **Providers** tab
3. Configure the connection settings for your chosen provider
4. Click **Save**

### Provider Presets

Orchestrator includes configurations for common providers:

| Preset         | Host              | Port | Base Path | API Format | Auth             |
| -------------- | ----------------- | ---- | --------- | ---------- | ---------------- |
| **Anthropic**  | api.anthropic.com | 443  | /v1       | Anthropic  | API Key required |
| **OpenAI**     | api.openai.com    | 443  | /v1       | OpenAI     | API Key required |
| **xAI**        | api.x.ai          | 443  | /v1       | OpenAI     | API Key required |
| **OpenRouter** | openrouter.ai     | 443  | /api/v1   | OpenAI     | API Key required |
| **Custom**     | (you specify)     | —    | /v1       | OpenAI     | Optional         |

**Note:** For local endpoints like LM Studio, use the **Custom** preset and configure the host/port manually.

---

## Configuration Options

### Basic Settings

| Setting       | Description                                     |
| ------------- | ----------------------------------------------- |
| **Name**      | Display name for the provider                   |
| **Host**      | Hostname or IP address (e.g., `api.openai.com`) |
| **Protocol**  | HTTP or HTTPS                                   |
| **Port**      | Server port (optional, uses protocol default)   |
| **Base Path** | API path prefix (usually `/v1`)                 |

### Authentication

| Setting       | Description                                  |
| ------------- | -------------------------------------------- |
| **Auth Type** | None or API Key                              |
| **API Key**   | Your provider's API key (stored in config)   |

---

## Using Remote Models

Once a provider is connected, its models appear alongside local models:

### In the Chat UI

- Click the model selector in the main toolbar
- Remote models are listed following the local Ollama models
- Select a model to start chatting

---

## Security

### API Key Storage

In this version, API keys are stored in the application's configuration file:

```
~/.orchestrator_ai/config.json
```

Ensure this directory has restricted permissions to protect your credentials.

---

## Related Documentation

- [Orchestrator API Guide](OpenAI_API_GUIDE.md) — API usage and SDK examples
- [FEATURES.md](FEATURES.md) — Feature inventory
- [README](../README.md) — Quick start guide
