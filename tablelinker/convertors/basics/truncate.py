from ..core import filters, params, validators


def truncate(string, length, omission="..."):
    """文字列を切り詰める

    string: 対象の文字列
    length: 切り詰め後の長さ
    ellipsis: 省略記号
    """
    return string[:length] + (omission if string[length:] else "")


class TruncateFilter(filters.InputOutputFilter):
    """
    長い文字を省略して表示
    """

    class Meta:
        key = "truncate"
        name = "文字列を短くする"
        description = "文字列を指定された文字数で切り取ります"
        help_text = None
        params = params.ParamSet(
            params.IntParam(
                "length",
                label="長さ",
                required=True,
                validators=(validators.IntValidator(), validators.RangeValidator(min=1, max=100),),
                default_value="10",
            ),
            params.StringParam("omission", label="省略文字", default_value="…"),
        )

    def process_filter(self, input_attr_idx, record, context):
        length = context.get_param("length")
        omission = context.get_param("omission")
        return truncate(record[input_attr_idx], length, omission=omission)
