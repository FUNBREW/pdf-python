# funbrew-pdf

Official Python client library for the [FUNBREW PDF API](https://pdf.funbrew.tech). Type hints included.

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

## Options

```python
result = pdf.from_html("<h1>Hello</h1>",
    options={"page-size": "A3"},
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
