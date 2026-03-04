# Remote MCP Providers

Remote MCP Providers allow you to connect Orchestrator to external MCP (Model Context Protocol) servers, aggregating their tools into your Orchestrator instance.

---

## Overview

With Remote MCP Providers, you can:

- Connect to any MCP server over HTTP/SSE
- Automatically discover and register remote tools
- Use remote tools alongside local core tools
- Aggregate tools from multiple MCP servers

This is different from Remote Providers (which provide inference endpoints). Remote MCP Providers provide **tools** that models can call.

---

## Adding an MCP Provider

### Via the UI

1. Open the Settings dialog (`Ctrl + ,`)
2. Navigate to the **Tools** or **Providers** tab
3. Enter the MCP server URL and configuration
4. Click **Save**

---

## Technical Details

### Tool Discovery

When you connect to an MCP provider:

1. Orchestrator establishes a connection to the MCP server
2. Discovers available tools
3. Registers each tool with a namespaced name
4. Tools become available for agent reasoning

### Tool Namespacing

To prevent naming conflicts, tools from remote MCP providers are typically prefixed:

```
provider_toolname
```

---

## Using Remote MCP Tools

### In Chat

Remote MCP tools work like any other tool. When a model decides to use a tool, Orchestrator handles the routing automatically. You can monitor tool calls in the **Activity Log** panel.

---

## Connection States

MCP Providers can be in the following states:

| State            | Indicator | Description                         |
| ---------------- | --------- | ----------------------------------- |
| **Connected**    | Green     | Active connection, tools discovered |
| **Connecting**   | Blue      | Establishing connection             |
| **Disconnected** | Gray      | Not connected                       |
| **Error**        | Red       | Connection or discovery failed      |

---

## Security

### Configuration Storage

Configuration is stored in the application's config directory:

```
~/.orchestrator_ai/config.json
```

---

## Related Documentation

- [Remote Providers](REMOTE_PROVIDERS.md) — Connect to inference APIs
- [FEATURES.md](FEATURES.md) — Feature inventory
- [README](../README.md) — Quick start guide
