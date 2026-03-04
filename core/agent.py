import json
import re
import os
from typing import Generator, List, Dict, Any, Optional
from .ollama_client import OllamaClient
from .tools import ToolExecutor
from .config import ConfigManager

class Agent:
    def __init__(self, workspace_manager, model: Optional[str] = None):
        self.config_manager = ConfigManager()
        self.ollama = OllamaClient(model)
        self.workspace_manager = workspace_manager
        self.tools = ToolExecutor(workspace_manager.get_root())
        self.history: List[Dict[str, str]] = []
        self.max_steps = 10

        # Load active agent configuration
        agent_conf = self.config_manager.get_active_agent()
        self.system_prompt = agent_conf.get("prompt", "")
        self.name = agent_conf.get("name", "Agent")

    def run(self, user_input: str) -> Generator[Dict[str, Any], None, None]:
        # Reload system prompt from config in case it changed
        agent_conf = self.config_manager.get_active_agent()
        self.system_prompt = agent_conf.get("prompt", "")
        self.name = agent_conf.get("name", "Agent")

        # Sync workspace path
        root = self.workspace_manager.get_root()
        if root:
            self.tools.workspace_path = os.path.abspath(os.path.expanduser(root))

        self.history.append({"role": "user", "content": user_input})

        # Inject dynamic context snapshot
        context = self.workspace_manager.get_context_snapshot()
        dynamic_system_prompt = self.system_prompt + "\n---\n" + context

        # Yield initial thinking state
        yield {"type": "thought", "content": "Consultando a Ollama..."}

        for step in range(self.max_steps):
            full_response = ""
            # Stream the agent's thought/action from Ollama
            for chunk in self.ollama.chat_stream(self.history, system=dynamic_system_prompt):
                full_response += chunk

            # Clean and repair JSON
            clean_json = self._extract_json(full_response)

            try:
                data = json.loads(clean_json, strict=False)
                thought = data.get("thought", "Thinking...")
                action = data.get("action")
                params = data.get("params", {})

                yield {"type": "thought", "content": thought}

                if not action or action == "finish":
                    yield {"type": "final", "content": params.get("content", full_response)}
                    self.history.append({"role": "assistant", "content": full_response})
                    return

                yield {"type": "action", "action": action, "params": params}

                # Execute tool
                observation = self._execute_tool(action, params)
                
                # Truncate observation to prevent context bloat
                if len(observation) > 2000:
                    observation = observation[:2000] + "\n... (output truncated for brevity) ..."
                
                yield {"type": "observation", "content": observation}

                # Add step to history
                self.history.append({"role": "assistant", "content": full_response})
                self.history.append({"role": "user", "content": f"Observation: {observation}"})

            except Exception as e:
                yield {"type": "error", "content": f"Failed to parse agent response: {str(e)}\nRaw: {full_response}"}
                return

        yield {"type": "error", "content": "Maximum reasoning steps reached."}

    # -------------------------------------------------------------------------
    # JSON extraction & repair
    # -------------------------------------------------------------------------

    def _strip_thinking_tags(self, text: str) -> str:
        """Remove Qwen3 / DeepSeek-R1 style <think>...</think> blocks."""
        # Complete blocks
        text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
        # Unclosed <think> that runs to end-of-string (streaming truncation)
        text = re.sub(r'<think>.*$', '', text, flags=re.DOTALL)
        return text.strip()

    def _balance_braces(self, json_str: str) -> str:
        """
        Balance unmatched { [ by appending the missing closers.
        Walks the string character-by-character, respecting quoted strings
        so braces inside string values are not counted.
        """
        in_string = False
        escape_next = False
        stack: List[str] = []
        pairs = {'}': '{', ']': '['}
        openers = set('{[')
        closers = set('}]')
        closer_map = {'{': '}', '[': ']'}

        for ch in json_str:
            if escape_next:
                escape_next = False
                continue
            if ch == '\\' and in_string:
                escape_next = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch in openers:
                stack.append(ch)
            elif ch in closers:
                if stack and stack[-1] == pairs[ch]:
                    stack.pop()
                # mismatched closer – leave as-is, json.loads will report it

        # Append missing closers in reverse insertion order
        return json_str + ''.join(closer_map[o] for o in reversed(stack))

    def _escape_literal_whitespace_in_strings(self, json_str: str) -> str:
        """
        Escape literal newlines, carriage returns and tabs that appear
        inside JSON string values (the model forgot to write \\n etc.).
        Characters outside strings are left untouched.
        """
        result = []
        in_string = False
        escape_next = False
        replacements = {'\n': '\\n', '\r': '\\r', '\t': '\\t'}

        for ch in json_str:
            if escape_next:
                escape_next = False
                result.append(ch)
                continue
            if ch == '\\' and in_string:
                escape_next = True
                result.append(ch)
                continue
            if ch == '"':
                in_string = not in_string
                result.append(ch)
                continue
            if in_string and ch in replacements:
                result.append(replacements[ch])
            else:
                result.append(ch)

        return ''.join(result)

    def _repair_json(self, json_str: str) -> str:
        """Apply heuristic repairs for the most common LLM JSON mistakes."""
        # 1. Trailing commas before } or ]
        json_str = re.sub(r',\s*([\]}])', r'\1', json_str)

        # 2. Python literals that sneak in
        json_str = re.sub(r'\bTrue\b', 'true', json_str)
        json_str = re.sub(r'\bFalse\b', 'false', json_str)
        json_str = re.sub(r'\bNone\b', 'null', json_str)

        # 3. Single-line // comments (invalid in JSON)
        #    Only strip outside of strings – simple heuristic: skip if inside quotes
        json_str = re.sub(r'(?m)(?<!:)(?<!https)(?<!http)//[^\n]*', '', json_str)

        # 4. Multi-line /* */ comments
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)

        # 5. Values accidentally left empty by comment removal
        json_str = re.sub(r':\s*,', ': null,', json_str)
        json_str = re.sub(r':\s*}', ': null}', json_str)

        # 6. Escape literal newlines/tabs inside JSON string values
        #    Walk char-by-char to only fix characters that are inside strings
        json_str = self._escape_literal_whitespace_in_strings(json_str)

        # 7. Balance unmatched braces / brackets
        json_str = self._balance_braces(json_str)

        return json_str.strip()

    def _find_outermost_object(self, text: str) -> Optional[str]:
        """
        Return the substring of *text* that spans the outermost JSON object
        { … }, properly handling nested braces and quoted strings.
        Returns None when no opening brace is found.
        """
        start = text.find('{')
        if start == -1:
            return None

        depth = 0
        in_string = False
        escape_next = False

        for i, ch in enumerate(text[start:], start):
            if escape_next:
                escape_next = False
                continue
            if ch == '\\' and in_string:
                escape_next = True
                continue
            if ch == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == '{':
                depth += 1
            elif ch == '}':
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]

        # Truncated object – take everything from the opening brace
        return text[start:]

    def _extract_json(self, text: str) -> str:
        """
        Robustly extract and repair a JSON object from an LLM response.

        Priority:
          1. Strip Qwen3 / DeepSeek <think>…</think> thinking blocks.
          2. Try ```json … ``` fenced blocks.
          3. Try any ``` … ``` fenced block whose content looks like JSON.
          4. Extract the outermost { … } from the remaining text.
          5. Fallback: wrap the entire response as a plain-text finish action
             so the caller always receives parseable JSON.
        """
        # Step 1 – remove thinking tags
        cleaned = self._strip_thinking_tags(text)

        # Step 2 & 3 – fenced code blocks
        for pattern in (
                r'```json\s*(.*?)\s*```',
                r'```(?:\w*\n)?\s*(.*?)\s*```',
        ):
            for match in re.finditer(pattern, cleaned, re.DOTALL):
                candidate = match.group(1).strip()
                if candidate.startswith('{'):
                    return self._repair_json(candidate)

        # Step 4 – outermost { … }
        candidate = self._find_outermost_object(cleaned)
        if candidate:
            return self._repair_json(candidate)

        # Step 5 – plain-text fallback: no JSON detected at all
        # json.dumps handles escaping of special characters, newlines, etc.
        escaped_content = json.dumps(cleaned)
        fallback = (
            '{"thought": "Responding with plain text.",'
            ' "action": "finish",'
            f' "params": {{"content": {escaped_content}}}}}'
        )
        return fallback

    # -------------------------------------------------------------------------
    # Tool dispatch
    # -------------------------------------------------------------------------

    def _execute_tool(self, action: str, params: Dict[str, Any]) -> str:
        if action == "create_file":
            return self.tools.create_file(params.get("path"), params.get("content", ""))
        elif action == "edit_file":
            return self.tools.edit_file(params.get("path"), params.get("old", ""), params.get("new", ""))
        elif action == "read_file":
            return self.tools.read_file(params.get("path"))
        elif action == "list_files" or action == "search_files":
            return self.tools.search_files(params.get("pattern", "*"))
        elif action == "get_system_info":
            return self.tools.get_system_info()
        elif action == "search_web":
            api_key = self.config_manager.config.get("brave_api_key", "")
            query = params.get("query") or params.get("q", "")
            return self.tools.search_web(query, api_key)
        else:
            return f"Unknown action: {action}"