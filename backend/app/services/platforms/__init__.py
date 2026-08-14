"""Platform fee module registry.

A platform is priced by its specialised module if one is registered, otherwise
by the shared ``DefaultFeeModule``. So adding a platform requires only seed
rows — never a code change here — while a platform with a genuine quirk can
still register a dedicated module. Business logic never hardcodes platform
names; it looks them up.
"""

from app.services.platforms.amazon_fees import AmazonFeeModule
from app.services.platforms.base import FeeBreakdown, FeeRuleLike, PlatformFeeModule
from app.services.platforms.flipkart_fees import FlipkartFeeModule
from app.services.platforms.generic_fees import DefaultFeeModule

# Only platforms needing platform-specific computation get an entry here.
_SPECIFIC: dict[str, PlatformFeeModule] = {
    module.name: module
    for module in (AmazonFeeModule(), FlipkartFeeModule())
}
_DEFAULT = DefaultFeeModule()


def get_fee_module(platform_name: str) -> PlatformFeeModule:
    """Return the fee module for a platform — specialised, else the default."""
    return _SPECIFIC.get(platform_name, _DEFAULT)


def has_specific_module(platform_name: str) -> bool:
    return platform_name in _SPECIFIC


def registered_platforms() -> list[str]:
    """Names of platforms with a *specialised* module (not the whole catalogue)."""
    return sorted(_SPECIFIC)


__all__ = [
    "PlatformFeeModule",
    "FeeBreakdown",
    "FeeRuleLike",
    "AmazonFeeModule",
    "FlipkartFeeModule",
    "DefaultFeeModule",
    "get_fee_module",
    "has_specific_module",
    "registered_platforms",
]
