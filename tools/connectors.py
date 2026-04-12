"""
Tool Connectors
---------------
Export agent outputs to external tools.

Supported:
  - Notion (via Notion API)
  - Confluence (via REST API)
  - CSV / JSON (local file export — no API key needed)
  - Markdown files (always available)

Usage:
    from tools.connectors import NotionConnector, ConfluenceConnector, LocalExporter

    # Export to Notion
    notion = NotionConnector(api_key="secret_...", database_id="...")
    notion.export(deliverable)

    # Export to Confluence
    conf = ConfluenceConnector(base_url="https://mycompany.atlassian.net",
                               username="me@company.com", api_token="...")
    conf.export(deliverable, space_key="SPACE", parent_page_id="12345")

    # Local CSV/JSON (no API key)
    LocalExporter.to_csv(results, "outputs/mission_summary.csv")
    LocalExporter.to_json(results, "outputs/mission_summary.json")
"""

from __future__ import annotations
import csv
import json
import os
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.deliverable import Deliverable


# ── Local exporter (no API key needed) ──────────────────────────────────────

class LocalExporter:
    """Export outputs to local CSV and JSON files."""

    @staticmethod
    def to_json(results: dict[str, str], path: str):
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        payload = {
            "exported_at": datetime.utcnow().isoformat(),
            "sections": [
                {"title": k, "content": v, "length": len(v)}
                for k, v in results.items()
            ],
        }
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"✔ Exported JSON → {path}")

    @staticmethod
    def to_csv(results: dict[str, str], path: str):
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Section", "Length (chars)", "Preview (200 chars)"])
            for title, content in results.items():
                writer.writerow([title, len(content), content[:200].replace("\n", " ")])
        print(f"✔ Exported CSV → {path}")

    @staticmethod
    def deliverables_to_json(deliverables: list["Deliverable"], path: str):
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
        payload = {
            "exported_at": datetime.utcnow().isoformat(),
            "deliverables": [
                {
                    "agent": d.agent_name,
                    "milestone": d.milestone,
                    "title": d.title,
                    "type": d.doc_type.value,
                    "doc_id": d.doc_id,
                    "revision": d.revision,
                    "content": d.content,
                }
                for d in deliverables
            ],
        }
        with open(path, "w") as f:
            json.dump(payload, f, indent=2)
        print(f"✔ Exported {len(deliverables)} deliverables → {path}")


# ── Notion connector ─────────────────────────────────────────────────────────

class NotionConnector:
    """
    Export deliverables to a Notion database.

    Setup:
      1. Create a Notion integration at notion.so/my-integrations
      2. Share your database with the integration
      3. Get the database ID from the database URL

    Each deliverable becomes one page in the database with properties:
      Title, Agent, Milestone, Type, Doc ID, Revision, Date
    """

    def __init__(self, api_key: str, database_id: str):
        self.api_key = api_key
        self.database_id = database_id
        self.base_url = "https://api.notion.com/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28",
        }

    def _post(self, endpoint: str, payload: dict) -> dict:
        import urllib.request
        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{self.base_url}/{endpoint}",
            data=data,
            headers=self.headers,
            method="POST",
        )
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def _markdown_to_blocks(self, text: str) -> list[dict]:
        """Convert markdown text to Notion block objects (simplified)."""
        blocks = []
        for line in text.split("\n"):
            if line.startswith("# "):
                blocks.append({"object": "block", "type": "heading_1",
                                "heading_1": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}})
            elif line.startswith("## "):
                blocks.append({"object": "block", "type": "heading_2",
                                "heading_2": {"rich_text": [{"type": "text", "text": {"content": line[3:]}}]}})
            elif line.startswith("### "):
                blocks.append({"object": "block", "type": "heading_3",
                                "heading_3": {"rich_text": [{"type": "text", "text": {"content": line[4:]}}]}})
            elif line.startswith("- ") or line.startswith("* "):
                blocks.append({"object": "block", "type": "bulleted_list_item",
                                "bulleted_list_item": {"rich_text": [{"type": "text", "text": {"content": line[2:]}}]}})
            elif line.strip():
                # Split long paragraphs (Notion limit: 2000 chars per block)
                for chunk in [line[i:i+1900] for i in range(0, len(line), 1900)]:
                    blocks.append({"object": "block", "type": "paragraph",
                                   "paragraph": {"rich_text": [{"type": "text", "text": {"content": chunk}}]}})
        return blocks[:100]  # Notion API limit per request

    def export(self, deliverable: "Deliverable") -> str:
        """Export a single deliverable as a Notion page. Returns the page URL."""
        page_payload = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Name": {"title": [{"text": {"content": deliverable.title}}]},
                "Agent": {"rich_text": [{"text": {"content": deliverable.agent_name}}]},
                "Milestone": {"rich_text": [{"text": {"content": deliverable.milestone}}]},
                "Type": {"rich_text": [{"text": {"content": deliverable.doc_type.value}}]},
                "Doc ID": {"rich_text": [{"text": {"content": deliverable.doc_id or "TBD"}}]},
                "Revision": {"rich_text": [{"text": {"content": deliverable.revision}}]},
            },
            "children": self._markdown_to_blocks(deliverable.content),
        }
        result = self._post("pages", page_payload)
        url = result.get("url", "")
        print(f"✔ Notion page created: {deliverable.title} → {url}")
        return url

    def export_all(self, deliverables: list["Deliverable"]) -> list[str]:
        return [self.export(d) for d in deliverables]


# ── Confluence connector ──────────────────────────────────────────────────────

class ConfluenceConnector:
    """
    Export deliverables to Confluence.

    Setup:
      1. Generate an API token at id.atlassian.com/manage-profile/security/api-tokens
      2. Find your space key in Confluence space settings
      3. Find a parent page ID from the page URL (?pageId=XXXXX)
    """

    def __init__(self, base_url: str, username: str, api_token: str):
        import base64
        self.base_url = base_url.rstrip("/")
        credentials = base64.b64encode(f"{username}:{api_token}".encode()).decode()
        self.headers = {
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _request(self, method: str, endpoint: str, payload: dict | None = None) -> dict:
        import urllib.request
        url = f"{self.base_url}/wiki/rest/api/{endpoint}"
        data = json.dumps(payload).encode() if payload else None
        req = urllib.request.Request(url, data=data, headers=self.headers, method=method)
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())

    def _markdown_to_storage(self, text: str) -> str:
        """Convert markdown to Confluence storage format (simplified HTML)."""
        lines = []
        for line in text.split("\n"):
            if line.startswith("# "):
                lines.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith("## "):
                lines.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith("### "):
                lines.append(f"<h3>{line[4:]}</h3>")
            elif line.startswith("- ") or line.startswith("* "):
                lines.append(f"<li>{line[2:]}</li>")
            elif line.startswith("| "):
                lines.append(f"<p><code>{line}</code></p>")
            elif line.strip():
                lines.append(f"<p>{line}</p>")
        return "\n".join(lines)

    def export(self, deliverable: "Deliverable", space_key: str,
               parent_page_id: str | None = None) -> str:
        """Export a deliverable as a Confluence page. Returns the page URL."""
        payload: dict = {
            "type": "page",
            "title": deliverable.title,
            "space": {"key": space_key},
            "body": {
                "storage": {
                    "value": self._markdown_to_storage(deliverable.content),
                    "representation": "storage",
                }
            },
        }
        if parent_page_id:
            payload["ancestors"] = [{"id": parent_page_id}]

        result = self._request("POST", "content", payload)
        page_id = result.get("id", "")
        url = f"{self.base_url}/wiki/spaces/{space_key}/pages/{page_id}"
        print(f"✔ Confluence page created: {deliverable.title} → {url}")
        return url

    def export_all(self, deliverables: list["Deliverable"],
                   space_key: str, parent_page_id: str | None = None) -> list[str]:
        return [self.export(d, space_key, parent_page_id) for d in deliverables]
