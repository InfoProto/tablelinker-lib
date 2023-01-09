from abc import ABC, abstractmethod
from enum import Enum, unique
from logging import getLogger

from .proxy import NoopCollectionProxy
from .validators import Errors

logger = getLogger(__name__)


@unique
class Status(Enum):
    NONE = 0
    PROCESSING = 1
    SUCCESS = 2
    FAILURE = 3


class Runner(ABC):
    """
    実行処理
    """

    def __init__(self):
        self.status = Status.NONE
        self.result = None

    @abstractmethod
    def run(self, filter, filter_params, input, ouput, proxy=None):
        pass


class LocalRunner(Runner):
    """
    メモリー上で実行するRunner
    """

    def run(self, filter, filter_params, input, output, proxy=None):
        # TODO: 1レコード毎に例外をキャッチして、しきい値(例10%)を超えたら止めて失敗とする
        try:
            self.status = Status.PROCESSING
            with Context(filter, filter_params, input, output, proxy=proxy) as context:
                filter.process(context)

            return output

        except Exception:
            self.status = Status.FAILURE
            raise
        else:
            self.status = Status.SUCCESS


class Context(object):
    """
    コンテキスト
    """

    def __init__(self, filter, filter_params, input, output, proxy=None):
        self._filter = filter
        self._input = input
        self._output = output
        self._filter_params = filter_params
        self._proxy = proxy if proxy is not None else NoopCollectionProxy
        self._current = None
        self._current_idx = None
        self._data = {}

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

    def proxy(self):
        return self._proxy

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
        params = self._filter.meta().params
        if name not in params:
            return None

        param = params[name]
        val = self._filter_params.get(name)
        return param.get_value(val, self)


class Job(object):
    """
    変換処理のJob
    """

    def __init__(self, runner, filter, filter_params, input, output, proxy=None):
        self.runner = runner
        self.filter = filter()
        self.input = input
        self.output = output
        self.filter_params = filter_params

        self.status = Status.NONE
        self._errors = Errors()
        self._proxy = proxy

        self._result = None

    def run(self):

        if not self._validate(self.filter_params, input=self.input, output=self.output):
            print("valid error!!", flush=True)
            return False

        result = self._runner_run()
        self.set_result(result)

        return True

    def _runner_run(self):
        return self.runner.run(self.filter, self.filter_params, self.input, self.output, proxy=self._proxy,)

    def _validate(self, params, input=None, output=None):
        if params is None:
            return True
        elif not self.filter.params.validate(params, self._errors, input, output,):
            return False
        else:
            return True

    def errors(self):
        return self._errors

    def set_result(self, result):
        self._result = result

    def get_result(self):
        """
        結果の取得
        :return:
        """
        return self._result


class LocalJob(Job):
    def __init__(self, filter, filter_params, input, output, proxy=None):
        super(LocalJob, self).__init__(LocalRunner(), filter, filter_params, input, output, proxy=proxy)

    # def get_result(self):
    #     return self.output
