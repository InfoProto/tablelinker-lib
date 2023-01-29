import csv
import io
import os
import tempfile

import pytest

from tablelinker import Table

sample_dir = os.path.join(os.path.dirname(__file__), "../sample/")


def test_excel_open():
    # シート名を指定せずに Excel ファイルを開くと
    # 最初のシートが開く
    table = Table(
        file=os.path.join(sample_dir, "hachijo_sightseeing.xlsx"),
        sheet=None)
    with table.open() as reader:
        for row in reader:
            assert ",".join(row) == (
                "観光スポット名称,所在地,緯度,経度,座標系,"
                "説明,八丈町ホームページ記載"
            )
            break

    # 存在しないシート名を指定して Excel ファイルを開くと
    # ValueError
    table = Table(
        file=os.path.join(sample_dir, "hachijo_sightseeing.xlsx"),
        sheet="その他")
    with pytest.raises(ValueError):
        table.open()

    # 存在するシート名を指定して Excel ファイルを開く
    table = Table(
        file=os.path.join(sample_dir, "hachijo_sightseeing.xlsx"),
        sheet="観光スポット")
    with table.open() as reader:
        for row in reader:
            assert ",".join(row) == (
                "観光スポット名称,所在地,緯度,経度,座標系,"
                "説明,八丈町ホームページ記載"
            )
            break


def test_excel_save():
    table = Table(os.path.join(sample_dir, "hachijo_sightseeing.xlsx"))

    with tempfile.TemporaryDirectory() as tmpdir:
        temppath = os.path.join(tmpdir, "tmpfile.csv")
        table.save(temppath)

        with open(temppath, "r", newline="") as f:
            reader = csv.reader(f)
            for lineno, row in enumerate(reader):
                assert len(row) == 7
                if lineno == 0:
                    assert ",".join(row) == (
                        "観光スポット名称,所在地,緯度,経度,座標系,"
                        "説明,八丈町ホームページ記載"
                    )


def test_excel_write():
    table = Table(os.path.join(sample_dir, "hachijo_sightseeing.xlsx"))

    # write() の出力をテキストバッファに保存
    buf = io.StringIO()
    table.write(lines=5, file=buf)

    # バッファの内容を csv reader で読み込んで検証
    with io.StringIO(buf.getvalue()) as f:
        reader = csv.reader(f)
        for lineno, row in enumerate(reader):
            assert len(row) == 7
            if lineno == 0:
                assert ",".join(row) == (
                    "観光スポット名称,所在地,緯度,経度,座標系,"
                    "説明,八丈町ホームページ記載"
                )

            assert lineno < 5


def test_excel_convert():
    table = Table(os.path.join(sample_dir, "hachijo_sightseeing.xlsx"))
    table = table.convert(
        convertor="move_col",
        params={
            "input_attr_idx": "座標系",
        },
    )

    with table.open() as csv:
        for lineno, row in enumerate(csv):
            assert len(row) == 7
            if lineno == 0:
                # ヘッダ「座標系」が最後尾に移動していることを確認
                assert ",".join(row) == (
                    "観光スポット名称,所在地,緯度,経度,"
                    "説明,八丈町ホームページ記載,座標系")

            elif lineno == 1:
                # レコードから座標系列が削除されていることを確認
                assert ",".join(row[0:4]) == "ホタル水路,,33.108218,139.80102"
                assert row[4].startswith("八丈島は伊豆諸島で唯一、")
                assert row[5] == (
                    "http://www.town.hachijo.tokyo.jp/kankou_spot/"
                    "mitsune.html#01")
