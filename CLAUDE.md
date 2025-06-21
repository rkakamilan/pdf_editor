# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

PDF分割ツールは、1500ページを超える大きなPDFファイルを複数の小さなファイルに分割するPythonスクリプトです。

### 主な機能

- ページ数による分割: 指定した最大ページ数ごとにPDFを分割
- 目次による分割: PDFの目次（しおり）に従って分割（オプションで最大ページ数も指定可能）

## 開発環境のセットアップ

このプロジェクトは [uv](https://github.com/astral-sh/uv) を使用しています。

```bash
# 必要な依存関係をインストール
uv add pypdf
```

## コマンド実行例

### スクリプト実行

```bash
# ページ数で分割
python main.py path/to/large.pdf --max-pages 100

# 目次で分割
python main.py path/to/large.pdf --use-toc

# 目次で分割し、最大ページ数を指定
python main.py path/to/large.pdf --use-toc --max-pages 200

# 出力先ディレクトリを指定
python main.py path/to/large.pdf --max-pages 100 --output-dir custom_output
```

## コードアーキテクチャ

プロジェクトは単一のPythonスクリプト（main.py）で構成されています。主要なコンポーネントは次のとおりです：

1. **get_toc_from_pdf()**: PDFから目次情報を抽出する
2. **split_by_max_pages()**: 最大ページ数でPDFを分割する
3. **split_by_toc()**: 目次に基づいてPDFを分割する
4. **main()**: コマンドライン引数を解析し、適切な分割関数を呼び出す

## 開発の注意点

- PDFの目次構造は複雑な場合があり、すべてのPDFで正常に動作するとは限りません
- 大きなPDFファイルの処理はメモリを大量に消費する可能性があるため、非常に大きなファイルを扱う場合はメモリ使用量に注意してください