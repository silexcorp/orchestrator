"""
work_engine.py — Orchestrator for agentic workflows (Work Mode).
Simplified version of WorkMode functionality from Swift.
"""
from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Callable

from core.chat_engine import ChatEngine
from models.agent import Agent

@dataclass
class WorkStep:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    status: str = "pending"  # pending, running, completed, failed
    output: str = ""

@dataclass
class WorkPlan:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    goal: str = ""
    steps: List[WorkStep] = field(default_factory=list)
    status: str = "pending"

class WorkEngine:
    """
    Executes a multi-step plan using an AI agent.
    """

    def __init__(self, chat_engine: ChatEngine):
        self.chat_engine = chat_engine
        self._active_plans: Dict[str, WorkPlan] = {}
        self._lock = threading.Lock()

    def create_plan(self, goal: str, agent: Agent) -> WorkPlan:
        """Use the agent to break down the goal into steps."""
        # This would normally be an LLM call to get a JSON list of steps.
        # For this prototype, we'll create a single step.
        plan = WorkPlan(goal=goal)
        plan.steps.append(WorkStep(description=f"Analyze and fulfill: {goal}"))
        
        with self._lock:
            self._active_plans[plan.id] = plan
        return plan

    def execute_plan(
        self, 
        plan_id: str, 
        agent: Agent,
        on_step_update: Callable[[WorkPlan, WorkStep], None],
        on_complete: Callable[[WorkPlan], None]
    ) -> None:
        """Run the steps of the plan one by one."""
        with self._lock:
            plan = self._active_plans.get(plan_id)
        
        if not plan:
            return

        def _run():
            plan.status = "running"
            for step in plan.steps:
                step.status = "running"
                on_step_update(plan, step)
                
                # Execute step (LLM call via ChatEngine)
                # In a real implementation, this would use tool calling outputs
                # For now, we simulate a response
                step.status = "completed"
                step.output = f"Executed step: {step.description}"
                on_step_update(plan, step)
            
            plan.status = "completed"
            on_complete(plan)

        threading.Thread(target=_run, daemon=True).start()


# Injected into the main app context
