import json
from logging import getLogger
import os
from typing import List, Optional, Union


logger = getLogger(__name__)


class Task(object):
    """
    タスクを管理するクラス。

    Attributes
    ----------
    convertor: str
        コンバータ名。
    params: dict
        パラメータ名と値を持つ dict。
    note: str, optional
        タスクの内容に対するメモ。
    """

    def __init__(
            self,
            convertor: str,
            params: dict,
            note: Optional[str] = None):
        self.convertor = convertor
        self.params = params
        self.note = note

    def __repr__(self):
        if self.note:
            return "{}({})".format(
                self.convertor,
                self.note)

        return "{}".format(self.convertor)

    @classmethod
    def create(cls, task: dict) -> "Task":
        """
        dict から Task を作成します。
        パラメータのキーのチェックも行います。

        Parameters
        ----------
        task: dict
            キーに "convertor", "params" を必ず含み、オプションとして
            "note" を含む dict。

        Returns
        -------
        Task
            新しい Task オブジェクト。

        Notes
        -----
        必要なキーが欠けていたり、不要なキーが含まれていると
        `ValueError` 例外を送出します。

        キーのチェックしかしないため、正しくない値が指定されていても
        エラーにはなりません。
        たとえば convertor に存在しないコンバータ名が指定されていたり、
        params にそのコンバータでは利用できないパラメータが
        指定されていてもエラーになりません。

        """
        if not isinstance(task, dict):
            raise ValueError("タスクが object ではありません。")

        unrecognized_keys = []
        for key in task.keys():
            if key not in ("convertor", "params", "note",):
                unrecognized_keys.append(key)

        if len(unrecognized_keys) > 0:
            raise ValueError("未定義のキー '{}' が使われています。".format(
                ",".join(unrecognized_keys)))

        undefined_keys = []
        for key in ("convertor", "params",):
            if key not in task:
                undefined_keys.append(key)

        if len(undefined_keys) > 0:
            raise ValueError("キー '{}' が必要です。".format(
                ",".join(undefined_keys)))

        return Task(**task)

    @classmethod
    def from_files(
            cls,
            taskfiles: Union[os.PathLike, List[os.PathLike]]) -> List["Task"]:
        """
        タスクファイルを読み込み、解析・検証してタスクリストを作成します。

        Parameters
        ----------
        taskfiles: PathLike, List[PathLike]
            タスクファイルのパス、またはパスのリスト。

        Returns
        -------
        List[Task]
            タスクのリスト。

        Notes
        -----
        タスクが1つの場合でもリストを返します。

        """
        if isinstance(taskfiles, os.PathLike):
            taskfiles = [taskfiles]

        all_tasks = []
        for taskfile in taskfiles:
            with open(taskfile, 'r') as jsonf:
                logger.debug("Reading tasks from '{}'.".format(
                    taskfile))
                try:
                    tasks = json.load(jsonf)
                except json.decoder.JSONDecodeError as e:
                    logger.error((
                        "タスクファイル '{}' の JSON 表記が正しくありません。"
                        "json.decoder.JSONDecodeError: {}").format(
                            taskfile, e))
                    raise ValueError("Invalid JSON in '{}'.({})".format(
                        taskfile, e))

            if isinstance(tasks, dict):
                # コンバータが一つだけ指定されている場合
                tasks = [tasks]

            try:
                for task in tasks:
                    # タスクファイルのフォーマットチェック
                    all_tasks.append(Task.create(task))

            except ValueError as e:
                logger.error((
                    "タスクファイル '{}' のフォーマットが"
                    "正しくありません。詳細：{}").format(taskfile, str(e)))
                raise ValueError("Invalid Task format in '{}'.({})".format(
                    taskfile, e))

        return all_tasks
