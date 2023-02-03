from abc import ABC
from logging import getLogger

from . import params

logger = getLogger(__name__)


class ConvertorMeta(object):
    def __init__(self, meta):
        self.key = meta.key
        self.name = meta.name
        self.description = meta.description
        self.message = getattr(
            meta, "message", getattr(meta, "description", ""))
        self.help_text = meta.help_text
        self.params = meta.params

    @property
    def input_params(self):
        return [
            param for param in self.params
            if param.Meta.type == "input-attribute"
        ]

    @property
    def output_params(self):
        return [
            param for param in self.params
            if param.Meta.type == "output-attribute"
        ]


class Convertor(ABC):
    """
    変換処理
    """

    @classmethod
    def meta(cls):
        return ConvertorMeta(cls.Meta)

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
                        context._convertor_params[key] = idx
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
                                context._convertor_params[key][i] = idx
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

                    context._convertor_params[key] = idx
                elif isinstance(val, list):
                    for i, v in enumerate(val):
                        if isinstance(v, str):
                            try:
                                idx = headers.index(v)
                            except ValueError:
                                idx = len(headers)
                                headers.append(v)

                            context._convertor_params[key][i] = idx

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
            logger.warning(
                "num_of_columns: {:d} but record has {:d} fields.".format(
                    context.get_data("num_of_columns"),
                    len(record)))
            return False
        else:
            return True

    def process_record(self, record, context):
        context.output(record)

    @classmethod
    def can_apply(cls, attrs):
        """
        対象の属性がこのコンバータに適用可能かどうかを返します。
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


class InputOutputConvertor(Convertor):
    @classmethod
    def meta(cls):
        _meta = ConvertorMeta(cls.Meta)
        _meta.params = params.ParamSet(
            [
                params.InputAttributeParam(
                    "input_attr_idx",
                    label="入力列",
                    description="処理をする対象の列",
                    required=True),
                params.OutputAttributeParam(
                    "output_attr_name",
                    label="出力列名",
                    description="変換結果を出力する列名です。",
                    help_text="空もしくは既存の名前が指定された場合、置換となります。",
                    required=False,
                ),
                params.AttributeParam(
                    "output_attr_idx",
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
        対象の属性がこのコンバータに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        if len(attrs) != 1:
            return False
        return True

    def initial_context(self, context):
        super().initial_context(context)
        self.input_attr_idx = context.get_param("input_attr_idx")
        self.output_attr_idx = context.get_param("output_attr_idx")
        self.output_attr_name = context.get_param("output_attr_name")
        self.overwrite = context.get_param("overwrite")

    def process_header(self, header, context):
        if self.output_attr_name is None:
            # 出力列名が指定されていない場合は既存列名を利用する
            self.output_attr_name = header[self.input_attr_idx]
            self.del_attr = self.input_attr_idx
        else:
            # 出力列名が存在するかどうか調べる
            try:
                idx = header.index(self.output_attr_name)
                self.del_attr = idx
            except ValueError:
                # 存在しない場合は新規列
                self.del_attr = None
                self.overwrite = True

        if self.output_attr_idx is None:
            # 出力列番号が指定されていない場合は末尾に追加
            self.output_attr_idx = len(header)

        header = self.reorder(
            original=header,
            del_idx=self.del_attr,
            insert_idx=self.output_attr_idx,
            insert_value=self.output_attr_name)

        context.output(header)

    def process_record(self, record, context):
        need_value = False
        if self.overwrite:
            need_value = True
        else:
            # 置き換える列に空欄があるかどうか
            if self.del_attr >= len(record) or \
                    record[self.del_attr] == "":
                need_value = True

        if need_value:
            value = self.process_convertor(record, context)
            if value is False:
                # コンバータの process_convertor で False を返す行はスキップされる
                return

        else:
            value = record[self.del_attr]

        record = self.reorder(
            original=record,
            del_idx=self.del_attr,
            insert_idx=self.output_attr_idx,
            insert_value=value)

        context.output(record)

    def process_convertor(self, record, context):
        return record[self.input_attr_idx]

    def reorder(self, original, del_idx, insert_idx, insert_value):
        new_list = original[:]
        if del_idx is not None:
            new_list.pop(del_idx)
            if del_idx < insert_idx:
                insert_idx -= 1

        new_list.insert(insert_idx, insert_value)
        return new_list


class InputOutputsConvertor(Convertor):
    """
    入力列が1, 出力列が複数のコンバータの基底クラス
    """

    @classmethod
    def meta(cls):
        _meta = ConvertorMeta(cls.Meta)
        _meta.params = params.ParamSet(
            [
                params.InputAttributeParam(
                    "input_attr_idx",
                    label="入力列",
                    description="処理をする対象の列",
                    required=True),
                params.OutputAttributeListParam(
                    "output_attr_names",
                    label="出力列名のリスト",
                    description="変換結果を出力する列名のリストです。",
                    help_text="既存の列名が指定された場合、置換となります。",
                    required=False,
                    default_value=[],
                ),
                params.AttributeParam(
                    "output_attr_idx",
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
        対象の属性がこのコンバータに適用可能かどうかを返します。
        attrs: 属性のリスト({name, attr_type, data_type})
        """
        if len(attrs) != 1:
            return False
        return True

    def initial_context(self, context):
        super().initial_context(context)
        self.old_attr_indexes = []
        self.del_attr_indexes = []
        self.input_attr_idx = context.get_param("input_attr_idx")
        self.output_attr_idx = context.get_param("output_attr_idx")
        self.output_attr_names = context.get_param("output_attr_names")

    def process_header(self, header, context):
        # 既存列をチェック
        for output_attr_name in self.output_attr_names:
            if output_attr_name in header:
                idx = header.index(output_attr_name)
                self.old_attr_indexes.append(idx)
            else:
                self.old_attr_indexes.append(None)

        # 挿入する位置
        if self.output_attr_idx is None or \
                self.output_attr_idx >= len(header):  # 末尾
            self.output_attr_idx = len(header)

        # 列を一つずつ削除した場合に正しい列番号になるよう調整
        self.del_attr_indexes = self.old_attr_indexes[:]
        for i, del_index in enumerate(self.del_attr_indexes):
            if del_index is None:
                continue

            if del_index < self.output_attr_idx:
                self.output_attr_idx -= 1

            for j, d in enumerate(self.del_attr_indexes[i + 1:]):
                if d is not None and del_index < d:
                    self.del_attr_indexes[i + j + 1] -= 1

        header = self.reorder(
            original=header,
            delete_idxs=self.del_attr_indexes,
            insert_idx=self.output_attr_idx,
            insert_values=self.output_attr_names
        )
        context.output(header)

    def process_record(self, record, context):
        old_values = []
        for idx in self.old_attr_indexes:
            if idx is None:
                old_values.append("")
            else:
                old_values.append(record[idx])

        if context.get_param("overwrite"):
            new_values = self.process_convertor(
                record, context)
        else:
            values = None
            new_values = []
            for i, old_value in enumerate(old_values):
                if old_value == "":
                    if values is None:
                        values = self.process_convertor(
                            record, context)

                    new_values.append(values[i])
                else:
                    new_values.append(old_value)

        record = self.reorder(
            original=record,
            delete_idxs=self.del_attr_indexes,
            insert_idx=self.output_attr_idx,
            insert_values=new_values)
        context.output(record)

    def process_convertor(self, record, context):
        return record[self.input_attr_idx]

    def reorder(self, original, delete_idxs, insert_idx, insert_values):
        """
        列の削除と追加を行う。

        Parameters
        ----------
        original: list[str]
            入力行。
        delete_idxs: list[(int, None)]
            削除する列番号、 None の場合は削除しない。
        insert_idx: int
            追加する列番号
        insert_values: list[str]
            追加する文字列のリスト
        """
        new_list = original[:]
        for delete_idx in delete_idxs:
            if delete_idx is None:
                continue

            del new_list[delete_idx]

        new_list = new_list[0:insert_idx] + insert_values \
            + new_list[insert_idx:]

        return new_list


class NoopConvertor(Convertor):
    """
    何もしない
    """

    class Meta:
        key = "noop"
        name = "何もしません"
        description = None
        help_text = None
        params = params.ParamSet()


class AttrCopyConvertor(InputOutputConvertor):
    """
    列コピー
    """

    class Meta:
        key = "acopy"
        name = "列のコピー"
        description = "列をコピーします"
        help_text = None
        params = params.ParamSet()


CONVERTORS = [AttrCopyConvertor]
CONVERTOR_DICT = {}
for f in CONVERTORS:
    CONVERTOR_DICT[f.key()] = f


def registry_convertor(convertor, selectable=True):
    """
    コンバータを登録します。
    convertor: コンバータクラス
    selectable: ユーザが選択可能なコンバータかどうか
    """
    if selectable:
        CONVERTORS.append(convertor)
    CONVERTOR_DICT[convertor.key()] = convertor


def convertor_find_by(name):
    return CONVERTOR_DICT.get(name)


def convertor_all():
    return [f for f in CONVERTORS]


def convertor_meta_list(attrs=[]):
    """
    適用可能なコンバータのメタ情報を取得します。
    """
    _attrs = attrs if attrs is not None else []
    return [
        convertor.meta() for convertor in convertor_all()
        if convertor.can_apply(_attrs)
    ]


def convertor_keys():
    return [f.Meta.key for f in CONVERTORS]


def encode_convertor(convertor):
    return [convertor.key()]


def decode_convertor(convertor):
    return convertor_find_by(convertor[0])()
