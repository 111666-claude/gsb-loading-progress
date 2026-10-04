"""命令行入口：跑加载进度样例。"""

import argparse

from .core import Loading


def build_parser():
    parser = argparse.ArgumentParser(prog="loading-progress", description="加载进度聚合")
    parser.add_argument("--sample", default="dup", help="dup / empty / unknown / scan")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "dup":
        book = Loading({"a": 1, "b": 1})
        book.report("a")
        book.report("a")
        print("progress=%.2f" % book.progress())
    elif args.sample == "empty":
        print("progress=%.2f" % Loading({}).progress())
    elif args.sample == "unknown":
        book = Loading({"a": 1, "b": 1})
        book.report("a")
        book.report("ghost")
        print("progress=%.2f" % book.progress())
    elif args.sample == "scan":
        book = Loading({"a-%d" % index: 1 for index in range(3000)})
        for _ in range(3000):
            book.progress()
        print("scanned=%d" % book.scanned_count())
    else:
        raise SystemExit("需要 --sample dup|empty|unknown|scan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
