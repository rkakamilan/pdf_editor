#!/usr/bin/env python3
import argparse
import os
import re
from typing import List, Tuple, Optional
from pypdf import PdfReader, PdfWriter


def get_toc_from_pdf(pdf_path: str) -> List[Tuple[str, int]]:
    """
    PDFから目次情報を取得する
    
    Args:
        pdf_path: PDFファイルのパス
        
    Returns:
        目次情報のリスト [(タイトル, ページ番号), ...]
    """
    reader = PdfReader(pdf_path)
    outlines = reader.outline
    
    # 目次が空の場合は空のリストを返す
    if not outlines:
        return []
    
    toc_entries = []
    
    def process_outline(outline, toc_entries):
        if isinstance(outline, list):
            for item in outline:
                process_outline(item, toc_entries)
        else:
            # ページ番号を取得（リンク先からページインデックスを解決）
            if hasattr(outline, "/Dest") and outline["/Dest"] is not None:
                try:
                    page_num = reader.get_destination_page_number(outline)
                    toc_entries.append((outline["/Title"], page_num))
                except:
                    pass
            elif hasattr(outline, "/A") and outline["/A"] is not None:
                try:
                    action = outline["/A"]
                    if action["/S"] == "/GoTo" and "/D" in action:
                        page_num = reader.get_destination_page_number(action["/D"])
                        toc_entries.append((outline["/Title"], page_num))
                except:
                    pass
    
    process_outline(outlines, toc_entries)
    return sorted(toc_entries, key=lambda x: x[1])


def split_by_max_pages(pdf_path: str, output_dir: str, max_pages: int) -> List[str]:
    """
    PDFを指定した最大ページ数で分割する
    
    Args:
        pdf_path: 分割するPDFファイルのパス
        output_dir: 出力先ディレクトリ
        max_pages: 1ファイルあたりの最大ページ数
        
    Returns:
        作成されたPDFファイルのパスのリスト
    """
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    output_files = []
    
    # 出力ディレクトリが存在しない場合は作成
    os.makedirs(output_dir, exist_ok=True)
    
    # ファイル名のベース部分を取得
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # 分割回数を計算
    num_parts = (total_pages + max_pages - 1) // max_pages
    
    for i in range(num_parts):
        writer = PdfWriter()
        start_page = i * max_pages
        end_page = min((i + 1) * max_pages, total_pages)
        
        # ページを追加
        for page_num in range(start_page, end_page):
            writer.add_page(reader.pages[page_num])
        
        # パディングされたインデックスを含むファイル名を作成
        output_file = os.path.join(output_dir, f"{base_name}_part{i+1:03d}.pdf")
        
        # PDFファイルを書き込む
        with open(output_file, "wb") as f:
            writer.write(f)
        
        output_files.append(output_file)
        print(f"Created: {output_file} (Pages {start_page+1}-{end_page})")
    
    return output_files


def split_by_toc(pdf_path: str, output_dir: str, max_pages: Optional[int] = None) -> List[str]:
    """
    PDFを目次に従って分割する
    
    Args:
        pdf_path: 分割するPDFファイルのパス
        output_dir: 出力先ディレクトリ
        max_pages: 1ファイルあたりの最大ページ数（オプション）
        
    Returns:
        作成されたPDFファイルのパスのリスト
    """
    reader = PdfReader(pdf_path)
    total_pages = len(reader.pages)
    output_files = []
    
    # 出力ディレクトリが存在しない場合は作成
    os.makedirs(output_dir, exist_ok=True)
    
    # ファイル名のベース部分を取得
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    
    # 目次情報を取得
    toc_entries = get_toc_from_pdf(pdf_path)
    
    # 目次がない場合は単純にページ数で分割
    if not toc_entries:
        print("No table of contents found. Splitting by page count.")
        return split_by_max_pages(pdf_path, output_dir, max_pages or 100)
    
    # 目次エントリに最終ページを追加
    toc_entries.append(("End", total_pages))
    
    # 各章を処理
    current_start = 0
    current_pages = []
    part_index = 1
    
    for i in range(len(toc_entries) - 1):
        title = toc_entries[i][0]
        start_page = toc_entries[i][1]
        end_page = toc_entries[i+1][1]
        
        # 現在の章のページ数
        chapter_pages = end_page - start_page
        
        # max_pagesが指定されていて、現在の蓄積ページ数 + この章のページ数が最大ページ数を超える場合
        if max_pages and current_pages and (sum(current_pages) + chapter_pages > max_pages):
            # 現在までの章を一つのファイルとして出力
            writer = PdfWriter()
            for page_num in range(current_start, start_page):
                writer.add_page(reader.pages[page_num])
            
            # ファイル名を作成（不正な文字を除去）
            safe_title = re.sub(r'[\\/*?:"<>|]', "_", title)
            output_file = os.path.join(output_dir, f"{base_name}_part{part_index:03d}.pdf")
            
            # PDFファイルを書き込む
            with open(output_file, "wb") as f:
                writer.write(f)
            
            output_files.append(output_file)
            print(f"Created: {output_file} (Pages {current_start+1}-{start_page})")
            
            # 現在のカウンターをリセット
            current_start = start_page
            current_pages = [chapter_pages]
            part_index += 1
        else:
            # この章を現在のファイルに追加
            current_pages.append(chapter_pages)
    
    # 最後のファイルを出力
    if current_start < total_pages:
        writer = PdfWriter()
        for page_num in range(current_start, total_pages):
            writer.add_page(reader.pages[page_num])
        
        output_file = os.path.join(output_dir, f"{base_name}_part{part_index:03d}.pdf")
        
        # PDFファイルを書き込む
        with open(output_file, "wb") as f:
            writer.write(f)
        
        output_files.append(output_file)
        print(f"Created: {output_file} (Pages {current_start+1}-{total_pages})")
    
    return output_files


def main():
    parser = argparse.ArgumentParser(description="PDFを指定したページ数または目次に従って分割するツール")
    parser.add_argument("pdf_path", help="分割するPDFファイルのパス")
    parser.add_argument("-o", "--output-dir", default="output", help="出力先ディレクトリ（デフォルト: output）")
    parser.add_argument("-m", "--max-pages", type=int, help="1ファイルあたりの最大ページ数")
    parser.add_argument("-t", "--use-toc", action="store_true", help="目次に従って分割する")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.pdf_path):
        print(f"エラー: ファイル '{args.pdf_path}' が見つかりません。")
        return
    
    try:
        if args.use_toc:
            print(f"PDFを目次に従って分割します（最大ページ数: {args.max_pages or '無制限'}）")
            output_files = split_by_toc(args.pdf_path, args.output_dir, args.max_pages)
        else:
            if not args.max_pages:
                print("エラー: 目次モードを使用しない場合は、最大ページ数（--max-pages）を指定してください。")
                return
            print(f"PDFを{args.max_pages}ページごとに分割します")
            output_files = split_by_max_pages(args.pdf_path, args.output_dir, args.max_pages)
        
        print(f"\n分割完了: {len(output_files)}個のファイルが作成されました")
    except Exception as e:
        print(f"エラーが発生しました: {e}")


if __name__ == "__main__":
    main()