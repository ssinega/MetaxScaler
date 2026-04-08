"""
Hardcoded support ticket dataset for AI Customer Support Triage.
Contains 30 realistic tickets with categories, priorities, and actions.
"""

from __future__ import annotations

TICKETS: list[dict] = [
    {
        "id": "ticket_001",
        "query": "Payment failed but money deducted from my credit card.",
        "category": "billing",
        "priority": "high",
        "action": "refund"
    },
    {
        "id": "ticket_002",
        "query": "My account is locked and I cannot reset my password through the portal.",
        "category": "account",
        "priority": "high",
        "action": "escalate"
    },
    {
        "id": "ticket_003",
        "query": "How do I export my team's analytics data to a CSV file?",
        "category": "technical",
        "priority": "low",
        "action": "guide"
    },
    {
        "id": "ticket_004",
        "query": "I want to cancel my annual subscription and get a prorated refund for the remaining 6 months.",
        "category": "billing",
        "priority": "medium",
        "action": "refund"
    },
    {
        "id": "ticket_005",
        "query": "The production API is returning 500 errors for all POST requests to the /orders endpoint.",
        "category": "technical",
        "priority": "high",
        "action": "escalate"
    },
    {
        "id": "ticket_006",
        "query": "I was charged twice for last month's pro tier and need one payment reversed immediately.",
        "category": "billing",
        "priority": "high",
        "action": "refund"
    },
    {
        "id": "ticket_007",
        "query": "We need to add a second administrator to our workspace but the settings page doesn't show the option.",
        "category": "account",
        "priority": "medium",
        "action": "guide"
    },
    {
        "id": "ticket_008",
        "query": "SSO login is failing with an invalid SAML assertion for all our employees since this morning.",
        "category": "technical",
        "priority": "high",
        "action": "escalate"
    },
    {
        "id": "ticket_009",
        "query": "Please downgrade our workspace to the free tier starting from the next billing cycle.",
        "category": "billing",
        "priority": "medium",
        "action": "guide"
    },
    {
        "id": "ticket_010",
        "query": "Our finance team needs historical VAT invoices for Q1; where can I download these?",
        "category": "billing",
        "priority": "low",
        "action": "guide"
    },
    {
        "id": "ticket_011",
        "query": "I cannot delete a deactivated employee account and they still show up in our permissions list.",
        "category": "account",
        "priority": "medium",
        "action": "escalate"
    },
    {
        "id": "ticket_012",
        "query": "Webhook deliveries are timing out and orders are not syncing correctly to our external ERP.",
        "category": "technical",
        "priority": "high",
        "action": "escalate"
    },
    {
        "id": "ticket_013",
        "query": "After updating payment details, our users also cannot sign in through SSO and invoices are missing.",
        "category": "technical",
        "priority": "high",
        "action": "escalate"
    },
    {
        "id": "ticket_014",
        "query": "We got a duplicate charge and now the owner account is locked out after too many reset attempts.",
        "category": "account",
        "priority": "high",
        "action": "escalate"
    },
    {
        "id": "ticket_015",
        "query": "Need immediate invoice correction; meanwhile data export button disappeared after the release.",
        "category": "technical",
        "priority": "high",
        "action": "escalate"
    },
    {
        "id": "ticket_016",
        "query": "Please cancel subscription at renewal, but right now payroll sync is failing and staff cannot clock in.",
        "category": "technical",
        "priority": "high",
        "action": "escalate"
    },
    {
        "id": "ticket_017",
        "query": "We were invoiced for 50 seats but only use 30, and our API rate limits are also being hit unexpectedly.",
        "category": "technical",
        "priority": "high",
        "action": "escalate"
    },
    {
        "id": "ticket_018",
        "query": "How do I set up organization-wide multi-factor authentication for all my team members?",
        "category": "account",
        "priority": "medium",
        "action": "guide"
    },
    {
        "id": "ticket_019",
        "query": "Our enterprise contract renewal failed and now we can't access our compliance reports.",
        "category": "billing",
        "priority": "high",
        "action": "escalate"
    },
    {
        "id": "ticket_020",
        "query": "Can you provide a step-by-step guide on integrating our dashboard with Slack alerts?",
        "category": "technical",
        "priority": "low",
        "action": "guide"
    },
    {
        "id": "ticket_021",
        "query": "Refund the annual plan \u2014 we paid for a year but are cancelling within the 30-day money-back period.",
        "category": "billing",
        "priority": "high",
        "action": "refund"
    },
    {
        "id": "ticket_022",
        "query": "A new hire hasn't received their invite email despite IT whitelisting your domain.",
        "category": "account",
        "priority": "medium",
        "action": "escalate"
    },
    {
        "id": "ticket_023",
        "query": "How do I configure SSO with Google Workspace for our organization?",
        "category": "technical",
        "priority": "medium",
        "action": "guide"
    },
    {
        "id": "ticket_024",
        "query": "My credit card was charged for the premium tier even though I downgraded to free last week.",
        "category": "billing",
        "priority": "high",
        "action": "refund"
    },
    {
        "id": "ticket_025",
        "query": "I need to transfer the primary ownership of my account to another administrative user.",
        "category": "account",
        "priority": "low",
        "action": "guide"
    },
    {
        "id": "ticket_026",
        "query": "Our dashboard is showing a blank screen for all users; this is critical and blocking our work.",
        "category": "technical",
        "priority": "high",
        "action": "escalate"
    },
    {
        "id": "ticket_027",
        "query": "How can I apply for a nonprofit discount for our organization?",
        "category": "billing",
        "priority": "low",
        "action": "guide"
    },
    {
        "id": "ticket_028",
        "query": "We received a refund but now the account is restricted and payment is still marked as pending.",
        "category": "account",
        "priority": "high",
        "action": "escalate"
    },
    {
        "id": "ticket_029",
        "query": "How do I archive projects that are no longer active?",
        "category": "technical",
        "priority": "low",
        "action": "guide"
    },
    {
        "id": "ticket_030",
        "query": "Our usage-based billing seems incorrect compared to the active user count in our settings.",
        "category": "billing",
        "priority": "medium",
        "action": "escalate"
    }
]
