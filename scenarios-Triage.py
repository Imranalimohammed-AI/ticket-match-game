# ── Scenario bank ──────────────────────────────────────────────────────────────
ALL_SCENARIOS: list[dict] = [
    # Incidents — unplanned disruptions needing emergency response
    {"s": "🖥️  My laptop won't power on at all",                                         "t": "Incident"},
    {"s": "🌐  GlobalProtect VPN shows 'Gateway not responding' — can't connect",        "t": "Incident"},
    {"s": "📧  Outlook keeps crashing immediately on launch this morning",               "t": "Incident"},
    {"s": "📧  All Outlook emails stuck in Outbox — cannot send or receive",             "t": "Incident"},
    {"s": "🔑  Okta MFA is not working — locked out of all SSO applications",           "t": "Incident"},
    {"s": "🔌  Shared network drive disappeared suddenly for the whole team",            "t": "Incident"},
    {"s": "💥  Database errors are blocking all staff transactions",                     "t": "Incident"},
    {"s": "❌  Critical error in Epic is blocking patient charting",                     "t": "Incident"},
    {"s": "🌐  GlobalProtect VPN disconnects every few minutes — can't stay connected", "t": "Incident"},
    {"s": "📧  Outlook calendar not syncing — meetings missing since yesterday",        "t": "Incident"},
    {"s": "🔓  Okta dashboard down — can't access any applications",                    "t": "Incident"},
    {"s": "📡  Internet completely down across Building B",                              "t": "Incident"},
    # Generic Service Requests — info, advice, or items NOT in the Service Catalog
    {"s": "🗝️   Need access to an internal app that is NOT listed in the portal",        "t": "Generic Service Request"},
    {"s": "👥  Add a new colleague to our existing AD security group",                   "t": "Generic Service Request"},
    {"s": "❓  Need IT advice on best practices for shared file storage",                "t": "Generic Service Request"},
    {"s": "🔑  Access to a shared mailbox — not available in the Service Catalog",      "t": "Generic Service Request"},
    {"s": "🖇️   Build a custom report inside an existing internal system",               "t": "Generic Service Request"},
    {"s": "💬  Guidance on the process for submitting a vendor invoice to Finance",     "t": "Generic Service Request"},
    # Service Catalog — standard portal items with auto-approval workflows
    {"s": "💻  Order a new laptop for a hire starting next week (via portal)",          "t": "Service Catalog (Fulfillment Task)"},
    {"s": "💿  Request Adobe Acrobat Pro installation via the Service Desk Portal",     "t": "Service Catalog (Fulfillment Task)"},
    {"s": "📦  Add a second monitor — available in the hardware catalog",               "t": "Service Catalog (Fulfillment Task)"},
    {"s": "🔐  Request Audit Access for a compliance review (via portal)",              "t": "Service Catalog (Fulfillment Task)"},
    {"s": "📱  Provision a company mobile phone for a field employee",                  "t": "Service Catalog (Fulfillment Task)"},
    {"s": "🏢  Facilities request for an ergonomic office chair (Service Portal)",      "t": "Service Catalog (Fulfillment Task)"},
    {"s": "🔧  Request a software upgrade for an existing licensed application",        "t": "Service Catalog (Fulfillment Task)"},
    {"s": "💿  Request Zoom license via the Cotiviti Service Desk Portal",              "t": "Service Catalog (Fulfillment Task)"},
    {"s": "🖨️   Add a network printer via the Cotiviti Service Portal",                 "t": "Service Catalog (Fulfillment Task)"},
]
