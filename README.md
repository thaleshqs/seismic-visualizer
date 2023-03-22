# Interface para visualização de arquivos .segy e .sgy

Uma simples interface para visualização de arquivos .segy e .sgy feito pela Linha 1.

## Description

Para rodar é necessário ter instalado o easygui, o tkinter, o matplotlib e o segyio instalado, que por sua vez tem como requisitos:

A C99 compatible C compiler (tested mostly on gcc and clang)
A C++ compiler for the Python extension, and C++11 for the tests
CMake version 2.8.12 or greater
Python 3.6 or greater
numpy version 1.10 or greater
setuptools version 28 or greater
setuptools-scm
pytest
(Ver mais em: https://github.com/equinor/segyio)

Todos podem ser instalados por meio do comando pip install.

Após fazer as devidas instalações para rodar o projeto digite python3 main.py e a interface deve abrir.

OBS.: Se seu computador tiver um processador arm será necessário instalar os requisitos em um terminal simulando a arquitetura x86, visto que o segyio ainda não está preparado para tal arquitetura.
