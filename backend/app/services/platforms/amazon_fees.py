"""Amazon India fee module.

Currently uses the standard data-driven algorithm from the base class — the
Amazon/Flipkart difference lives entirely in the ``fee_rules`` data, which is
the intended design (RG1/RG2). This class is the named seam where an
Amazon-specific quirk (e.g. a category referral-fee cap) would be overridden.
"""

from app.services.platforms.base import PlatformFeeModule


class AmazonFeeModule(PlatformFeeModule):
    name = "Amazon"
