#!/usr/bin/env python3
"""
テスト用の共通設定とモックオブジェクト
"""
from unittest.mock import MagicMock


def create_mock_pdf_with_toc():
    """
    目次付きのモックPDFリーダーを作成

    Returns:
        目次情報を持ったモックPDFReaderオブジェクト
    """
    mock_reader = MagicMock()
    # 10ページのPDFをシミュレート
    mock_reader.pages = [MagicMock() for _ in range(10)]

    # 目次情報を設定
    outline_item1 = MagicMock()
    outline_item1.__getitem__.side_effect = lambda key: "Chapter 1" if key == "/Title" else "dest1"

    outline_item2 = MagicMock()
    outline_item2.__getitem__.side_effect = lambda key: "Chapter 2" if key == "/Title" else "dest2"

    outline_item3 = MagicMock()
    outline_item3.__getitem__.side_effect = lambda key: "Chapter 3" if key == "/Title" else "dest3"

    mock_reader.outline = [outline_item1, outline_item2, outline_item3]

    # get_destination_page_numberメソッドをモック
    mock_reader.get_destination_page_number.side_effect = lambda x: {
        "dest1": 0,  # Chapter 1 (ページ 1)
        outline_item1: 0,
        "dest2": 3,  # Chapter 2 (ページ 4)
        outline_item2: 3,
        "dest3": 7,  # Chapter 3 (ページ 8)
        outline_item3: 7
    }[x]

    return mock_reader


def create_mock_pdf_without_toc():
    """
    目次なしのモックPDFリーダーを作成

    Returns:
        目次情報を持たないモックPDFReaderオブジェクト
    """
    mock_reader = MagicMock()
    # 10ページのPDFをシミュレート
    mock_reader.pages = [MagicMock() for _ in range(10)]

    # 目次なし
    mock_reader.outline = []

    return mock_reader


def create_mock_pdf_with_action_toc():
    """
    Actionタイプの目次を持つモックPDFリーダーを作成

    Returns:
        Actionタイプの目次情報を持ったモックPDFReaderオブジェクト
    """
    mock_reader = MagicMock()
    # 10ページのPDFをシミュレート
    mock_reader.pages = [MagicMock() for _ in range(10)]

    # Action目次情報を設定
    outline_item1 = MagicMock()

    def getitem_side_effect1(key):
        if key == "/Title":
            return "Chapter 1"
        elif key == "/Dest":
            return None
        elif key == "/A":
            action = MagicMock()
            action.__getitem__.side_effect = lambda k: "/GoTo" if k == "/S" else "dest1" if k == "/D" else None
            return action
        return None

    outline_item1.__getitem__.side_effect = getitem_side_effect1

    outline_item2 = MagicMock()

    def getitem_side_effect2(key):
        if key == "/Title":
            return "Chapter 2"
        elif key == "/Dest":
            return None
        elif key == "/A":
            action = MagicMock()
            action.__getitem__.side_effect = lambda k: "/GoTo" if k == "/S" else "dest2" if k == "/D" else None
            return action
        return None

    outline_item2.__getitem__.side_effect = getitem_side_effect2

    mock_reader.outline = [outline_item1, outline_item2]

    # get_destination_page_numberメソッドをモック
    mock_reader.get_destination_page_number.side_effect = lambda x: {
        "dest1": 0,
        "dest2": 5
    }[x]

    return mock_reader