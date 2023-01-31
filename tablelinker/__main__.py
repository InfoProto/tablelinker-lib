import csv
import io
import json
from logging import getLogger
import os
import sys
import tempfile

from docopt import docopt

from tablelinker import Table

logger = getLogger(__name__)

HELP = """
'tablelinker' は表データ（CSV, TSV, Excel）を読み込み、
さまざまなコンバータを適用して変換・加工し、
目的のフォーマットの表データを生成するツールです。

Usage:
  {p} -h
  {p} mapping [-d] [-i <file>] [-s <sheet>] [-o <file>] [-a]\
 ([-t <sheet>] <template>|--headers=<headers>)
  {p} [convert] [-d] [-i <file>] [-s <sheet>] [-o <file>] [--no-cleaning] [<task>...]

Options:
  -h --help              このヘルプを表示
  -d --debug             デバッグメッセージを表示
  -i, --input=<file>     入力ファイルを指定（省略時は標準入力）
  -s, --sheet=<sheet>    入力ファイルのうち対象とするシート名（省略時は先頭）
  -o, --output=<file>    出力ファイルを指定（省略時は標準出力）
  -a, --auto             マッピング情報ではなくマッピング結果を出力する
  -t, --template-sheet=<sheet>  テンプレートのシート名（省略時は先頭）
  --no-cleaning          指定すると入力ファイルをクリーニングしない
  --headers=<headers>    列名リスト（カンマ区切り）

Parameters:
  <task>        タスクファイル（コンバータとパラメータを記述した JSON）
  <template>    テンプレート列を含む表データファイル

Examples:

- CSV ファイル ma030000.csv を変換して標準出力に表示します

  python -m tablelinker -i ma030000.csv task.json

  適用するコンバータやパラメータは task.json ファイルに JSON 形式で記述します。

- Excel ファイル hachijo_sightseeing.xlsx をテンプレート\
  xxxxxx_tourism.csv に合わせるマッピング情報を生成します

  python -m tablelinker mapping \
-i hachijo_sightseeing.xlsx templates/xxxxxx_tourism.csv

  マッピング情報はタスクとして利用できる JSON 形式で出力されます。
""".format(p='tablelinker')

def _validate_task(task: dict):
    """
    タスクの書式をチェックします。

    Notes
    -----
    書式に問題があれば ValueError 例外を送出します。
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


def convert(args: dict):
    taskfiles = args['<task>']
    all_tasks = []

    skip_cleaning = bool(args['--no-cleaning'])

    if len(taskfiles) > 0:
        for taskfile in taskfiles:
            with open(taskfile, 'r') as jsonf:
                logger.debug("Reading tasks from '{}'.".format(
                    taskfile))
                try:
                    tasks = json.load(jsonf)
                except json.decoder.JSONDecodeError as e:
                    logger.error((
                        "タスクファイル '{}' の JSON 表記が正しくありません。"
                        "json.decoder.JSONDecodeError: {}").format(taskfile, e))
                    sys.exit(-1)

            if isinstance(tasks, dict):
                # コンバータが一つだけ指定されている場合
                tasks = [tasks]

            try:
                if isinstance(tasks, list):
                    # 複数のコンバータがリストで指定されている場合
                    for task in tasks:
                        # タスクファイルのフォーマットチェック
                        _validate_task(task)

                else:
                    raise ValueError("タスクリストが Array ではありません。")

            except ValueError as e:
                logger.error((
                    "タスクファイル '{}' のフォーマットが"
                    "正しくありません。詳細：{}").format(taskfile, str(e)))
                sys.exit(-1)

            all_tasks += tasks

    with tempfile.TemporaryDirectory() as tmpdir:
        if args['--input'] is not None:
            csv_in = args['--input']
        else:
            logger.debug("Reading csv data from STDIN...")
            # sys.stdin は seek できないので、一時ファイルに保存する
            csv_in = os.path.join(tmpdir, 'input.csv')
            with open(csv_in, 'wb') as fout:
                fout.write(sys.stdin.buffer.read())

        logger.debug("Start convertor(s)...")
        table = Table(
            csv_in,
            sheet=args['--sheet'],
            skip_cleaning=skip_cleaning)

        for task in all_tasks:
            try:
                # タスク実行
                if "note" in task:
                    logger.info(task["note"])

                logger.debug("Running {}".format(task["convertor"]))
                table = table.convert(
                    task["convertor"], task["params"])

            except RuntimeError as e:
                logger.error((
                    "タスク '{}' の実行中にエラーが発生しました。"
                    "詳細：{}").format(task["convertor"], str(e)))
                sys.exit(-1)

        # 結果を出力
        if args['--output'] is None:
            table.write()
        else:
            table.save(args['--output'])


def mapping(args: dict):
    from tablelinker.convertors import core
    from tablelinker.convertors.core.mapping import ItemsPair
    from collections import OrderedDict

    with tempfile.TemporaryDirectory() as tmpdir:
        if args['--input'] is not None:
            csv_in = args['--input']
        else:
            # 標準入力のデータを一時ファイルに保存する
            # Note: stdin は seek() が利用できないため
            logger.debug("Reading csv data from STDIN...")
            csv_in = os.path.join(tmpdir, 'input.csv')
            with open(csv_in, 'wb') as fout:
                fout.write(sys.stdin.buffer.read())

        # しきい値
        # 手作業で修正することを前提とするため、緩い値を用いる
        th = 20

        # 入力 CSV の見出し行を取得
        table = Table(csv_in, sheet=args['--sheet'])
        with table.open() as reader:
            headers = reader.__next__()

        # テンプレート CSV の見出し行を取得
        if args['<template>']:
            # ファイル名を指定
            template = Table(
                file=args['<template>'],
                sheet=args['--template-sheet'])
            with template.open() as reader:
                template_headers = reader.__next__()

        elif args['--headers']:
            with io.StringIO(
                    args['--headers'], newline='') as stream:
                reader = csv.reader(stream)
                template_headers = reader.__next__()

        # 項目マッピング
        pair = ItemsPair(template_headers, headers)

        mapping = OrderedDict()
        for result in pair.mapping():
            output, header, score = result
            if output is None:
                # マッピングされなかったカラムは除去
                continue

            if score * 100.0 < th or \
                    header is None:
                mapping[output] = None
            else:
                mapping[output] = header

        if args["--auto"] is False:
            # 結果出力
            result = json.dumps({
                "convertor": "mapping_cols",
                "params": {"column_map": dict(mapping)},
            }, indent=2, ensure_ascii=False)

            if args['--output']:
                with open(args['--output'], 'w') as f:
                    print(result, file=f)
            else:
                print(result)

        else:
            # "--auto" オプションが指定されている場合は変換結果を出力
            table = table.convert(
                convertor='mapping_cols',
                params={'column_map':dict(mapping)})
            if args['--output']:
                with open(args['--output'], 'w', newline='') as fout,\
                        table.open() as reader:
                    writer = csv.writer(fout)
                    for row in reader:
                        writer.writerow(row)

            else:
                with table.open() as reader:
                    writer = csv.writer(sys.stdout)
                    for row in reader:
                        writer.writerow(row)


if __name__ == '__main__':
    import logging

    args = docopt(HELP)

    if args['--debug']:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s:%(levelname)s:%(module)s:%(lineno)d:%(message)s')

    if args['--input'] is not None:
        if args['--input'].lower() in ('-', 'stdin'):
            args['--input'] = None

    if args['--output'] is not None:
        if args['--output'].lower() in ('-', 'stdout'):
            args['--output'] = None

    if args['mapping']:
        mapping(args)
    else:
        convert(args)
