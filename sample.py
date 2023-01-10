from logging import getLogger
import sys

from tablelinker import Table

logger = getLogger(__name__)


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.WARNING)

    # 入力 CSV は Shift_JIS
    csv_path = "sample/sakurai_sightseeing_spots_sjis.csv"
    out_path = "output.csv"

    table = Table(csv_path)

    table = table.convert(
        'rename_col', {
            "input_attr_idx": "NO",
            "new_col_name": "番号",
        })
    table = table.convert(
        'geocoder_code', {
            "input_attr_idx": "住所",
            "output_attr_name": "5桁コード",
            "withCheckDigit": False,
            "output_attr_new_index": 0,
        })
    table.save(out_path)  # encoding はデフォルトで UTF-8

    # Pandas DataFrame を利用して JSON にエクスポート
    table.toPandas().to_json(
        "output.json", orient="records", indent=2, force_ascii=False)
