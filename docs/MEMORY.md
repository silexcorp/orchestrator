# Orchestrator Memory System

The Python version of Orchestrator uses a simplified but effective memory system to provide long-term context.

## Memory Layers

### 1. User Profile (`user_profiles.json`)
Contains distilled summaries of who the user is and their general preferences as learned by each agent.

### 2. Working Memory (`memory_entries.json`)
Individual entries extracted from past conversations that contain specific facts or data.

## Technical Operation

### Extraction
When a conversation ends or reaches a save point, the agent analyzes the history and extracts new insights that are saved as a `MemoryEntry`.

### Search (BM25)
Unlike the macOS version which uses vector search (Embeddings), the current Linux version uses the **BM25** keyword search algorithm.

When you ask a question, Orchestrator:
1. Tokenizes your query.
2. Searches the memory database for entries with the highest matching terms.
3. Injects the most relevant results into the agent's system prompt.

## Data Management
You can view and manage accumulated memory from the **Memory** tab in the application's management window.
