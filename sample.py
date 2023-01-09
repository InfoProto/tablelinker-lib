from logging import getLogger

from tablelinker import Table

logger = getLogger(__name__)


if __name__ == '__main__':
    import logging
    logging.basicConfig(level=logging.DEBUG)

    csv_path = "sakurai_sightseeing_spots.csv"
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
    table.save(out_path)
