#!/usr/bin/env python3

import argparse
import os
import os.path
import sys
import logging
import random

from .color import Color
from .utils import monitor_results, flush_input
from .chunktypes import ChunkTypes
from .png import PngParser
from .version import __version__


def show_banner():
    colors = [
        "\033[0m",
        "\033[31m",
        "\033[32m",
        "\033[33m",
        "\033[34m",
        "\033[35m",
        "\033[36m"
    ]

    def colorize(letter):
        if letter == " " or letter == "\n":
            return letter
        c = random.choice(colors)
        return "%s%s\033[0m" % (c, letter)

    raw_banner = """
 ▄▄▄· ▐ ▄  ▄▄ •  ▄▄▄· ▄▄▄· ▄▄▄  .▄▄ · ▄▄▄ .▄▄▄
▐█ ▄█•█▌▐█▐█ ▀ ▪▐█ ▄█▐█ ▀█ ▀▄ █·▐█ ▀. ▀▄.▀·▀▄ █·
 ██▀·▐█▐▐▌▄█ ▀█▄ ██▀·▄█▀▀█ ▐▀▀▄ ▄▀▀▀█▄▐▀▀▪▄▐▀▀▄
▐█▪·•██▐█▌▐█▄▪▐█▐█▪·•▐█ ▪▐▌▐█•█▌▐█▄▪▐█▐█▄▄▌▐█•█▌
.▀   ▀▀ █▪·▀▀▀▀ .▀    ▀  ▀ .▀  ▀ ▀▀▀▀  ▀▀▀ .▀  ▀
"""
    banner = "".join(colorize(l) for l in raw_banner)

    version = "\033[1mv%s\033[0m" % __version__

    final = "%s %s\n"
    print(final % (banner, version))


def show_meta(filename):
    meta = "\033[1;33mFilename: \033[34m%s \033[35m| \033[33mSize: \033[34m%s\033[0m" % (os.path.basename(filename), os.stat(filename).st_size)
    print("%s\n" % meta)


def print_error_and_exit(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    exit(1)


def print_chunk(chunk, idx, data=False, crc=False, length=False, hexa=False):
    # sPos = chunk.start_position
    # ePos = chunk.end_position
    # if hexa:
    #     print('[{}{:08x}-{:08x}{}] ({}{}{})'.format(Color.line, sPos, ePos,
    #                                                 Color.r, Color.id,
    #                                                 chunk.id, Color.r))
    # else:
    #     print('[{}{:08d}-{:08d}{}] ({}{}{})'.format(Color.line, sPos,
    #                                                 ePos, Color.r,
    #                                                 Color.id, chunk.id,
    #                                                 Color.r))
    print('({}{}{})'.format(Color.id, idx, Color.r))
    print('{}{}{}:'.format(Color.chunk, chunk.type, Color.r))

    if crc:
        current = chunk.crc
        computed = chunk.compute_crc()
        if current == computed:
            print('{}CRC : {}{}'.format(Color.crc, computed.hex(), Color.r))
        else:
            print('{}CRC : {} : Incorrect must be {}{}'.format(Color.crc, current.hex(), computed.hex(), Color.r))
    if length:
        print('{}Length : {}{}'.format(Color.length, chunk.length,
                                       Color.r))

    print('{}Data size : {}{}'.format(Color.length, len(chunk.data), Color.r))
    if data:
        print(str(chunk.data))

    print()


def args_parser():
    parser = argparse.ArgumentParser(description='Prints PNG text sections')
    parser.add_argument('file', help='an PNG image')

    # Select Chunk
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-a', '--all', help='Print all chunk infos',
                       action='store_true')
    group.add_argument('-o', '--object', help='Print the chunk with this id',
                       type=int)
    group.add_argument('-t', '--type', help='Filter chunk by type',
                       type=str)
    group.add_argument('--text', help='Display all text chunk',
                       action='store_true')

    # Chunk infos
    parser.add_argument('-d', '--data', help='Print chunk data',
                        action='store_true')
    parser.add_argument('-l', '--length', help='Print chunk length',
                        action='store_true')
    parser.add_argument('-c', '--crc', help='Print chunk crc and check if is right',
                        action='store_true')
    parser.add_argument('--hex', help='Print bytes position in Hexadecimal',
                        action='store_true')
    parser.add_argument('-s', '--show', help='Show image',
                        action='store_true')

    # Save file
    parser.add_argument('--output', help='Save image (fixe current file error)',
                        type=str, default='')

    # Debug
    parser.add_argument('-v', '--verbose',
                        action='store_true', help="Verbose mode")

    return parser.parse_args()


def main():
    show_banner()
    args = args_parser()

    filename = args.file
    if not os.path.isfile(filename):
        print_error_and_exit('Error: file not found %s' % filename)
    show_meta(filename)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    with PngParser(filename) as png:

        chunks = None
        if args.object is not None:
            chunks = png.get_by_id(args.object)

        elif args.type is not None:
            type_ = ChunkTypes.from_binary(args.type.encode())
            chunks = png.get_by_type(type_)

        elif args.text:
            chunks = png.get_text_chunks()

        else:
            chunks = png.get_all()

        for idx, chunk in enumerate(chunks):
            print_chunk(chunk, idx, args.data, args.crc, args.length, args.hex)

        if args.show:
            png.show_image()

        if args.output:
            name = args.output
            png.save_file(name)

    if args.show:
        flush_input()
