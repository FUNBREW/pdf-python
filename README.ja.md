# funbrew-pdf

FUNBREW PDF APIのPythonクライアントライブラリです。

## インストール

```bash
pip install funbrew-pdf
```

## 使い方

```python
from funbrew_pdf import FunbrewPdf

pdf = FunbrewPdf("sk-your-api-key")

# HTML → PDF
result = pdf.from_html("<h1>Hello World</h1>")
print(result["data"]["download_url"])

# URL → PDF
result = pdf.from_url("https://example.com")

# テンプレート → PDF
result = pdf.from_template("invoice", {
    "company_name": "FUNBREW Inc.",
    "amount": "100,000",
})

# PDF生成 + メール送信
result = pdf.from_html_with_email(
    "<h1>請求書</h1>",
    "customer@example.com",
    subject="請求書をお送りします",
)

# テストモード
result = pdf.test("<h1>Test</h1>")

# ダウンロード
content = pdf.download("uuid.pdf")
with open("output.pdf", "wb") as f:
    f.write(content)

# 利用状況
usage = pdf.usage()
```

## オプション

```python
result = pdf.from_html("<h1>Hello</h1>",
    options={"page-size": "A3"},
    expiration_hours=168,
    max_downloads=5,
    password="secret",
    watermark="CONFIDENTIAL",
)
```
