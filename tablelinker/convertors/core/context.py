from logging import getLogger

# from .validators import Errors

logger = getLogger(__name__)


class Context(object):
    """
    コンテキスト
    """

    def __init__(self, convertor, convertor_params, input, output, proxy=None):
        """
        Parameters
        ----------
        convertor: Convertor
            The convertor class to be used in this context.
        convertor_params: dict[Param, Any]
            The pairs of parameter name and its value.
        input: InputCollection
            The input source of this context.
        output: OutputCollection
            The output source of this context.
        """
        self._convertor = convertor
        self._input = input
        self._output = output
        self._convertor_params = convertor_params
        self._current = None
        self._data = {}

        # Check parameters
        convertor_meta = self._convertor.meta()
        declared_params = convertor_meta.params
        convertor_key = convertor_meta.key

        for key in self._convertor_params.keys():
            if key in declared_params:
                continue

            msg = ("コンバータ '{}' ではパラメータ '{}' は"
                   "利用できません").format(convertor_key, key)
            logger.warning(msg)

        for name in declared_params.keys():
            param = declared_params[name]
            if param.required and name not in self._convertor_params:
                msg = ("コンバータ '{}' の必須パラメータ '{}' が"
                       "未指定です").format(convertor_key, name)
                logger.error(msg)
                raise ValueError("Param '{}' is required.".format(name))

    def __enter__(self):
        # TODO: preheat params
        self._input.__enter__()
        self._output.__enter__()
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self._input.__exit__(exception_type, exception_value, traceback)
        self._output.__exit__(exception_type, exception_value, traceback)

    def reset(self):
        return self._input.reset()

    def next(self):
        self._current = self._input.next()
        return self._current

    def read(self):
        for record in self._input:
            self._current = record
            yield self._current

    def output(self, value):
        self._output.append(value)

    def input(self):
        return self._current

    def set_data(self, name, value):
        self._data[name] = value

    def get_data(self, name):
        return self._data[name]

    def get_proxy(self, value):
        return self._proxy(value)

    def get_param(self, name):
        # TODO: memo化
        convertor_meta = self._convertor.meta()
        declared_params = convertor_meta.params
        convertor_key = convertor_meta.key
        if name not in declared_params:
            msg = (
                "Accessing param '{}' of the converter '{}' "
                "which is not declared.").format(name, convertor_key)
            logger.error(msg)
            raise ValueError(msg)

        param = declared_params[name]
        if param.required and name not in self._convertor_params:
            logger.error("コンバータ '{}' のパラメータ '{}' は必須です（終了します）".format(
                convertor_key, name))
            msg = "Param '{}' of the convertor '{}' is required.".format(
                convertor_key, name)
            raise ValueError(msg)

        val = self._convertor_params.get(name)
        return param.get_value(val, self)

    def get_params(self):
        """
        有効なパラメータ名のリストを取得する
        """
        return self._convertor.meta().params.keys()
