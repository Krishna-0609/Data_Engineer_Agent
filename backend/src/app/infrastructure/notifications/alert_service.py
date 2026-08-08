"""
Infrastructure — Real-Time Alerting & Notification Engine

Sends Slack Webhook alerts and Email notifications on pipeline completion,
execution failure, or data quality rule breach.
"""

from __future__ import annotations

from typing import Any
import httpx
import structlog

logger = structlog.get_logger()


class AlertService:
    """
    Service for sending incident notifications to Slack webhooks and email recipients.
    """

    def __init__(self, default_slack_webhook: str | None = None) -> None:
        self._default_slack_webhook = default_slack_webhook

    async def send_slack_alert(
        self,
        pipeline_name: str,
        status: str,
        details: str,
        rows_processed: int = 0,
        execution_id: str | None = None,
        webhook_url: str | None = None,
    ) -> bool:
        target_url = webhook_url or self._default_slack_webhook
        if not target_url:
            logger.info("slack_alert.skipped_no_url", pipeline_name=pipeline_name)
            return False

        color = "#10B981" if status.lower() == "success" else "#EF4444"
        icon = "✅" if status.lower() == "success" else "🚨"

        payload = {
          "attachments": [
            {
              "color": color,
              "blocks": [
                {
                  "type": "header",
                  "text": {
                    "type": "plain_text",
                    "text": f"{icon} AI Data Pipeline Alert: {pipeline_name}",
                    "emoji": True
                  }
                },
                {
                  "type": "section",
                  "fields": [
                    {"type": "mrkdwn", "text": f"*Status:*\n`{status.upper()}`"},
                    {"type": "mrkdwn", "text": f"*Rows Processed:*\n`{rows_processed}`"},
                    {"type": "mrkdwn", "text": f"*Execution ID:*\n`{execution_id or 'N/A'}`"},
                    {"type": "mrkdwn", "text": f"*Environment:*\n`Production`"}
                  ]
                },
                {
                  "type": "section",
                  "text": {
                    "type": "mrkdwn",
                    "text": f"*Summary & Logs:*\n```{details[:500]}```"
                  }
                }
              ]
            }
          ]
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.post(target_url, json=payload)
                if resp.status_code == 200:
                    logger.info("slack_alert.sent", pipeline_name=pipeline_name)
                    return True
                else:
                    logger.error("slack_alert.failed", status_code=resp.status_code, body=resp.text)
                    return False
        except Exception as exc:
            logger.error("slack_alert.exception", error=str(exc))
            return False

    async def send_email_alert(
        self, recipient: str, subject: str, body: str
    ) -> bool:
        """Simulated SMTP/SES email dispatch."""
        logger.info("email_alert.dispatched", recipient=recipient, subject=subject)
        return True
