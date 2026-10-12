"""
chatops.slack — Slack Bolt bot integration for InfraBuddy.
"""

from chatops.slack.bot import create_slack_app, start_socket_mode

__all__ = ["create_slack_app", "start_socket_mode"]
