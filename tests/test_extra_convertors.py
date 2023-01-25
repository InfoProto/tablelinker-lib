import io
import os
import re
import sys

from tablelinker import Table

sample_dir = os.path.join(os.path.dirname(__file__), "../sample/")

Table.useExtraConvertors()


def test_to_seireki():
    # 気象庁「過去に発生した火山災害」より作成
    # https://www.data.jma.go.jp/vois/data/tokyo/STOCK/kaisetsu/volcano_disaster.htm
    stream = io.StringIO((
        "噴火年月日,火山名,犠牲者（人）,備考\n"
        "享保6年6月22日,浅間山,15,噴石による\n"
        "寛保元年8月29日,渡島大島,1467,岩屑なだれ・津波による\n"
        "明和元年7月,恵山,多数,噴気による\n"
        "安永8年11月8日,桜島,150余,噴石・溶岩流などによる「安永大噴火」\n"
        "天明元年4月11日,桜島,8、不明7,高免沖の島で噴火、津波による\n"
        "天明3年8月5日,浅間山,1151,火砕流、土石なだれ、吾妻川・利根川の洪水による\n"
        "天明5年4月18日,青ヶ島,130～140,当時327人の居住者のうち130～140名が死亡と推定され、残りは八丈島に避難\n"
        "寛政4年5月21日,雲仙岳,約15000,地震及び岩屑なだれによる「島原大変肥後迷惑」\n"
        "文政5年3月23日,有珠山,103,火砕流による\n"
        "天保12年5月23日,口永良部島,多数,噴火による、村落焼亡\n"
        "安政3年9月25日,北海道駒ヶ岳,19～27,噴石、火砕流による\n"
        "明治21年7月15日,磐梯山,461（477とも）,岩屑なだれにより村落埋没\n"
        "明治33年7月17日,安達太良山,72,火口の硫黄採掘所全壊\n"
        "明治35年8月上旬(7日～9日のいつか),伊豆鳥島,125,全島民死亡。\n"
        "大正3年1月12日,桜島,58～59,噴火・地震による「大正大噴火」\n"
        "大正15年5月24日,十勝岳,144（不明を含む）,融雪型火山泥流による「大正泥流」\n"
        "昭和15年7月12日,三宅島,11,火山弾・溶岩流などによる\n"
        "昭和27年9月24日,ベヨネース列岩,31,海底噴火（明神礁）、観測船第5海洋丸遭難により全員殉職\n"
        "昭和33年6月24日,阿蘇山,12,噴石による\n"
        "平成3年6月3日,雲仙岳,43（不明を含む）,火砕流による「平成3年(1991年)雲仙岳噴火」\n"
        "平成26年9月27日,御嶽山,63（不明を含む）,噴石等による\n"
    ))
    table = Table(stream)
    table = table.convert(
        convertor="to_seireki",
        params={
            "input_attr_idx": "噴火年月日",
            "output_attr_idx": 0,
            "overwrite": True,
        },
    )

    with table.open(as_dict=True) as dictreader:
        for lineno, row in enumerate(dictreader):
            assert len(row) == 4
            if lineno > 0:
                # 「噴火年月日」列は西暦に変換
                assert re.match(r'^[0-9]{4}', row["噴火年月日"])


def test_to_wareki():
    # 統計局「人口推計 / 長期時系列データ 長期時系列データ
    # （平成12年～令和２年）」より作成
    # https://www.e-stat.go.jp/stat-search/files?page=1&layout=datalist&toukei=00200524&tstat=000000090001&cycle=0&tclass1=000000090004&tclass2=000001051180&tclass3val=0
    stream = io.StringIO((
        "年次,総人口（千人）\n"
        "2000,126926\n"
        "2005,127768\n"
        "2010,128057\n"
        "2015,127095\n"
        "2020,126146\n"
    ))
    table = Table(stream)
    table = table.convert(
        convertor="to_wareki",
        params={
            "input_attr_idx": "年次",
            "output_attr_name": "和暦",
            "output_attr_idx": 1,
        },
    )

    with table.open(as_dict=True) as dictreader:
        for lineno, row in enumerate(dictreader):
            assert len(row) == 3
            if lineno == 0:
                assert ",".join(row) == "年次,和暦,総人口（千人）"
            elif int(row["年次"]) == 2019:
                assert re.match(r'^(平成|令和)', row["和暦"])
            elif int(row["年次"]) < 2019:
                assert re.match(r'^平成', row["和暦"])
            else:
                assert re.match(r'^令和', row["和暦"])


def test_geocoder_code():
    table = Table(os.path.join(sample_dir, "hachijo_sightseeing.csv"))
    table = table.convert(
        convertor="geocoder_code",
        params={
            "input_attr_idx": "所在地",
            "output_attr_name": "市区町村コード",
            "output_attr_idx": 0,
            "within": ["東京都"],
            "default": "0"
        }
    )

    with table.open() as csv:
        for lineno, row in enumerate(csv):
            assert len(row) == 8
            if lineno == 0:
                # ヘッダに「市区町村コード」が追加されていることを確認
                assert ",".join(row) == (
                    '市区町村コード,観光スポット名称,所在地,'
                    '緯度,経度,座標系,説明,八丈町ホームページ記載')
            elif row[2] == "":
                assert row[0] == "0"
            elif "八丈町" in row[2]:
                assert row[0] == "13401"  # 八丈町コード


def test_geocoder_prefecture():
    table = Table(os.path.join(sample_dir, "hachijo_sightseeing.csv"))
    table = table.convert(
        convertor="geocoder_prefecture",
        params={
            "input_attr_idx": "所在地",
            "output_attr_name": "都道府県名",
            "output_attr_idx": 0,
            "default": "東京都"
        }
    )

    with table.open() as csv:
        for lineno, row in enumerate(csv):
            assert len(row) == 8
            if lineno == 0:
                # ヘッダに「都道府県名」が追加されていることを確認
                assert ",".join(row) == (
                    '都道府県名,観光スポット名称,所在地,'
                    '緯度,経度,座標系,説明,八丈町ホームページ記載')
            else:
                assert row[0] == "東京都"


def test_geocoder_municipality():
    table = Table(os.path.join(sample_dir, "hachijo_sightseeing.csv"))
    table = table.convert(
        convertor="geocoder_municipality",
        params={
            "input_attr_idx": "所在地",
            "output_attr_name": "市区町村名",
            "output_attr_idx": 0,
            "within": ["東京都"],
            "default": "不明"
        }
    )

    with table.open() as csv:
        for lineno, row in enumerate(csv):
            assert len(row) == 8
            if lineno == 0:
                # ヘッダに「市区町村名」が追加されていることを確認
                assert ",".join(row) == (
                    '市区町村名,観光スポット名称,所在地,'
                    '緯度,経度,座標系,説明,八丈町ホームページ記載')
            elif row[2] == "":
                assert row[0] == "不明"
            else:
                assert row[0] == "八丈町"


def test_geocoder_latlong():
    table = Table(os.path.join(sample_dir, "hachijo_sightseeing.csv"))
    table = table.convert(
        convertor="geocoder_latlong",
        params={
            "input_attr_idx": "所在地",
            "output_attr_names": ["緯度", "経度", "レベル"],
            "output_attr_idx": "説明",
            "within": ["東京都"],
            "default": "",
        }
    )

    with table.open() as csv:
        for lineno, row in enumerate(csv):
            assert len(row) == 8
            if lineno == 0:
                # ヘッダの「説明」列の前に「緯度」「経度」「レベル」列が
                # 追加されていることを確認
                assert ",".join(row) == (
                    "観光スポット名称,所在地,座標系,"
                    "緯度,経度,レベル,説明,八丈町ホームページ記載")
            elif row[1] == "":
                assert row[5] == ""
            else:
                assert int(row[5]) >= 3  # 町以上まで一致している


