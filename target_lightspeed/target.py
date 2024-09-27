"""Lightspeed target class."""

from __future__ import annotations

from singer_sdk import typing as th
from target_hotglue.target import TargetHotglue

from target_lightspeed.sinks import (
    UpdateInventorySink,
)


class TargetLightspeed(TargetHotglue):
    """Sample target for Lightspeed."""

    name = "target-lightspeed"

    SINK_TYPES = [UpdateInventorySink]
    MAX_PARALLELISM = 1

    config_jsonschema = th.PropertiesList(
        th.Property(
            "base_url",
            th.StringType,
            required=True,
        ),
        th.Property(
            "language",
            th.StringType,
            required=True,
        ),
        th.Property("api_key", th.StringType, required=True),
        th.Property("api_secret", th.StringType, required=True),
    ).to_dict()


if __name__ == "__main__":
    TargetLightspeed.cli()
