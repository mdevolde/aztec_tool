import argparse
import sys
from pathlib import Path
from . import __version__
from .decoder import AztecDecoder
from .exceptions import AztecDecoderError


def main():
    parser = argparse.ArgumentParser(
        description="A fast, pure-Python Aztec Code reader with auto-orientation and Reed-Solomon correction.",
        prog="aztec-tool",
    )
    parser.add_argument(
        "image", type=Path, nargs="?", help="Path to Aztec barcode image"
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--info", action="store_true", help="Print metadata about the barcode"
    )
    group.add_argument(
        "--debug", action="store_true", help="Dump bitmap and corrected bits"
    )
    parser.add_argument_group(group)
    parser.add_argument(
        "--no-auto-orient", action="store_false", help="Disable auto-orientation"
    )
    parser.add_argument(
        "--no-auto-correct", action="store_false", help="Disable auto-correction"
    )
    parser.add_argument(
        "--no-mode-auto-correct",
        action="store_false",
        help="Disable mode auto-correction",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    args = parser.parse_args()

    if not args.image:
        parser.print_help()
        sys.exit(0)

    try:
        decoder = AztecDecoder(
            args.image,
            auto_orient=args.no_auto_orient,
            auto_correct=args.no_auto_correct,
            mode_auto_correct=args.no_mode_auto_correct,
        )
        if args.info:
            print(f"Type:         {decoder.aztec_type.name}")
            print(f"Layers:       {decoder.mode_info['layers']}")
            print(f"Data words:   {decoder.mode_info['data_words']}")
            print(
                f"ECC bits:     {"".join([str(bit) for bit in decoder.mode_info['ecc_bits']])}"
            )
        elif args.debug:
            print("Bitmap:")
            print(decoder.bitmap)
            print("Corrected bits:")
            print(decoder.corrected_bits)
        else:
            print(decoder.decode())
    except AztecDecoderError as e:
        print(f"[error] {e}", file=sys.stderr)
        sys.exit(1)
