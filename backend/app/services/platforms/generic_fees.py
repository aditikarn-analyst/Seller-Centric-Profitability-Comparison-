"""Default fee module used for any platform without a specialised one.

Because all fee inputs come from the ``fee_rules`` data, the standard base-class
algorithm prices every marketplace correctly. New platforms therefore need no
code — only seed rows. A platform earns a dedicated subclass only if it has a
genuine computation the shared algorithm cannot express from the rule fields.
"""

from app.services.platforms.base import PlatformFeeModule


class DefaultFeeModule(PlatformFeeModule):
    name = "__default__"
