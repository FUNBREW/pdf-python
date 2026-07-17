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
        base_url: API base URL (default: https://pdf.funbrew.cloud)
    """

    def __init__(self, api_key: str, base_url: str = "https://pdf.funbrew.cloud"):
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

    def from_markdown(
        self, markdown: str, theme: str = "business", **options: Any
    ) -> dict:
        """Generate PDF from Markdown content.

        Args:
            markdown: Markdown content to convert
            theme: Theme name (business, modern, minimal, academic, creative)
            **options: Additional options (options, filename, etc.)
        """
        return self._post(
            "/api/pdf/generate-from-markdown",
            {"markdown": markdown, "theme": theme, **options},
        )

    def markdown_themes(self) -> dict:
        """Get available Markdown themes."""
        return self._get("/api/markdown/themes")

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

    def batch(self, items: list[dict]) -> dict:
        """Batch generate multiple PDFs."""
        return self._post("/api/pdf/batch", {"items": items})

    def batch_status(self, batch_uuid: str) -> dict:
        """Get batch generation status."""
        return self._get(f"/api/pdf/batch/{batch_uuid}")

    def merge(self, filenames: list[str], **options: Any) -> dict:
        """Merge multiple PDFs into one."""
        return self._post("/api/pdf/merge", {"filenames": filenames, **options})

    def merge_upload(
        self,
        files: list[str],
        server_filenames: list[str] | None = None,
        **options: Any,
    ) -> dict:
        """Merge uploaded PDF files (and optionally server files) into one.

        Args:
            files: List of file paths to upload
            server_filenames: Existing server filenames to include in the merge
            **options: Additional options (expiration_hours, max_downloads, watermark)
        """
        opened = []
        multipart_files = []
        try:
            for path in files:
                f = open(path, "rb")
                opened.append(f)
                multipart_files.append(("files[]", (path.rsplit("/", 1)[-1], f, "application/pdf")))

            data: dict[str, Any] = {}
            if server_filenames:
                for name in server_filenames:
                    data.setdefault("filenames[]", [])
                    if isinstance(data["filenames[]"], list):
                        data["filenames[]"].append(name)
            data.update(options)

            res = requests.post(
                f"{self.base_url}/api/pdf/merge-upload",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Accept": "application/json",
                },
                files=multipart_files,
                data=data,
                timeout=60,
            )
            body = res.json()
            if not res.ok:
                raise FunbrewError(
                    body.get("message", "API request failed"), res.status_code
                )
            return body
        except requests.RequestException as e:
            raise FunbrewError(f"Network error: {e}") from e
        finally:
            for f in opened:
                f.close()

    # --- Split / Rotate / Compress ---

    def split(self, filename: str, pages: str, **options: Any) -> dict:
        """Split a PDF by extracting specific pages.

        Args:
            filename: Source PDF filename on server
            pages: Page specification (e.g. "1-3", "1,3,5", "1,3-5")
            **options: Additional options (expiration_hours, max_downloads)
        """
        return self._post(
            "/api/pdf/split", {"filename": filename, "pages": pages, **options}
        )

    def rotate(
        self, filename: str, angle: int, pages: str | None = None, **options: Any
    ) -> dict:
        """Rotate PDF pages.

        Args:
            filename: Source PDF filename on server
            angle: Rotation angle (90, 180, or 270)
            pages: Optional page specification (e.g. "1,3"). Rotates all if omitted.
            **options: Additional options (expiration_hours, max_downloads)
        """
        payload: dict[str, Any] = {"filename": filename, "angle": angle, **options}
        if pages is not None:
            payload["pages"] = pages
        return self._post("/api/pdf/rotate", payload)

    def compress(
        self, filename: str, quality: str = "medium", **options: Any
    ) -> dict:
        """Compress a PDF to reduce file size.

        Args:
            filename: Source PDF filename on server
            quality: Compression quality ("low", "medium", "high")
            **options: Additional options (expiration_hours, max_downloads)
        """
        return self._post(
            "/api/pdf/compress",
            {"filename": filename, "quality": quality, **options},
        )

    def to_image(
        self, filename: str, format: str = "png", **options: Any
    ) -> dict:
        """Convert PDF pages to images.

        Args:
            filename: Source PDF filename on server
            format: Output format ("png" or "jpg")
            **options: Additional options (pages, dpi)
        """
        return self._post(
            "/api/pdf/to-image",
            {"filename": filename, "format": format, **options},
        )

    def extract_text(self, filename: str, **options: Any) -> dict:
        """Extract text from a PDF.

        Args:
            filename: Source PDF filename on server
            **options: Additional options (pages, per_page)
        """
        return self._post(
            "/api/pdf/extract-text", {"filename": filename, **options}
        )

    def metadata(self, filename: str, **fields: Any) -> dict:
        """Read or set PDF metadata.

        When only filename is provided, reads metadata.
        When fields (title, author, subject, keywords) are provided, creates a new PDF with updated metadata.

        Args:
            filename: Source PDF filename on server
            **fields: Metadata fields to set (title, author, subject, keywords, creator, producer)
        """
        return self._post("/api/pdf/metadata", {"filename": filename, **fields})

    def page_numbers(self, filename: str, **options: Any) -> dict:
        """Add page numbers to a PDF.

        Args:
            filename: Source PDF filename on server
            **options: Options (position, format, start_number, font_size, expiration_hours, max_downloads)
        """
        return self._post(
            "/api/pdf/page-numbers", {"filename": filename, **options}
        )

    def to_pdfa(self, filename: str, conformance: str = "2b", **options: Any) -> dict:
        """Convert PDF to PDF/A archival format.

        Args:
            filename: Source PDF filename on server
            conformance: PDF/A conformance level ("1b", "2b", "3b")
            **options: Additional options (expiration_hours, max_downloads)
        """
        return self._post(
            "/api/pdf/to-pdfa",
            {"filename": filename, "conformance": conformance, **options},
        )

    # --- Markdown ---

    def markdown_preview(self, markdown: str, theme: str = "business") -> dict:
        """Preview Markdown as HTML.

        Args:
            markdown: Markdown content to preview
            theme: Theme name (default: business)
        """
        return self._post(
            "/api/markdown/preview", {"markdown": markdown, "theme": theme}
        )

    # --- Webhooks (SaaS) ---

    def webhooks(self) -> dict:
        """List all webhooks."""
        return self._get("/api/webhooks")

    def create_webhook(self, url: str, events: list[str]) -> dict:
        """Create a webhook.

        Args:
            url: Webhook URL
            events: List of event names to subscribe to
        """
        return self._post("/api/webhooks", {"url": url, "events": events})

    def update_webhook(self, webhook_id: int, **data: Any) -> dict:
        """Update a webhook.

        Args:
            webhook_id: Webhook ID
            **data: Fields to update (url, events, is_active)
        """
        return self._request("PUT", f"/api/webhooks/{webhook_id}", data)

    def delete_webhook(self, webhook_id: int) -> dict:
        """Delete a webhook."""
        return self._request("DELETE", f"/api/webhooks/{webhook_id}")

    # --- Templates (SaaS) ---

    def templates(self) -> dict:
        """List all templates."""
        return self._get("/api/templates")

    def create_template(
        self,
        name: str,
        slug: str,
        html_content: str,
        variables: list[dict] | None = None,
    ) -> dict:
        """Create a template.

        Args:
            name: Template name
            slug: URL-safe slug (lowercase alphanumeric and hyphens)
            html_content: HTML content with {{ variable }} placeholders
            variables: List of variable definitions [{"name": "...", "required": true}]
        """
        payload: dict[str, Any] = {
            "name": name,
            "slug": slug,
            "html_content": html_content,
        }
        if variables is not None:
            payload["variables"] = variables
        return self._post("/api/templates", payload)

    def update_template(self, template_id: int, **data: Any) -> dict:
        """Update a template.

        Args:
            template_id: Template ID
            **data: Fields to update (name, html_content, variables, is_active)
        """
        return self._request("PUT", f"/api/templates/{template_id}", data)

    def delete_template(self, template_id: int) -> dict:
        """Delete a template."""
        return self._request("DELETE", f"/api/templates/{template_id}")

    # --- Storage Config (SaaS) ---

    def storage_config(self) -> dict:
        """Get current storage configuration."""
        return self._get("/api/storage-config")

    def create_storage_config(self, driver: str, config: dict) -> dict:
        """Create storage configuration.

        Args:
            driver: Storage driver ("s3" or "gcs")
            config: Driver config (must include "bucket")
        """
        return self._post(
            "/api/storage-config", {"driver": driver, "config": config}
        )

    def update_storage_config(self, **data: Any) -> dict:
        """Update storage configuration.

        Args:
            **data: Fields to update (driver, config, is_active)
        """
        return self._request("PUT", "/api/storage-config", data)

    def delete_storage_config(self) -> dict:
        """Delete storage configuration."""
        return self._request("DELETE", "/api/storage-config")

    # --- Usage & Test ---

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
