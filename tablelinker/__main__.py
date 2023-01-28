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
'tablelinker' は CSV 形式の表データを読み込み、
さまざまなコンバータを適用して変換・加工し、
目的のフォーマットの表データを生成するツールです。

Usage:
  {p} -h
  {p} mapping [-d] [-i <file>] [-o <file>] (<template>|--headers=<headers>)
  {p} [convert] [-d] [-i <file>] [-s <sheet>] [-o <file>] [--no-cleaning] [<task>...]

Options:
  -h --help              このヘルプを表示
  -d --debug             デバッグメッセージを表示
  -i, --input=<file>     入力ファイルを指定（省略時は標準入力）
  -s, --sheet=<sheet>    入力ファイルのうち対象とするシート（省略時は先頭）
  -o, --output=<file>    出力ファイルを指定（省略時は標準出力）
  --no-cleaning          指定すると入力ファイルをクリーニングしない
  --headers=<headers>    列名リスト（カンマ区切り）

Parameters:
  <task>        タスクファイル（コンバータとパラメータを記述した JSON）
  <template>    表データのテンプレート CSV ファイル

Examples:

- CSV ファイルを変換して標準出力に表示します

  python -m tablelinker -i sample/ma0300000.csv sample/task.json

  適用するコンバータやパラメータは <task> に JSON 形式で記述します。

- CSV ファイルをテンプレートに合わせるマッピング情報を生成します

  python -m tablelinker mapping \
-i sample/sakurai_sightseeing_spots_sjis.csv \
templates/sightseeing_spots.csv

  マッピング情報はタスクとして利用できる JSON 形式で出力されます。
""".format(p='tablelinker')


def convert(args: dict):
    taskfiles = args['<task>']
    tasks = []

    skip_cleaning = bool(args['--no-cleaning'])

    if len(taskfiles) > 0:
        for taskfile in taskfiles:
            with open(taskfile, 'r') as jsonf:
                logger.debug("Reading tasks from '{}'.".format(
                    taskfile))
                try:
                    tasks.append(json.load(jsonf))
                except json.decoder.JSONDecodeError as e:
                    logger.error((
                        "タスクファイル '{}' の JSON 表記が正しくありません。"
                        "json.decoder.JSONDecodeError: {}").format(taskfile, e))
                    sys.exit(-1)

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
            sheet = args['--sheet'],
            skip_cleaning=skip_cleaning)

        for task in tasks:
            if isinstance(task, dict):
                # コンバータが一つだけ指定されている場合
                logger.debug("Running {}".format(task["convertor"]))
                table = table.convert(
                    task["convertor"], task["params"])
            elif isinstance(task, list):
                # 複数のコンバータがリストで指定されている場合
                for t in task:
                    logger.debug("Running {}".format(t["convertor"]))
                    table = table.convert(
                        t["convertor"], t["params"])

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
            logger.debug("Reading csv data from STDIN...")
            csv_in = os.path.join(tmpdir, 'input.csv')
            with open(csv_in, 'wb') as fout:
                fout.write(sys.stdin.buffer.read())

        # しきい値
        # 手作業で修正することを前提とするため、緩い値を用いる
        th = 20

        # 入力 CSV の見出し行を取得
        with core.CsvInputCollection(csv_in) as f:
            headers = f.next()

        # テンプレート CSV の見出し行を取得
        if args['<template>']:
            # ファイル名指定
            with open(
                    args['<template>'],
                    mode='r', newline='') as f:
                reader = csv.reader(f)
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


if __name__ == '__main__':
    import logging

    args = docopt(HELP)

    if args['--debug']:
        log_level = logging.DEBUG
    else:
        log_level = logging.WARNING

    logging.basicConfig(
        level=log_level,
        format='%(levelname)s:%(module)s:%(lineno)d:%(message)s')

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
