"""FUNBREW PDF API client for Python."""

from __future__ import annotations

from typing import Any

import requests


class FunbrewError(Exception):
    """FUNBREW PDF API error."""

    def __init__(self, message: str, status_code: int = 0):
        super().__init__(message)
        self.status_code = status_code


class FunbrewPdf:
    """FUNBREW PDF API client.

    Args:
        api_key: Your API key (sk-...)
        base_url: API base URL (default: https://pdf.funbrew.tech)
    """

    def __init__(self, api_key: str, base_url: str = "https://pdf.funbrew.tech"):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )
        self.session.timeout = 60

    def from_html(self, html: str, **options: Any) -> dict:
        """Generate PDF from HTML content."""
        return self._post("/api/pdf/generate-from-html", {"html": html, **options})

    def from_url(self, url: str, **options: Any) -> dict:
        """Generate PDF from URL."""
        return self._post("/api/pdf/generate-from-url", {"url": url, **options})

    def from_template(
        self, slug: str, variables: dict | None = None, **options: Any
    ) -> dict:
        """Generate PDF from template."""
        return self._post(
            "/api/pdf/generate-from-template",
            {"template": slug, "variables": variables or {}, **options},
        )

    def from_html_with_email(
        self,
        html: str,
        to: str,
        subject: str = "",
        body: str = "",
        **options: Any,
    ) -> dict:
        """Generate PDF and send via email."""
        email: dict[str, str] = {"to": to}
        if subject:
            email["subject"] = subject
        if body:
            email["body"] = body
        return self.from_html(html, email=email, **options)

    def info(self, filename: str) -> dict:
        """Get PDF file info."""
        return self._get(f"/api/pdf/info/{filename}")

    def download(self, filename: str) -> bytes:
        """Download PDF file content as bytes."""
        res = self.session.get(f"{self.base_url}/api/pdf/download/{filename}")
        if not res.ok:
            raise FunbrewError("Download failed", res.status_code)
        return res.content

    def delete(self, filename: str) -> dict:
        """Delete PDF file."""
        return self._request("DELETE", f"/api/pdf/delete/{filename}")

    def usage(self) -> dict:
        """Get usage information."""
        return self._get("/api/usage")

    def test(self, html: str, **options: Any) -> dict:
        """Generate PDF in test mode (no count, TEST watermark)."""
        return self.from_html(html, test=True, **options)

    def _get(self, path: str) -> dict:
        return self._request("GET", path)

    def _post(self, path: str, data: dict) -> dict:
        return self._request("POST", path, data)

    def _request(self, method: str, path: str, data: dict | None = None) -> dict:
        try:
            res = self.session.request(
                method,
                f"{self.base_url}{path}",
                json=data if method != "GET" else None,
            )
            body = res.json()
            if not res.ok:
                raise FunbrewError(
                    body.get("message", "API request failed"), res.status_code
                )
            return body
        except requests.RequestException as e:
            raise FunbrewError(f"Network error: {e}") from e
