import os
import sys

from tablelinker import Table

sample_dir = os.path.join(os.path.dirname(__file__), "../sample/")

original_sakurai_header = (
    "市区町村コード,NO,都道府県名,市区町村名,"
    "名称,名称_カナ,名称_英語,POIコード,"
    "住所,方書,緯度,経度,利用可能曜日,開始時間,終了時間,"
    "利用可能日時特記事項,料金(基本),料金(詳細),"
    "説明,説明_英語,アクセス方法,駐車場情報,"
    "バリアフリー情報,連絡先名称,連絡先電話番号,"
    "連絡先内線番号,画像,画像_ライセンス,URL,備考"
)

def test_calc_col():
    table = Table(os.path.join(sample_dir, "ma030000.csv"))
    table = table.convert(
        convertor="calc",
        params={
            "input_attr_idx1": "出生数",
            "input_attr_idx2": "人口",
            "operator": "/",
            "output_attr_name": "出生率（計算）",
            "overwrite": False
        },
    )

    with table.open() as csv:
        for lineno, row in enumerate(csv):
            assert len(row) == 16
            if lineno == 0:
                # ヘッダに「出生率（計算）」が追加されていることを確認
                assert ",".join(row) == (
                    ',人口,出生数,死亡数,（再掲）,,自　然,死産数,,,'
                    '周産期死亡数,,,婚姻件数,離婚件数,出生率（計算）')

            elif lineno == 4:
                # 計算結果が正しいことを確認
                assert abs(float(row[-1]) - 0.00569) < 1.0e-6


def test_concat_col():
    table = Table(os.path.join(
        sample_dir, "sakurai_sightseeing_spots_sjis.csv"))
    table = table.convert(
        convertor="concat",
        params={
            "input_attr_idx1": "都道府県名",
            "input_attr_idx2": "市区町村名",
            "separator": " ",
            "output_attr_name": "自治体名",
            "delete_col": True
        },
    )

    with table.open() as csv:
        for lineno, row in enumerate(csv):
            assert len(row) == 29
            if lineno == 0:
                # ヘッダから「都道府県名」「市区町村名」が削除され、
                # 「自治体名」が追加されていることを確認
                assert ",".join(row) == (
                    "市区町村コード,NO,名称,名称_カナ,名称_英語,POIコード,"
                    "住所,方書,緯度,経度,利用可能曜日,開始時間,終了時間,"
                    "利用可能日時特記事項,料金(基本),料金(詳細),"
                    "説明,説明_英語,アクセス方法,駐車場情報,"
                    "バリアフリー情報,連絡先名称,連絡先電話番号,"
                    "連絡先内線番号,画像,画像_ライセンス,URL,備考,自治体名"
                )

            elif lineno > 0:
                # 結合結果を確認
                assert row[-1] == "山口県 柳井市"


def test_delete_col():
    table = Table(os.path.join(
        sample_dir, "hachijo_sightseeing.csv"))
    table = table.convert(
        convertor="delete_col",
        params={
            "input_attr_idx": "座標系",
        },
    )

    with table.open() as csv:
        for lineno, row in enumerate(csv):
            assert len(row) == 6
            if lineno == 0:
                # ヘッダに「座標系」が存在しないことを確認
                assert ",".join(row) == (
                    "観光スポット名称,所在地,緯度,経度,"
                    "説明,八丈町ホームページ記載")

            elif lineno == 1:
                # レコードから座標系列が削除されていることを確認
                assert ",".join(row[0:4]) == "ホタル水路,,33.108218,139.80102"
                assert row[4].startswith("八丈島は伊豆諸島で唯一、")
                assert row[5] == "http://www.town.hachijo.tokyo.jp/kankou_spot/mitsune.html#01"


def test_delete_string_match():
    table = Table(os.path.join(
        sample_dir, "ma030000.csv"))
    table = table.convert(
        convertor="delete_string_match",
        params={
            "input_attr_idx": 0,
            "query": "",
        },
    )

    with table.open() as csv:
        lines = 0
        for row in csv:
            assert len(row) == 15
            assert row[0] != ""
            lines += 1

        # 出力行数をチェック
        assert lines == 71


def test_delete_string_contains():
    table = Table(os.path.join(
        sample_dir, "ma030000.csv"))
    table = table.convert(
        convertor="delete_string_contains",
        params={
            "input_attr_idx": 0,
            "query": "市",
        },
    )

    with table.open() as csv:
    lines = 0
    for row in dictreader:
        assert len(row) == 15
        assert "市" not in row[""]
        lines += 1

    # 出力行数をチェック
    assert lines == 53


def test_delete_pattern_match():
    table = Table(os.path.join(
        sample_dir, "ma030000.csv"))
    table = table.convert(
        convertor="delete_pattern_match",
        params={
            "input_attr_idx": 0,
            "pattern":"(^$|.+区部$|.+市$)",
        },
    )

    dictreader = table.open(as_dict=True)
    lines = 0
    for row in dictreader:
        assert len(row) == 15
        assert row[""] != ""
        assert not row[""].endswith("区部")
        assert not row[""].endswith("市")
        lines += 1

    # 出力行数をチェック
    assert lines == 50


def test_insert_col():
    table = Table(os.path.join(
        sample_dir, "hachijo_sightseeing.csv"))
    table = table.convert(
        convertor="insert_col",
        params={
            "output_attr_idx": "所在地",
            "output_attr_name": "都道府県名",
            "value": "東京都",
        },
    )

    with table.open() as csv:
        for lineno, row in enumerate(csv):
            assert len(row) == 8
            if lineno == 0:
                # 「所在地」の前に「都道府県名」が追加されていることを確認
                assert ",".join(row) == (
                    "観光スポット名称,都道府県名,所在地,緯度,経度,"
                    "座標系,説明,八丈町ホームページ記載")

            else:
                # 都道府県名欄に「東京都」が追加されていることを確認
                assert row[1] == "東京都"


def test_insert_cols():
    table = Table(os.path.join(
        sample_dir, "hachijo_sightseeing.csv"))
    table = table.convert(
        convertor="insert_cols",
        params={
            "output_attr_idx": "所在地",
            "output_attr_names": ["都道府県名", "市区町村名"],
             "values": ["東京都", "八丈町"],
        },
    )

    with table.open() as csv:
        for lineno, row in enumerate(csv):
            assert len(row) == 9
            if lineno == 0:
                # 「所在地」の前に「都道府県名」「市区町村名」が
                # 追加されていることを確認
                assert ",".join(row) == (
                    "観光スポット名称,都道府県名,市区町村名,所在地,"
                    "緯度,経度,座標系,説明,八丈町ホームページ記載")

            else:
                # 都道府県名欄に「東京都」が追加されていることを確認
                assert row[1] == "東京都"
                # 市区町村名に「八丈町」が追加されていることを確認
                assert row[2] == "八丈町"

def test_mapping_cols():
    table = Table(os.path.join(
        sample_dir, "ma030000.csv"))
    table = table.convert(
        convertor="mapping_cols",
        params={
            "column_map": {
                "都道府県": 0,
                "人口": "人口",
                "婚姻件数": "婚姻件数",
                "離婚件数": "離婚件数",
            },
        },
    )

    with table.open() as csv:
        for lineno, row in enumerate(csv):
            assert len(row) == 4
            if lineno == 0:
                # ヘッダを確認
                assert ",".join(row) == "都道府県,人口,婚姻件数,離婚件数"

            elif lineno == 4:
                # 列の値が正しくマップされていることを確認
                assert row == ["01 北海道", "5188441", "20904", "9070"]
                break


def test_move_col():
    table = Table(os.path.join(
        sample_dir, "hachijo_sightseeing.csv"))
    table = table.convert(
        convertor="move_col",
        params={
            "input_attr_idx": "経度",
            "output_attr_idx": "緯度"
        },
    )

    with table.open() as csv:
        for lineno, row in enumerate(csv):
            assert len(row) == 7
            if lineno == 0:
                # ヘッダの順番が「経度」「緯度」に入れ替わっていることを確認
                assert ",".join(row) == (
                    "観光スポット名称,所在地,経度,緯度,"
                    "座標系,説明,八丈町ホームページ記載")

            elif lineno == 1:
                # 緯度と経度が入れ替わっていることを確認
                assert row[2] == "139.80102"
                assert row[3] == "33.108218"


def test_rename_col():
    table = Table(os.path.join(sample_dir, "ma030000.csv"))
    table = table.convert(
        convertor="rename_col",
        params={
            "input_attr_idx": 0,
            "output_attr_name": "都道府県名",
        },
    )

    with table.open() as csv:
        for lineno, row in enumerate(csv):
            assert len(row) == 15
            if lineno == 0:
                # 0列目のヘッダが「都道府県名」に変更されていることを確認
                assert ",".join(row) == (
                    "都道府県名,人口,出生数,死亡数,（再掲）,,自　然,死産数,,,"
                    "周産期死亡数,,,婚姻件数,離婚件数")
