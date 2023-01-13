from ..core import filters, params


def to_harf_number(value):
    """
    全角数字を半角数字に変換します。
    value: 文字列
    """
    return value.translate(
        str.maketrans({"１": "1", "２": "2", "３": "3", "４": "4", "５": "5",
                       "６": "6", "７": "7", "８": "8", "９": "9", "０": "0"})
    )


def to_harf_symbol(value):
    """
    全角記号を半角記号に変換します
    value: 文字列
    """
    return value.translate(
        str.maketrans(
            {
                "＂": '"',
                "＼": "\\",
                "！": "!",
                "＃": "#",
                "＄": "$",
                "％": "%",
                "＆": "&",
                "＇": "'",
                "（": "(",
                "）": ")",
                "＊": "*",
                "＋": "+",
                "，": ",",
                "－": "-",
                "．": ".",
                "／": "/",
                "：": ":",
                "；": ";",
                "＜": "<",
                "＝": "=",
                "＞": ">",
                "？": "?",
                "＠": "@",
                "［": "[",
                "］": "]",
                "＾": "^",
                "＿": "_",
                "｀": "`",
                "｛": "{",
                "｜": "|",
                "｝": "}",
                "～": "~",
            }
        )
    )


def to_whole_symbol(value):
    """
    半角記号を全角記号に変換します。
    value: 文字列
    """
    return value.translate(
        str.maketrans(
            {
                '"': "＂",
                "\\": "＼",
                "!": "！",
                "#": "＃",
                "$": "＄",
                "%": "％",
                "&": "＆",
                "'": "＇",
                "(": "（",
                ")": "）",
                "*": "＊",
                "+": "＋",
                ",": "，",
                "-": "－",
                ".": "．",
                "/": "／",
                ":": "：",
                ";": "；",
                "<": "＜",
                "=": "＝",
                ">": "＞",
                "?": "？",
                "@": "＠",
                "[": "［",
                "]": "］",
                "^": "＾",
                "_": "＿",
                "`": "｀",
                "{": "｛",
                "|": "｜",
                "}": "｝",
                "~": "～",
            }
        )
    )


def to_harf_alphanumeric(value):
    """
    全角英数字記号を半角英数字記号に変換します
    value: 文字列
    """
    return value.translate(str.maketrans({chr(0xFF01 + i): chr(0x21 + i) for i in range(94)}))


def to_whole_alphanumeric(value):
    """
    半角英数字記号を全角英数字記号に変換します
    value: 文字列
    """
    return value.translate(str.maketrans({chr(0x0021 + i): chr(0xFF01 + i) for i in range(94)}))


class ToHarfNumberFilter(filters.InputOutputFilter):

    """
    全角数字を半角数字に変換するフィルターです。
    """

    class Meta:
        key = "to_harf_number"
        name = "数字（全角→半角）変換"
        description = """
          全角数字を半角数字に変換します
          """
        help_text = None
        params = params.ParamSet()

    def process_filter(self, input_attr_idx, record, context):
        return to_harf_number(record[input_attr_idx])


class ToHarfSymbolFilter(filters.InputOutputFilter):
    class Meta:
        key = "to_harf_symbol"
        name = "全角記号（全角→半角）変換"
        description = """
        全角記号を半角記号に変換します
        """
        help_text = None
        params = params.ParamSet()

    def process_filter(self, output_attr_name, record, context):
        return to_harf_symbol(record[output_attr_name])


class ToWholeSymbolFilter(filters.InputOutputFilter):
    """
    半角記号を全角記号に変換するフィルターです。
    """

    class Meta:
        key = "to_whole_symbol"
        name = "半角記号（半角→全角）変換"
        description = """
        半角記号を全角記号に変換します
        """
        help_text = None
        params = params.ParamSet()

    def process_filter(self, output_attr_name, record, context):
        return to_whole_symbol(record[output_attr_name])


class ToHarfAlphanumericFilter(filters.InputOutputFilter):
    class Meta:
        key = "to_harf_alphanumeric"
        name = "全角英数字記号（全角→半角）変換"
        description = """
        全角英数字記号を半角英数字記号に変換します
        """
        help_text = None
        params = params.ParamSet()

    def process_filter(self, output_attr_name, record, context):
        return to_harf_alphanumeric(record[output_attr_name])


class ToWholeAlphanumericFilter(filters.InputOutputFilter):
    """
    半角英数字記号を全角英数字記号に変換するフィルターです。
    """

    class Meta:
        key = "to_whole_alphanumeric"
        name = "半角英数字記号（半角→全角）変換"
        description = """
        半角英数字記号を全角英数字記号に変換します
        """
        help_text = None
        params = params.ParamSet()

    def process_filter(self, output_attr_name, record, context):
        return to_whole_alphanumeric(record[output_attr_name])
