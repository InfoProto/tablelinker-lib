from abc import ABC
from . import params


class FilterMeta(object):
    def __init__(self, meta):
        self.key = meta.key
        self.name = meta.name
        self.description = meta.description
        self.message = meta.message if hasattr(meta, "message") else meta.description or ""
        self.help_text = meta.help_text
        self.params = meta.params

    @property
    def input_params(self):
        return [param for param in self.params if param.Meta.type == "input-attribute"]

    @property
    def output_params(self):
        return [param for param in self.params if param.Meta.type == "output-attribute"]


class Filter(ABC):
    """
    変換処理
    """

    @classmethod
    def meta(cls):
        return FilterMeta(cls.Meta)

    @classmethod
    def key(cls):
        return cls.meta().key

    @property
    def params(self):
        return self.__class__.meta().params

    def process(self, context):
        self.initial_context(context)
        self.initial(context)

        # 念のため先頭に戻し、2行目から処理する
        context.reset()
        context.next()

        self.process_header(context.get_data('headers'), context)
        for record in context.read():
            if not self.check_process_record(record, context):
                continue
            self.process_record(record, context)

    def initial_context(self, context):
        """
        パラメータの前処理と、ヘッダ情報の登録を行う。
        """
        headers = context.next()
        context.set_data("num_of_columns", len(headers))  # 入力データ列数

        # 入出力列番号に列名が指定された場合、列番号に変換する
        for key in context.get_params():
            if key.startswith('input_attr_idx'):
                val = context.get_param(key)
                if isinstance(val, str):
                    try:
                        idx = headers.index(val)
                        context._filter_params[key] = idx
                    except ValueError:
                        raise RuntimeError((
                            "パラメータ '{}' で指定された列 '{}' は"
                            "有効な列名ではありません。有効な列名は次の通り; {}"
                        ).format(key, val, ",".join(headers)))
                elif isinstance(val, list):
                    for i, v in enumerate(val):
                        if isinstance(v, str):
                            try:
                                idx = headers.index(v)
                                context._filter_params[key][i] = idx
                            except ValueError:
                                raise RuntimeError((
                                    "パラメータ '{}' の {} 番目で指定された列 '{}' は"
                                    "有効な列名ではありません。有効な列名は次の通り; {}"
                                ).format(key, i + 1, v, ",".join(headers)))

            if key.startswith('output_attr_idx'):
                val = context.get_param(key)
                if isinstance(val, str):
                    try:
                        idx = headers.index(val)
                    except ValueError:
                        idx = len(headers)

                    context._filter_params[key] = idx
                elif isinstance(val, list):
                    for i, v in enumerate(val):
                        if isinstance(v, str):
                            try:
                                idx = headers.index(v)
                            except ValueError:
                                idx = len(headers)
                                headers.append(v)

                            context._filter_params[key][i] = idx

        context.set_data("headers", headers)

    def initial(self, context):
        pass

    def process_header(self, headers, context):
        context.output(headers)

    def check_process_record(self, record, context):
        """
        入力するレコードへのチェックを行います。
        :return: boolean
        """
        if context.get_data("num_of_columns") != len(record):
            return False
        else:
            return True

    def process_record(self, record, context):
        context.output(record)

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        return True

    @classmethod
    def get_message(cls, params):
        """
        変換時に追加するメッセージを生成します。
        params: パラメータのリストです。
        """
        return cls.meta().message.format(**params)


class InputOutputFilter(Filter):
    @classmethod
    def meta(cls):
        _meta = FilterMeta(cls.Meta)
        _meta.params = params.ParamSet(
            [
                params.InputAttributeParam("input_attr_idx", label="入力列", description="処理をする対象の列", required=True),
                params.OutputAttributeParam(
                    "output_attr_name",
                    label="出力列名",
                    description="変換結果を出力する列名です。",
                    help_text="空もしくは既存の名前が指定された場合、置換となります。",
                    required=False,
                ),
                params.AttributeParam(
                    "output_attr_new_index",
                    label="出力列の位置",
                    description="新しい列の挿入位置です。",
                    label_suffix="の後",
                    empty=True,
                    empty_label="先頭",
                    required=False,
                ),
                params.BooleanParam(
                    "overwrite",
                    label="上書き",
                    description="既に値が存在する場合に上書きするか指定します。",
                    default_value=False,
                    required=False)
            ]
            + _meta.params.params()
        )
        return _meta

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        if len(attrs) != 1:
            return False
        return True

    def initial(self, context):
        self.output_attr_index = None
        self.new_attr = None
        self.overwrite = None

    def process_header(self, header, context):
        output_attr_name = context.get_param("output_attr_name")
        input_attr_idx = context.get_param("input_attr_idx")
        self.overwrite = context.get_param("overwrite")

        if output_attr_name is None:
            # Noneの場合は既存列を置換する
            self.output_attr_index = input_attr_idx
            self.overwrite = True
            self.new_attr = False
        else:
            # 既存列か調べる
            try:
                self.output_attr_index = header.index(output_attr_name)
                self.new_attr = False
            except ValueError:
                # 新規列の追加
                self.output_attr_index = len(header)
                self.new_attr = True
                header.append(output_attr_name)

        # 移動
        output_attr_new_index = context.get_param("output_attr_new_index")
        if output_attr_new_index is not None:
            # 指定位置へ
            header.insert(output_attr_new_index, header.pop(self.output_attr_index))

        context.output(header)

    def process_record(self, record, context):
        input_attr_idx = context.get_param("input_attr_idx")

        if self.output_attr_index < len(record):
            if self.overwrite or \
                    record[self.output_attr_index] == "":
                value = self.process_filter(input_attr_idx, record, context)
                record[self.output_attr_index] = value
            else:
                # 値が存在する場合は上書きしない
                pass
        else:
            value = self.process_filter(input_attr_idx, record, context)
            record.insert(self.output_attr_index, value)

        # 移動
        output_attr_new_index = context.get_param("output_attr_new_index")
        if output_attr_new_index is not None:
            # 指定位置へ
            record.insert(output_attr_new_index, record.pop(self.output_attr_index))

        context.output(record)

    def process_filter(self, input_attr_idx, record, context):
        return record[input_attr_idx]


class InputOutputsFilter(Filter):
    """
    入力列が1, 出力列が複数のフィルタの基底クラス
    """

    @classmethod
    def meta(cls):
        _meta = FilterMeta(cls.Meta)
        _meta.params = params.ParamSet(
            [
                params.InputAttributeParam("input_attr_idx", label="入力列", description="処理をする対象の列", required=True),
                params.OutputAttributeListParam(
                    "output_attr_names",
                    label="出力列名のリスト",
                    description="変換結果を出力する列名のリストです。",
                    help_text="既存の列名が指定された場合、置換となります。",
                    required=True,
                ),
                params.AttributeParam(
                    "output_attr_new_index",
                    label="出力列の位置",
                    description="新しい列の挿入位置です。",
                    label_suffix="の後",
                    empty=True,
                    empty_label="先頭",
                    required=False,
                ),
                params.BooleanParam(
                    "overwrite",
                    label="上書き",
                    description="既に値が存在する場合に上書きするか指定します。",
                    default_value=False,
                    required=False
                ),
            ]
            + _meta.params.params()
        )
        return _meta

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのフィルタに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        if len(attrs) != 1:
            return False
        return True

    def initial(self, context):
        self.del_attr_indexes = []
        self.new_attr = None
        self.input_attr_idx = None

    def process_header(self, header, context):
        output_attr_names = context.get_param("output_attr_names")
        self.input_attr_idx = context.get_param("input_attr_idx")

        # 既存列は削除
        for output_attr_name in output_attr_names:
            if output_attr_name in header:
                idx = header.index(output_attr_name)
                self.del_attr_indexes.append(idx)
                del header[idx]
            else:
                self.del_attr_indexes.append(None)

        # 指定列に挿入
        output_attr_new_index = context.get_param("output_attr_new_index")
        if output_attr_new_index is None or \
                output_attr_new_index >= len(header):  # 末尾
            header = header + output_attr_names
        else:  # 指定位置
            header = header[0:output_attr_new_index] + \
                output_attr_names + \
                header[output_attr_new_index:]

        context.output(header)

    def process_record(self, record, context):
        values = self.process_filter(self.input_attr_idx, record, context)

        old_values = []
        for idx in self.del_attr_indexes:
            if idx is None:
                old_values.append("")
            else:
                old_values.append(record[idx])
                del record[idx]

        if context.get_param("overwrite"):
            new_values = values
        else:
            new_values = []
            for i, old_value in enumerate(old_values):
                if old_value == "":
                    new_values.append(values[i])
                else:
                    new_values.append(old_value)

        # 指定列に挿入
        output_attr_new_index = context.get_param("output_attr_new_index")
        if output_attr_new_index is None or \
                output_attr_new_index >= len(record):  # 末尾
            record = record + new_values
        else:  # 指定位置
            record = record[0:output_attr_new_index] + \
                new_values + record[output_attr_new_index:]

        context.output(record)

    def process_filter(self, input_attr_idx, record, context):
        return record[input_attr_idx]


class NoopFilter(Filter):
    """
    何もしない
    """

    class Meta:
        key = "noop"
        name = "何もしません"
        description = None
        help_text = None
        params = params.ParamSet()


class AttrCopyFilter(InputOutputFilter):
    """
    列コピー
    """

    class Meta:
        key = "acopy"
        name = "列のコピー"
        description = "列をコピーします"
        help_text = None
        params = params.ParamSet()


FILTERS = [AttrCopyFilter]
FILTER_DICT = {}
for f in FILTERS:
    FILTER_DICT[f.key()] = f


def registry_filter(filter, selectable=True):
    """
    フィルタを登録します。
    filter: フィルタクラス
    selectable: ユーザが選択可能なフィルターかどうか
    """
    if selectable:
        FILTERS.append(filter)
    FILTER_DICT[filter.key()] = filter


def filter_find_by(name):
    return FILTER_DICT.get(name)


def filter_all():
    return [f for f in FILTERS]


def filter_meta_list(attrs=[]):
    """
    適用可能なフィルタのメタ情報を取得します。
    """
    _attrs = attrs if attrs is not None else []
    return [filter.meta() for filter in filter_all() if filter.can_apply(_attrs)]


def filter_keys():
    return [f.Meta.key for f in FILTERS]


def encode_filter(filter):
    return [filter.key()]


def decode_filter(filter):
    return filter_find_by(filter[0])()
