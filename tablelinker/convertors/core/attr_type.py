from datetime import datetime
from logging import getLogger
import re

from .convertors.core.types import AttrType

logger = getLogger(__name__)


class AttrTypeResolver(object):
    """
    意味型を分析するクラスです。

    Notes
    -----
    意味型のリストは converters.core.types で定義されています。
    """

    column_name_map = None

    def __init__(self, dataset_attr, threshold=None):
        """コンストラクタ

        Args:
            dataset_attr (datasets.models.DatasetAttr): DetasetAttrのインスタンス
            threshold (float)): しきい値
        """
        self.attr_types = AttrType.choices()
        self.dataset_attr = dataset_attr
        self.dataset = dataset_attr.dataset
        self.threshold = threshold if threshold is not None else 0.99
        self.counter = self.__setup_counter()
        self.collector = self.__setup_collector()
        self.mtab_result = None

        # mtab
        self.column_cta_wikidata_id = None
        self.mtab_attr_type_key = None
        self.wikidata_map = settings.WIKIDATA_MAP
        # self.mtab_result = self.__setup_mtab_result()
        self.mtab_result = None  # 一時的に disabled
        if self.mtab_result is not None:
            wikidata_uri = "http://www.wikidata.org/entity/"
            column_index = self.dataset_attr.index
            if self.mtab_result.cta_data:
                # cta_dataが存在する場合のみ保存する
                self.column_cta_data_annotations = next(
                    (cta_data["annotation"]
                     for cta_data in self.mtab_result.cta_data if cta_data["target"] == column_index), []
                )
            # TODO annotationがあると、画面がエラー表示されるので一時的にコメントアウト
            # if len(self.column_cta_data_annotations) > 0:
            #     column_cta_wikidata_uri = self.column_cta_data_annotations[0]["wikidata"].replace(wikidata_uri, "")
            #     self.column_cta_wikidata_id = column_cta_wikidata_uri.replace(wikidata_uri, "")
            #     self.mtab_attr_type_key = (
            #         self.wikidata_map[self.column_cta_wikidata_id] if self.column_cta_wikidata_id in self.wikidata_map else None
            #     )

        # COLUMN_NAME
        if self.__class__.column_name_map is None:
            self.__class__.column_name_map = []
            for k, v in settings.COLUMN_NAME_MAP.items():
                self.__class__.column_name_map.append([re.compile(k), v])

        self.column_name_attr_type_key = None
        for pattern_value in self.column_name_map:
            if pattern_value[0].match(self.dataset_attr.name):
                self.column_name_attr_type_key = pattern_value[1]

    def append(self, record, index):
        """
        型判定に必要なデータを追加します。
        """
        if index < len(record):
            value = record[index]
            attr_type_key = self.__resolve_type(value, index)
            self.__count(value, attr_type_key)
            self.__collect(value, attr_type_key)

    def resolve(self):
        attr_type = self.__analyze()
        if attr_type:
            self.dataset_attr.attr_type = attr_type[0]
        self.dataset_attr.save()
        return self.dataset_attr.attr_type

    def __setup_counter(self):
        """
        属性を判定するカウンターをセットします。
        """
        counter = {}
        for attr_type in self.attr_types:
            counter[attr_type[0]] = 0
        return counter

    def __setup_collector(self):
        """
        データの値を判定するコレクターをセットアップします。
        """
        collector = {}
        for attr_type in self.attr_types:
            collector[attr_type[0]] = set()
        return collector

    def __setup_mtab_result(self):
        if self.dataset.mtab_file and self.dataset.mtab_file.size > 0:
            mtab_result = MTabResult()
            mtab_result.analyze(self.dataset.mtab_file)
            return mtab_result
        else:
            return {}

    def __count(self, value, attr_type_key):
        """
        判定された型をカウントします。
        """
        self.counter[attr_type_key] += 1

    def __collect(self, value, attr_type_key):
        """
        判定された型を収集します。
        """
        self.collector[attr_type_key].add(value)

    def __resolve_type(self, value, index):
        """
        型の判定をします。

        各情報へのアクセス方法
        self.dataset_attr #解析対象の属性
        self.dataset #解析対象のデータセット
        self.dataset.attr_set # 解析対象のデータセットの全属性

        """
        attr_type = None
        if is_organizaion(value):
            attr_type = "organization"  # organizaion: 組織
        elif is_area(value):
            attr_type = "area"  # area: 面積
        elif is_price(value):
            attr_type = "price"  # price: 価格
        elif is_datetime(value):
            attr_type = "datetime"  # datetime: 日時
        elif is_date(value):
            attr_type = "date"  # date: 日付

        if attr_type is None:
            attr_type = "unknown"

        return attr_type

    def __analyze(self):
        """
        判定された型の数を分析して型を決定します。
        """
        attr_type_key = 'unknown'

        total = sum(self.counter.values())
        if total > 0:
            # しきい値を超える型がある場合、その型に決定する
            for key, value in self.counter.items():
                if (value / total) >= self.threshold:
                    attr_type_key = key
                    continue

        # mtbによる解析
        if attr_type_key == 'unknown' and self.mtab_attr_type_key is not None:
            attr_type_key = self.mtab_attr_type_key

        # カラム名による解析
        if attr_type_key == 'unknown' and self.column_name_attr_type_key is not None:
            attr_type_key = self.column_name_attr_type_key

        for attr in self.attr_types:
            if attr[0] == attr_type_key:
                return attr

        return None


def is_organizaion(value):
    return re.match("株式会社.*", value) or re.match(".*株式会社", value)


def is_area(value):
    return re.match(".*m2", value)


def is_price(value):
    return re.match("¥.*", value) or re.match(".*円", value)


DATE_FORMATS = [
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%Y年%m月%d日",
]


def is_date(value):
    for datetime_format in DATE_FORMATS:
        try:
            datetime.strptime(value, datetime_format)
            return True
        except ValueError:
            pass
    return False


DATETIME_FORMATS = [
    "%Y/%m/%d %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y/%m/%d %H:%M",
    "%Y-%m-%d %H:%M",
    "%Y年%m月%d日 *%H時%M分",
    "%Y年%m月%d日 *%H時%M分%S秒",
]


def is_datetime(value):
    for datetime_format in DATETIME_FORMATS:
        try:
            datetime.strptime(value, datetime_format)
            return True
        except ValueError:
            pass
    return False
