# funbrew-pdf

Official Python client library for the [FUNBREW PDF API](https://pdf.funbrew.cloud). Type hints included.

[日本語ドキュメント](README.ja.md)

## Installation

```bash
pip install funbrew-pdf
```

## Quick Start

```python
from funbrew_pdf import FunbrewPdf

pdf = FunbrewPdf("sk-your-api-key")

# HTML to PDF
result = pdf.from_html("<h1>Hello World</h1>")
print(result["data"]["download_url"])

# URL to PDF
result = pdf.from_url("https://example.com")

# Markdown to PDF
result = pdf.from_markdown("# Hello World", theme="modern")

# List available Markdown themes
themes = pdf.markdown_themes()

# Template to PDF
result = pdf.from_template("invoice", {
    "company_name": "Acme Inc.",
    "amount": "1,000",
})
```

## Features

```python
# Generate PDF and send via email
result = pdf.from_html_with_email(
    "<h1>Invoice</h1>",
    "customer@example.com",
    subject="Your invoice is ready",
)

# Test mode (no count, TEST watermark)
result = pdf.test("<h1>Test</h1>")

# File operations
info = pdf.info("uuid.pdf")
content = pdf.download("uuid.pdf")
with open("output.pdf", "wb") as f:
    f.write(content)
pdf.delete("uuid.pdf")

# Usage stats
usage = pdf.usage()
```

## Split PDF

```python
# Extract pages 1-3
result = pdf.split("uuid.pdf", "1-3")

# Extract specific pages
result = pdf.split("uuid.pdf", "1,3,5")

# Mix ranges and individual pages
result = pdf.split("uuid.pdf", "1,3-5")
```

## Rotate PDF

```python
# Rotate all pages 90 degrees
result = pdf.rotate("uuid.pdf", 90)

# Rotate specific pages only
result = pdf.rotate("uuid.pdf", 180, pages="1,3")

# Supported angles: 90, 180, 270
result = pdf.rotate("uuid.pdf", 270)
```

## Compress PDF

```python
# Compress with default quality (medium)
result = pdf.compress("uuid.pdf")
print(f"Saved {result['data']['savings_percent']}%")

# Quality levels: low, medium, high
result = pdf.compress("uuid.pdf", quality="low")
```

## Extract Text

```python
# Extract all text
result = pdf.extract_text("uuid.pdf")
print(result["data"]["text"])

# Extract from specific pages
result = pdf.extract_text("uuid.pdf", pages="1,3")

# Get per-page text
result = pdf.extract_text("uuid.pdf", per_page=True)
for page in result["data"]["pages"]:
    print(f"Page {page['page']}: {page['text']}")
```

## Metadata

```python
# Read metadata
result = pdf.metadata("uuid.pdf")
print(result["data"]["title"], result["data"]["author"])

# Set metadata (returns new file)
result = pdf.metadata("uuid.pdf", title="Invoice", author="FUNBREW")
```

## Page Numbers

```python
# Add page numbers (bottom-center by default)
result = pdf.page_numbers("uuid.pdf")

# Custom position and format
result = pdf.page_numbers("uuid.pdf",
    position="top-right",
    format="Page {page} of {total}",
    start_number=1,
)
```

## PDF/A Conversion

```python
# Convert to PDF/A-2b (default)
result = pdf.to_pdfa("uuid.pdf")

# Specify conformance level: 1b, 2b, 3b
result = pdf.to_pdfa("uuid.pdf", conformance="1b")
```

## PDF to Image

```python
# Convert all pages to PNG (default)
result = pdf.to_image("uuid.pdf")
for img in result["data"]["images"]:
    print(img["download_url"])

# Convert to JPG
result = pdf.to_image("uuid.pdf", format="jpg")

# Convert specific pages with custom DPI
result = pdf.to_image("uuid.pdf", pages="1,3", dpi=300)
```

## Merge PDFs

```python
# Merge server-side PDFs
result = pdf.merge(["uuid1.pdf", "uuid2.pdf"])

# Merge uploaded local files
result = pdf.merge_upload(["file1.pdf", "file2.pdf"])

# Mix uploaded and server files
result = pdf.merge_upload(
    ["local.pdf"],
    server_filenames=["uuid1.pdf"],
)
```

## Markdown Preview

```python
# Preview Markdown as HTML (no PDF generated)
result = pdf.markdown_preview("# Hello World", theme="modern")
html = result["data"]["html"]
```

## Webhooks (SaaS)

```python
# List webhooks
webhooks = pdf.webhooks()

# Create webhook
wh = pdf.create_webhook("https://example.com/hook", ["pdf.generated"])

# Update webhook
pdf.update_webhook(wh["data"]["id"], is_active=False)

# Delete webhook
pdf.delete_webhook(wh["data"]["id"])
```

## Templates (SaaS)

```python
# List templates
templates = pdf.templates()

# Create template
tpl = pdf.create_template(
    name="Invoice",
    slug="invoice",
    html_content="<h1>{{ company_name }}</h1>",
    variables=[{"name": "company_name", "required": True}],
)

# Update template
pdf.update_template(tpl["data"]["id"], name="Invoice v2")

# Delete template
pdf.delete_template(tpl["data"]["id"])
```

## Storage Config (SaaS)

```python
# Get storage config
config = pdf.storage_config()

# Create storage config (S3 or GCS)
pdf.create_storage_config("s3", {"bucket": "my-bucket", "region": "us-east-1"})

# Update storage config
pdf.update_storage_config(is_active=False)

# Delete storage config
pdf.delete_storage_config()
```

## Options

```python
result = pdf.from_html("<h1>Hello</h1>",
    options={"page-size": "A3", "orientation": "Landscape"},
    expiration_hours=168,
    max_downloads=5,
    password="secret",
    watermark="CONFIDENTIAL",
)
```

## Error Handling

```python
from funbrew_pdf import FunbrewPdf, FunbrewError

try:
    result = pdf.from_html("<h1>Hello</h1>")
except FunbrewError as e:
    print(e)               # Error message
    print(e.status_code)   # HTTP status code
```

## License

MIT
