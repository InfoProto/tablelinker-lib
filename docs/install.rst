.. _install:

インストール手順
================

.. note::

    他の Python パッケージと同様に、 Tablelinker パッケージは
    多くの依存パッケージをインストールします。システムの
    Python 環境を汚さないように venv などで仮想環境を作成し、
    その仮想環境内にインストールすることをお勧めします。

Tablelinker パッケージのインストール
------------------------------------

Tablelinker は pip コマンドでインストールできます。 ::

    pip install tablelinker

住所辞書データのインストール
----------------------------

住所ジオコーディング機能が必要なコンバータを利用するには、
別途住所辞書データをダウンロード・インストールする必要があります。 ::

    python -m jageocoder download-dictionary
    python -m jageocoder install-dictionary jusho-20220519.zip

詳細は `jageocoderのインストール手順 <https://jageocoder.readthedocs.io/ja/latest/install.html#install-dictionary>`_ を参照してください。

住所ジオコーディング機能を利用しない場合は住所辞書データは不要です。

アンインストール手順
--------------------

住所辞書データをインストールした場合、 Tablelinker パッケージを
アンインストールする前に辞書をアンインストールしてください。 ::

    python -m jageocoder uninstall-dictionary

Tablelinker パッケージは pip uninstall でアンインストールできます。 ::

    pip uninstall tablelinker

