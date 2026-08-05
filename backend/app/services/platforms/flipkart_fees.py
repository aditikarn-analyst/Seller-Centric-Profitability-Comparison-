"""Flipkart fee module.

As with Amazon, the standard base-class algorithm applies; Flipkart's different
economics come from its ``fee_rules`` rows, not from divergent code. Override
hooks here if Flipkart introduces a computation the shared algorithm cannot
express from the rule fields alone.
"""

from app.services.platforms.base import PlatformFeeModule


class FlipkartFeeModule(PlatformFeeModule):
    name = "Flipkart"
