"""Map simulation animation types to frontend visualization payloads."""

from __future__ import annotations

from typing import Any

ANIMATION_MAPPING: dict[str, dict[str, Any]] = {
    "bubbles": {
        "animation_asset": "bubbles.json",
        "color_overlay": None,
        "intensity": "medium",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
    "bubbles_with_heat": {
        "animation_asset": "bubbles.json",
        "color_overlay": None,
        "intensity": "high",
        "show_thermometer": True,
        "thermometer_direction": "up",
    },
    "fire": {
        "animation_asset": "fire.json",
        "color_overlay": None,
        "intensity": "high",
        "show_thermometer": True,
        "thermometer_direction": "up",
    },
    "color_change_blue": {
        "animation_asset": "color_change.json",
        "color_overlay": "#2563EB",
        "intensity": "medium",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
    "color_change_red": {
        "animation_asset": "color_change.json",
        "color_overlay": "#DC2626",
        "intensity": "medium",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
    "precipitate_white": {
        "animation_asset": "precipitate.json",
        "color_overlay": "#F8FAFC",
        "intensity": "medium",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
    "precipitate_yellow": {
        "animation_asset": "precipitate.json",
        "color_overlay": "#FACC15",
        "intensity": "medium",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
    "smoke": {
        "animation_asset": "smoke.json",
        "color_overlay": None,
        "intensity": "medium",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
    "dissolve": {
        "animation_asset": "dissolve.json",
        "color_overlay": None,
        "intensity": "low",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
    "no_reaction": {
        "animation_asset": "no_reaction.json",
        "color_overlay": None,
        "intensity": "low",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
    "bright_flame": {
        "animation_asset": "fire.json",
        "color_overlay": "#FB923C",
        "intensity": "high",
        "show_thermometer": True,
        "thermometer_direction": "up",
    },
    "brisk_bubbles": {
        "animation_asset": "bubbles.json",
        "color_overlay": None,
        "intensity": "high",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
    "catalytic_bubbles": {
        "animation_asset": "bubbles.json",
        "color_overlay": None,
        "intensity": "medium",
        "show_thermometer": True,
        "thermometer_direction": "up",
    },
    "crystal_deposition": {
        "animation_asset": "precipitate.json",
        "color_overlay": "#D1D5DB",
        "intensity": "low",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
    "dense_precipitate": {
        "animation_asset": "precipitate.json",
        "color_overlay": "#E5E7EB",
        "intensity": "high",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
    "flame_with_condensation": {
        "animation_asset": "fire.json",
        "color_overlay": "#93C5FD",
        "intensity": "high",
        "show_thermometer": True,
        "thermometer_direction": "up",
    },
    "glow_combustion": {
        "animation_asset": "fire.json",
        "color_overlay": "#F59E0B",
        "intensity": "medium",
        "show_thermometer": True,
        "thermometer_direction": "up",
    },
    "heat_only": {
        "animation_asset": "explosion_safe.json",
        "color_overlay": None,
        "intensity": "medium",
        "show_thermometer": True,
        "thermometer_direction": "up",
    },
    "heating_with_fumes": {
        "animation_asset": "smoke.json",
        "color_overlay": None,
        "intensity": "medium",
        "show_thermometer": True,
        "thermometer_direction": "up",
    },
    "indicator_color_shift": {
        "animation_asset": "color_change.json",
        "color_overlay": "#A855F7",
        "intensity": "medium",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
    "metal_deposition": {
        "animation_asset": "precipitate.json",
        "color_overlay": "#B45309",
        "intensity": "medium",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
    "ph_color_spectrum": {
        "animation_asset": "color_change.json",
        "color_overlay": "#22C55E",
        "intensity": "medium",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
    "precipitate_cloud": {
        "animation_asset": "precipitate.json",
        "color_overlay": "#F8FAFC",
        "intensity": "medium",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
    "reactive_bubbles": {
        "animation_asset": "bubbles.json",
        "color_overlay": None,
        "intensity": "high",
        "show_thermometer": True,
        "thermometer_direction": "up",
    },
    "slow_bubbles": {
        "animation_asset": "bubbles.json",
        "color_overlay": None,
        "intensity": "low",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
    "steady_flame": {
        "animation_asset": "fire.json",
        "color_overlay": None,
        "intensity": "medium",
        "show_thermometer": True,
        "thermometer_direction": "up",
    },
    "steam_with_heat": {
        "animation_asset": "smoke.json",
        "color_overlay": "#E2E8F0",
        "intensity": "medium",
        "show_thermometer": True,
        "thermometer_direction": "up",
    },
    "surface_blackening": {
        "animation_asset": "smoke.json",
        "color_overlay": "#1F2937",
        "intensity": "low",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
    "vigorous_bubbles": {
        "animation_asset": "bubbles.json",
        "color_overlay": None,
        "intensity": "high",
        "show_thermometer": True,
        "thermometer_direction": "up",
    },
    "white_fumes": {
        "animation_asset": "smoke.json",
        "color_overlay": "#F8FAFC",
        "intensity": "medium",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
    "yellow_precipitate": {
        "animation_asset": "precipitate.json",
        "color_overlay": "#FDE047",
        "intensity": "high",
        "show_thermometer": False,
        "thermometer_direction": None,
    },
}

DEFAULT_VISUALIZATION = {
    "animation_asset": "no_reaction.json",
    "color_overlay": None,
    "intensity": "low",
    "show_thermometer": False,
    "thermometer_direction": None,
}


def get_visualization(simulation_result: dict[str, Any]) -> dict[str, Any]:
    """Return frontend visualization payload for a simulation result."""
    animation_type = simulation_result.get("animation_type", "no_reaction")
    return ANIMATION_MAPPING.get(animation_type, DEFAULT_VISUALIZATION)
