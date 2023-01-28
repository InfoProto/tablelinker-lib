.. tablelinker documentation master file, created by
    sphinx-quickstart on Mon Jan 16 05:05:34 2023.
    You can adapt this file completely to your liking, but it should at least
    contain the root `toctree` directive.

Tablelinker ドキュメント
========================

Tablelinker は CSV や Excel ファイルなどの表データを読み込み、
さまざまな :ref:`convertor` を適用して変換・加工し、
目的のフォーマットの表データを生成するツールです。

表データの入力、変換、出力という処理はデータ解析の前処理として
不可欠ですが、基本的な処理は比較的簡単なため、
あちこちで同じようなコードが実装されています。
しかし実際の表データは、 CSV ファイルと書かれていても
文字エンコーディングや区切り文字がまちまちだったり、
同じフォーマットのはずの表データが作成者や作成時期によって
列名の表記が少し違うといった細かい問題に悩まされることが多く、
想定外の手間がかかります。

Tablelinker は、表データの前処理によく利用される変換処理を
ライブラリ化し、オープンソースとして公開することで、
データのクリーニングやバリデーションといった作業に要するコストを
減らすことを目的とします。


.. toctree::
    :maxdepth: 2
    :caption: 目次

    quick_start
    install
    as_library
    as_command
    convertor
    api
