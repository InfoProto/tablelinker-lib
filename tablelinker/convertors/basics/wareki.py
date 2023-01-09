import re

from ..core import filters, params
from jeraconv import jeraconv


def wareki2seireki(value):
    """
    和暦西暦変換
    value: 文字列
    """
    j2w = jeraconv.J2W()

    targets = re.findall(r"明治\d?\d年|大正\d?\d年|昭和\d?\d年|平成\d?\d年|令和\d?\d年", value)

    result = str(value)
    for target in targets:
        result = result.replace(target, "{}年".format(j2w.convert(target)))

    return result


class ToSeirekiFilter(filters.InputOutputFilter):
    """
    和暦を西暦に変換するフィルターです。
    """

    class Meta:
        key = "wareki2seireki"
        name = "和暦西暦変換"
        description = """
        和暦を西暦に変換します
        """
        help_text = None
        params = params.ParamSet()

    def process_filter(self, output_attr_name, record, context):
        return wareki2seireki(record[output_attr_name])
