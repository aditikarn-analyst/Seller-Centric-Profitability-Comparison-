"""Platform fee module registry.

The orchestrator looks modules up by platform name, so registering a new
marketplace here (plus seeding its rows) is the only code change adding a
platform requires.
"""

from app.services.platforms.amazon_fees import AmazonFeeModule
from app.services.platforms.base import FeeBreakdown, FeeRuleLike, PlatformFeeModule
from app.services.platforms.flipkart_fees import FlipkartFeeModule

_REGISTRY: dict[str, PlatformFeeModule] = {
    module.name: module
    for module in (AmazonFeeModule(), FlipkartFeeModule())
}


def get_fee_module(platform_name: str) -> PlatformFeeModule:
    """Return the fee module for a platform name, or raise if unregistered."""
    try:
        return _REGISTRY[platform_name]
    except KeyError as exc:
        raise KeyError(
            f"No fee module registered for platform '{platform_name}'. "
            f"Registered: {sorted(_REGISTRY)}"
        ) from exc


def registered_platforms() -> list[str]:
    return sorted(_REGISTRY)


__all__ = [
    "PlatformFeeModule",
    "FeeBreakdown",
    "FeeRuleLike",
    "AmazonFeeModule",
    "FlipkartFeeModule",
    "get_fee_module",
    "registered_platforms",
]
