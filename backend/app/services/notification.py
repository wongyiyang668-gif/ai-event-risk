import os
import requests
import json
from datetime import datetime

class NotificationService:
    """
    Service for sending high-risk alerts to external platforms via Webhooks.
    """
    def __init__(self):
        self.webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    def send_risk_alert(self, event_id: str, content: str, source: str, risk_summary: str, recommendation: str, risk_score: float):
        """
        Send a formatted Discord Embed alert for high-risk events.
        """
        if not self.webhook_url:
            print("Warning: DISCORD_WEBHOOK_URL not set. Skipping alert.")
            return

        # Determine color based on score (High: Red, Moderate: Orange)
        color = 0xff0000 if risk_score >= 0.6 else 0xffa500

        payload = {
            "embeds": [
                {
                    "title": "🚨 High Risk Event Detected",
                    "description": risk_summary,
                    "color": color,
                    "fields": [
                        {"name": "Event ID", "value": f"`{event_id}`", "inline": True},
                        {"name": "Source", "value": source.capitalize(), "inline": True},
                        {"name": "Risk Score", "value": f"{risk_score:.2f}", "inline": True},
                        {"name": "Actionable Recommendation", "value": recommendation}
                    ],
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {"text": "AI Risk Scoring System"}
                }
            ]
        }

        try:
            response = requests.post(self.webhook_url, json=payload, timeout=5)
            response.raise_for_status()
        except Exception as e:
            print(f"Error sending Discord alert: {e}")

# Singleton instance
notification_service = NotificationService()
