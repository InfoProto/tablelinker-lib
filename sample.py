from logging import getLogger

from tablelinker import Table

logger = getLogger(__name__)


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.WARNING)

    # 利用するコンバータを登録
    import tablelinker.convertors.basics as basic_convertors
    import tablelinker.convertors.extras as extra_convertors
    basic_convertors.register()
    extra_convertors.register()

    # 入力 CSV は Shift_JIS
    csv_path = "sample/sakurai_sightseeing_spots_sjis.csv"
    out_path = "output.csv"

    table = Table(csv_path)

    table = table.convert(
        'geocoder_code', {
            "input_attr_idx": "住所",
            "output_attr_name": "都道府県コード又は市区町村コード",
            "withCheckDigit": False,
            "output_attr_new_index": 1,
        })
    table = table.convert(
        'geocoder_latlong', {
            "input_attr_idx": "住所",
            "output_attr_names": ["緯度", "経度", "ジオコーディングレベル"],
            "overwrite": False,
        })
    table = table.convert(
        'mapping_cols', {
            "column_list": [  # 推奨データセット - 観光
                '都道府県コード又は市区町村コード', 'NO', '都道府県名',
                '市区町村名', '名称', '名称_カナ', '名称_英語',
                'POIコード', '住所', '方書', '緯度', '経度',
                '利用可能曜日', '開始時間', '終了時間', '利用可能日時特記事項',
                '料金（基本）', '料金（詳細）', '説明', '説明_英語',
                'アクセス方法', '駐車場情報', 'バリアフリー情報',
                '連絡先名称', '連絡先電話番号', '連絡先内線番号',
                '画像', '画像_ライセンス', 'URL', '備考']
        })

    table.save(out_path)  # encoding はデフォルトで UTF-8

    # Pandas DataFrame を利用して JSON にエクスポート
    table.toPandas().to_json(
        "output.json", orient="records", indent=2, force_ascii=False)
