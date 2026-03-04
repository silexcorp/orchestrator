# Skills

Skills are packages of instructions and context that provide the agent with specialized expertise.

---

## Using Skills

1. Open the management window (**Ctrl + Shift + M**) → **Skills** tab.
2. You will see the available skills in your local folder.
3. You can import new skills by clicking the **Import...** button and selecting a Markdown file.

### File Location
Skills are saved as `.md` files in:
`~/.config/orchestrator/skills/`

---

## Creating Skills

You can create your own skills by writing a Markdown file with the following suggested format:

```markdown
# [Skill Name]

You are an expert in [specific field]. 

## Methodology
1. Identify the problem.
2. Apply [specific technique].
3. Format the response as [desired format].
```

Once saved in the `skills/` folder, it will automatically appear in Orchestrator.

---

## Smart Capability Selection

To save tokens, Orchestrator does not send all instructions for all skills in every message. It only loads the full content of the skills that the agent determines are necessary for the current task based on the initial context.
