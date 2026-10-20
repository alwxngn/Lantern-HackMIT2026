"""Skill 14 — return to a named home pose.

Reuses the exact same navigate+wait-for-arrival mechanism
``hackmitdog.aegis.locations``'s ``go_to_named_location`` uses (see
``DIMOS_SKILL_IMPLEMENTATION_PLAN.md`` §6 row 14, §8):

- ``ExtendedSpatialMemorySpec.find_robot_location``
  (``hackmitdog.aegis.spec_ext``, backed by DimOS's
  ``dimos.perception.experimental.spatial_perception.SpatialMemory``) to look
  up the named pose.
- ``NavigationInterfaceSpec.set_goal`` / ``cancel_goal``
  (``dimos.navigation.navigation_spec``) for the actual movement.

This DimOS install reports battery percentage
(``GO2Connection.get_battery_soc`` / ``battery_soc``) and has no
autonomous-docking or charge-initiation API. ``return_to_home`` stops at a
named pose and reports arrival. It does not claim that charging or docking
happened.

The arrival poll is local to this module, same pattern as
``navigation_skills.py`` and ``object_memory.py``.

No DimOS code is modified.
"""

from __future__ import annotations

import time

from dimos.agents.annotation import skill
from dimos.agents.capabilities import CAP_MOVEMENT
from dimos.agents.skill_result import SkillResult
from dimos.core.module import Module
from dimos.core.stream import In
from dimos.msgs.geometry_msgs.PoseStamped import PoseStamped
from dimos.msgs.geometry_msgs.Quaternion import Quaternion
from dimos.msgs.geometry_msgs.Vector3 import make_vector3
from dimos.msgs.tf2_msgs.TFMessage import TFMessage
from dimos.navigation.base import NavigationState
from dimos.navigation.navigation_spec import NavigationInterfaceSpec
from dimos.utils.logging_config import setup_logger

from hackmitdog.aegis.skill_errors import AegisError
from hackmitdog.aegis.spec_ext import ExtendedSpatialMemorySpec

logger = setup_logger()

_GOAL_POLL_INTERVAL_S = 0.1
_GOAL_SETTLE_S = 1.5
_DEFAULT_ARRIVAL_TIMEOUT_S = 60.0


def _wait_for_goal(
    navigation: NavigationInterfaceSpec, timeout_s: float
) -> tuple[str, float]:
    """Poll `navigation` until arrival, cancellation/failure, or timeout.

    Duplicated from ``locations.py``'s ``_wait_for_arrival`` /
    ``navigation_skills.py``'s ``_wait_for_goal`` (itself mirroring
    ``UnitreeSkillContainer._wait_for_goal``): the planner drops out of
    FOLLOWING_PATH for a moment on every replan, so a pause only counts as
    "done" once it has held for ``_GOAL_SETTLE_S``.
    """
    start = time.monotonic()
    deadline = start + timeout_s
    idle_since: float | None = None

    while time.monotonic() < deadline:
        if navigation.is_goal_reached():
            return "reached", time.monotonic() - start
        if navigation.get_state() == NavigationState.FOLLOWING_PATH:
            idle_since = None
        elif idle_since is None:
            idle_since = time.monotonic()
        elif time.monotonic() - idle_since > _GOAL_SETTLE_S:
            return "failed", time.monotonic() - start
        time.sleep(_GOAL_POLL_INTERVAL_S)

    return "timeout", time.monotonic() - start


class HomeSkills(Module):
    """Return to a named home pose."""

    _spatial_memory: ExtendedSpatialMemorySpec
    _navigation: NavigationInterfaceSpec

    tf: In[TFMessage]

    # Battery percentage is already its own DimOS tool
    # (GO2Connection.get_battery_soc). GO2ConnectionSpec does not declare
    # battery_soc, so this skill does not inject the connection to report it.

    @skill(uses=[CAP_MOVEMENT])
    def return_to_home(
        self, home_name: str = "home", timeout_s: float = _DEFAULT_ARRIVAL_TIMEOUT_S
    ) -> SkillResult[AegisError]:
        """Navigate to the named home location and wait to arrive.

        This only drives to a previously saved pose. It does not initiate
        charging or docking. On success this reports `outcome:
        "arrived_at_dock_pose"` — arrival at the pose, nothing more. Call
        `get_battery_soc` separately for battery level
        (`dimos.robot.unitree.go2.connection.GO2Connection`).

        Does not invent a default home pose: if `home_name` was never saved,
        this fails rather than guessing a position.

        Args:
            home_name: Name of the saved location to treat as home. Defaults
                to "home". Must have been saved earlier with
                `save_named_location`.
            timeout_s: Give up and report failure after this many seconds.

        Example:
            return_to_home()
            return_to_home("charging spot", timeout_s=90)
        """
        home_name = home_name.strip()
        if not home_name:
            return SkillResult.fail("INVALID_INPUT", "home_name must not be empty.")
        if timeout_s <= 0:
            return SkillResult.fail("INVALID_INPUT", "timeout_s must be positive.")

        try:
            location = self._spatial_memory.find_robot_location(home_name)
        except Exception as exc:
            logger.exception("return_to_home: lookup failed", home_name=home_name)
            return SkillResult.fail(
                "EXECUTION_FAILED", f"Could not look up '{home_name}': {exc}"
            )

        if location is None:
            return SkillResult.fail(
                "LOCATION_NOT_FOUND",
                f"No named location called '{home_name}'. Save one with "
                f"save_named_location('{home_name}') first.",
            )

        goal = PoseStamped(
            position=make_vector3(*location.position),
            orientation=Quaternion.from_euler(make_vector3(*location.rotation)),
            frame_id="map",
        )

        try:
            if not self._navigation.set_goal(goal):
                return SkillResult.fail(
                    "EXECUTION_FAILED", f"Planner rejected the goal for '{home_name}'."
                )

            outcome, elapsed_s = _wait_for_goal(self._navigation, timeout_s)
        except Exception as exc:
            logger.exception("return_to_home: navigation failed", home_name=home_name)
            return SkillResult.fail("EXECUTION_FAILED", f"Navigation failed: {exc}")

        if outcome == "reached":
            return SkillResult.ok(
                f"Arrived at '{home_name}'. Stopped at the pose only -- charging/docking "
                "was not initiated (no such API exists in this DimOS install).",
                name=home_name,
                elapsed_s=round(elapsed_s, 1),
                outcome="arrived_at_dock_pose",
            )
        if outcome == "timeout":
            return SkillResult.fail(
                "EXECUTION_TIMEOUT", f"Did not reach '{home_name}' within {timeout_s:.0f}s."
            )
        return SkillResult.fail(
            "EXECUTION_FAILED", f"Navigation to '{home_name}' was cancelled or failed."
        )

    @skill
    def stop_return_to_home(self) -> SkillResult[AegisError]:
        """Cancel an in-progress `return_to_home` call.

        Safe to call even if nothing is navigating.
        """
        self._navigation.cancel_goal()
        return SkillResult.ok("Navigation cancelled.")
