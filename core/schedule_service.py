"""
schedule_service.py — Task scheduling for Agents.
Uses apscheduler to trigger agent prompts on a schedule (cron or interval).
"""
from __future__ import annotations

import logging
import threading
from datetime import datetime
from typing import Optional, Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from models.schedule import Schedule


class ScheduleService:
    """
    Manages background tasks that trigger AI agents based on time.
    """

    def __init__(self):
        self._scheduler = BackgroundScheduler()
        self._scheduler.start()
        self._jobs: dict[str, str] = {}  # schedule_id -> job_id
        self._lock = threading.Lock()

    def add_schedule(self, schedule: Schedule, callback: Callable[[Schedule], None]) -> bool:
        """Add and start a schedule."""
        if not schedule.enabled:
            return False

        with self._lock:
            self.remove_schedule(schedule.id)

            trigger = None
            if schedule.frequency == "interval":
                # Assuming internal stored as minutes for simplified Python version
                trigger = IntervalTrigger(minutes=60) # Placeholder
            elif schedule.frequency == "cron":
                try:
                    trigger = CronTrigger.from_crontab(schedule.cron_expression)
                except Exception:
                    return False
            
            if not trigger:
                return False

            job = self._scheduler.add_job(
                func=callback,
                trigger=trigger,
                args=[schedule],
                id=schedule.id,
                replace_existing=True
            )
            self._jobs[schedule.id] = job.id
            return True

    def remove_schedule(self, schedule_id: str) -> None:
        """Stop and remove a schedule."""
        with self._lock:
            if schedule_id in self._jobs:
                try:
                    self._scheduler.remove_job(schedule_id)
                except Exception:
                    pass
                self._jobs.pop(schedule_id)

    def shutdown(self) -> None:
        self._scheduler.shutdown()


# Shared singleton
schedule_service = ScheduleService()
