#!/usr/bin/env python3

import argparse
import os
import os.path
import sys
import logging
import random
import zlib

from .color import Color
from .png import PngParser
from .version import __version__
from .chunktypes import CHUNK_CRC_SIZE


RAW_BANNER = """
 ▄▄▄· ▐ ▄  ▄▄ •  ▄▄▄· ▄▄▄· ▄▄▄  .▄▄ · ▄▄▄ .▄▄▄
▐█ ▄█•█▌▐█▐█ ▀ ▪▐█ ▄█▐█ ▀█ ▀▄ █·▐█ ▀. ▀▄.▀·▀▄ █·
 ██▀·▐█▐▐▌▄█ ▀█▄ ██▀·▄█▀▀█ ▐▀▀▄ ▄▀▀▀█▄▐▀▀▪▄▐▀▀▄
▐█▪·•██▐█▌▐█▄▪▐█▐█▪·•▐█ ▪▐▌▐█•█▌▐█▄▪▐█▐█▄▄▌▐█•█▌
.▀   ▀▀ █▪·▀▀▀▀ .▀    ▀  ▀ .▀  ▀ ▀▀▀▀  ▀▀▀ .▀  ▀
"""


def show_banner() -> None:
    colors = [
        '\033[0m',
        '\033[31m',
        '\033[32m',
        '\033[33m',
        '\033[34m',
        '\033[35m',
        '\033[36m'
    ]

    def colorize(letter: str) -> str:
        if letter in (' ', '\n'):
            return letter
        choice = random.choice(colors)
        return f'{choice}{letter}\033[0m'

    banner = ''.join(colorize(l) for l in RAW_BANNER)
    version = f'\033[1mv{__version__}\033[0m'

    print(f'{banner} {version}\n')


def show_meta(filename: str) -> None:
    meta = f'\033[1;33mFilename: \033[34m{os.path.basename(filename)} \033[35m| \033[33m' \
           f'Size: \033[34m{os.stat(filename).st_size}\033[0m\n'
    print(meta)


def print_error_and_exit(*args, **kwargs) -> None:
    print(*args, file=sys.stderr, **kwargs)
    sys.exit(1)


def print_chunk(chunk, idx: int, spos: int, epos: int,
                print_data: bool = False, format_raw: bool = False,
                print_crc: bool = False, print_length: bool = False,
                hexa: bool = False) -> None:
    if hexa:
        print(f'[{Color.line}{spos:08x}-{epos:08x}{Color.r}] ({Color.id}{idx}{Color.r})')
    else:
        print(f'[{Color.line}{spos:08d}-{epos:08d}{Color.r}] ({Color.id}{idx}{Color.r})')
    try:
        print(f'{Color.chunk}{chunk.type.decode()}{Color.r}:')
    except UnicodeDecodeError:
        print(f'{Color.chunk}{chunk.type}{Color.r}:')

    if print_crc:
        current = chunk.crc
        computed = zlib.crc32(
            chunk.type + chunk.data).to_bytes(CHUNK_CRC_SIZE, 'big')
        if current == computed:
            print(f'{Color.crc}CRC : {computed.hex()}{Color.r}')
        else:
            print(f'{Color.crc}CRC : {current.hex()} : Incorrect must be {computed.hex()}{Color.r}')
    if print_length:
        print(f'{Color.length}Length : {epos - spos}{Color.r}')

    print(f'{Color.length}Data size : {len(chunk.data)}{Color.r}')
    if print_data:
        if format_raw:
            print(chunk.data)
        else:
            print(chunk)

    print()


def args_parser() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Prints PNG text sections')
    parser.add_argument('file', help='A PNG image')

    # Select Chunk
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-a', '--all', help='Print all chunk infos', action='store_true')
    group.add_argument(
        '-c', '--chunk', help='Select chunk with this id', type=int)
    group.add_argument('-t', '--type', help='Select chunks by type', type=str)
    group.add_argument(
        '--text', help='Display all text chunk', action='store_true')

    # Chunk infos
    parser.add_argument(
        '-d', '--data', help='Print chunk data', action='store_true')
    parser.add_argument(
        '--raw', help='Print chunk data as raw bytes', action='store_true')
    parser.add_argument(
        '--length', help='Print chunk length', action='store_true')
    parser.add_argument(
        '--crc', help='Print chunk crc and check if is right', action='store_true')
    parser.add_argument(
        '--hex', help='Print bytes position in Hexadecimal', action='store_true')
    parser.add_argument('-s', '--show', help='Show image', action='store_true')

    # Save file
    parser.add_argument(
        '-o', '--output', help='Save image (fix input file errors if any)', type=str, default='')

    # Debug
    parser.add_argument('-v', '--verbose', action='count',
                        help='Increase verbosity')
    return parser.parse_args()


def main() -> None:
    show_banner()
    args = args_parser()

    filename = args.file
    if not os.path.isfile(filename):
        print_error_and_exit(f'Error: file not found {filename}')
    show_meta(filename)

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    with PngParser(filename) as png:
        chunks: list
        if args.chunk is not None:
            chunks = [png.get_by_index(args.chunk)]
        elif args.type is not None:
            chunks = png.get_by_type(args.type.encode())
        elif args.text:
            args.data = True
            chunks = png.get_text_chunks()
        else:
            chunks = png.get_all()

        for idx, chunk in enumerate(chunks):
            spos, epos = png.get_pos(chunk)
            print_chunk(chunk, idx, spos, epos, args.data,
                        args.raw, args.crc, args.length, args.hex)

        if args.show:
            png.show_image()

        if args.output:
            name = args.output
            png.save_file(name)

    # if args.show:
    #     flush_input()
