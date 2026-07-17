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

# Markdown → PDF
result = pdf.from_markdown("# Hello World", theme="modern")

# Markdownテーマ一覧を取得
themes = pdf.markdown_themes()

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

## PDF分割

```python
# ページ1〜3を抽出
result = pdf.split("uuid.pdf", "1-3")

# 特定ページを抽出
result = pdf.split("uuid.pdf", "1,3,5")

# 範囲と個別ページの混合
result = pdf.split("uuid.pdf", "1,3-5")
```

## ページ回転

```python
# 全ページを90度回転
result = pdf.rotate("uuid.pdf", 90)

# 特定ページのみ回転
result = pdf.rotate("uuid.pdf", 180, pages="1,3")

# 対応角度: 90, 180, 270
result = pdf.rotate("uuid.pdf", 270)
```

## PDF圧縮

```python
# デフォルト品質（medium）で圧縮
result = pdf.compress("uuid.pdf")
print(f"削減率: {result['data']['savings_percent']}%")

# 品質レベル: low, medium, high
result = pdf.compress("uuid.pdf", quality="low")
```

## テキスト抽出

```python
# 全テキストを抽出
result = pdf.extract_text("uuid.pdf")
print(result["data"]["text"])

# 特定ページのみ
result = pdf.extract_text("uuid.pdf", pages="1,3")

# ページごとに取得
result = pdf.extract_text("uuid.pdf", per_page=True)
for page in result["data"]["pages"]:
    print(f"ページ{page['page']}: {page['text']}")
```

## メタデータ

```python
# メタデータ読み取り
result = pdf.metadata("uuid.pdf")
print(result["data"]["title"], result["data"]["author"])

# メタデータ設定（新しいファイルを返す）
result = pdf.metadata("uuid.pdf", title="請求書", author="FUNBREW")
```

## ページ番号挿入

```python
# ページ番号追加（デフォルト: 下中央）
result = pdf.page_numbers("uuid.pdf")

# カスタム位置・書式
result = pdf.page_numbers("uuid.pdf",
    position="top-right",
    format="Page {page} of {total}",
    start_number=1,
)
```

## PDF/A変換

```python
# PDF/A-2b（デフォルト）に変換
result = pdf.to_pdfa("uuid.pdf")

# 準拠レベル指定: 1b, 2b, 3b
result = pdf.to_pdfa("uuid.pdf", conformance="1b")
```

## PDF→画像変換

```python
# 全ページをPNGに変換（デフォルト）
result = pdf.to_image("uuid.pdf")
for img in result["data"]["images"]:
    print(img["download_url"])

# JPGに変換
result = pdf.to_image("uuid.pdf", format="jpg")

# 特定ページをカスタムDPIで変換
result = pdf.to_image("uuid.pdf", pages="1,3", dpi=300)
```

## PDFマージ

```python
# サーバー上のPDFをマージ
result = pdf.merge(["uuid1.pdf", "uuid2.pdf"])

# ローカルファイルをアップロードしてマージ
result = pdf.merge_upload(["file1.pdf", "file2.pdf"])

# ローカルファイルとサーバー上のファイルを混合マージ
result = pdf.merge_upload(
    ["local.pdf"],
    server_filenames=["uuid1.pdf"],
)
```

## Markdownプレビュー

```python
# MarkdownをHTMLとしてプレビュー（PDF生成なし）
result = pdf.markdown_preview("# Hello World", theme="modern")
html = result["data"]["html"]
```

## Webhook管理（SaaS版）

```python
# Webhook一覧
webhooks = pdf.webhooks()

# Webhook作成
wh = pdf.create_webhook("https://example.com/hook", ["pdf.generated"])

# Webhook更新
pdf.update_webhook(wh["data"]["id"], is_active=False)

# Webhook削除
pdf.delete_webhook(wh["data"]["id"])
```

## テンプレート管理（SaaS版）

```python
# テンプレート一覧
templates = pdf.templates()

# テンプレート作成
tpl = pdf.create_template(
    name="請求書",
    slug="invoice",
    html_content="<h1>{{ company_name }}</h1>",
    variables=[{"name": "company_name", "required": True}],
)

# テンプレート更新
pdf.update_template(tpl["data"]["id"], name="請求書 v2")

# テンプレート削除
pdf.delete_template(tpl["data"]["id"])
```

## ストレージ設定（SaaS版）

```python
# ストレージ設定取得
config = pdf.storage_config()

# ストレージ設定作成（S3またはGCS）
pdf.create_storage_config("s3", {"bucket": "my-bucket", "region": "us-east-1"})

# ストレージ設定更新
pdf.update_storage_config(is_active=False)

# ストレージ設定削除
pdf.delete_storage_config()
```

## オプション

```python
result = pdf.from_html("<h1>Hello</h1>",
    options={"page-size": "A3", "orientation": "Landscape"},
    expiration_hours=168,
    max_downloads=5,
    password="secret",
    watermark="CONFIDENTIAL",
)
```
