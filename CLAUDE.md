# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

PDF分割ツールは、1500ページを超える大きなPDFファイルを複数の小さなファイルに分割するPythonスクリプトです。

### 主な機能

- ページ数による分割: 指定した最大ページ数ごとにPDFを分割
- 目次による分割: PDFの目次（しおり）に従って分割（オプションで最大ページ数も指定可能）

## 開発環境のセットアップ

このプロジェクトは [uv](https://github.com/astral-sh/uv) を使用しています。Python 3.11以上が必要です。

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
   - PDFのアウトライン（目次）構造を再帰的に処理し、各エントリのタイトルとページ番号を取得
   - ページ番号順にソートされたタプルのリスト `[(タイトル, ページ番号), ...]` を返す

2. **split_by_max_pages()**: 最大ページ数でPDFを分割する
   - 指定された最大ページ数ごとにPDFを分割し、新しいファイルを作成
   - ファイル名は元のファイル名に連番を付けた形式（例: `document_part001.pdf`）

3. **split_by_toc()**: 目次に基づいてPDFを分割する
   - PDFの目次構造に従って分割し、各章や節ごとに新しいファイルを作成
   - `max_pages`パラメータが指定されている場合は、章の合計ページ数がこの値を超えないよう調整

4. **main()**: コマンドライン引数を解析し、適切な分割関数を呼び出す
   - argparseを使用してコマンドライン引数を処理
   - 引数に基づいて適切な分割関数を選択して実行

## 開発の注意点

- PDFの目次構造は複雑な場合があり、すべてのPDFで正常に動作するとは限りません
- 大きなPDFファイルの処理はメモリを大量に消費する可能性があるため、非常に大きなファイルを扱う場合はメモリ使用量に注意してください
- 目次情報がないPDFの場合、`--use-toc`オプションを使用しても自動的にページ数による分割にフォールバックします
- エラー処理が実装されていますが、PDFファイルの構造によっては予期しないエラーが発生する可能性があります

## デバッグとテスト

テスト用の小さなPDFファイルでスクリプトの動作を確認することをお勧めします：

```bash
# テスト用の小さなPDFで実行
python main.py test.pdf --max-pages 10

# 詳細な情報を表示して実行（将来的に実装予定）
python main.py large.pdf --max-pages 100 --verbose
```