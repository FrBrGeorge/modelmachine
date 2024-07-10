from __future__ import annotations

import argparse
import inspect
import sys
from dataclasses import dataclass
from typing import Callable

import pyparsing as pp
from pyparsing import CaselessLiteral as Li
from pyparsing import Group as Gr
from pyparsing import Word as Wd

from modelmachine.__about__ import __version__
from modelmachine.cpu.source import source


@dataclass
class Param:
    name: str
    short: str | None
    help: str


def ignore() -> list[pp.ParseResults]:
    return []


pp.ParserElement.set_default_whitespace_chars(" \t")
SKIP_SHORT = 2
param = (
    Wd(pp.alphas, pp.alphanums + "_")
    + (Li(", ").set_parse_action(ignore) + Gr("-" + pp.Char(pp.alphas)))[0, 1]
    + Li("--").set_parse_action(ignore)
    + Wd(pp.alphanums, pp.printables + " \t")
).set_parse_action(
    lambda t: [
        Param(
            name=t[0],
            short="".join(t[1]) if len(t) > SKIP_SHORT else None,
            help=t[-1],
        )
    ]
)


class Cli:
    _parser: argparse.ArgumentParser
    _subparsers: argparse._SubParsersAction[argparse.ArgumentParser]

    def __init__(self, description: str):
        self._parser = argparse.ArgumentParser(description=description)
        self._subparsers = self._parser.add_subparsers(title="commands")

    def __call__(self, f: Callable[..., int]) -> Callable[..., int]:
        docstring = str(inspect.getdoc(f))
        sig = inspect.signature(f)

        cmd = self._subparsers.add_parser(f.__name__, help=docstring.split(".")[0])

        params: dict[str, Param] = {
            p[0].name: p[0] for p in param.search_string(docstring)
        }

        for key, arg in sig.parameters.items():
            p = params.get(key)
            if p is None:
                msg = (
                    f"Cannot find parameter '{key}' in docstring of"
                    f" '{f.__name__}'; known params: {list(params)};"
                    f" docstring: {docstring}"
                )
                raise KeyError(msg)
            if arg.default is inspect.Parameter.empty:
                if arg.annotation == "str":
                    cmd.add_argument(key, help=p.help)
                else:
                    raise NotImplementedError
            else:
                short = [p.short] if p.short is not None else []
                if arg.annotation == "str":
                    cmd.add_argument(*short, f"--{p.name}", help=p.help)
                if arg.annotation == "bool":
                    if arg.default is False:
                        cmd.add_argument(
                            *short,
                            f"--{p.name}",
                            action="store_true",
                            help=p.help,
                        )
                    else:
                        assert arg.default is True
                        cmd.add_argument(
                            *short,
                            f"--no-{p.name}",
                            action="store_false",
                            help=p.help,
                        )
                else:
                    raise NotImplementedError

        def g(args: argparse.Namespace) -> int:
            argv = {}
            for key in sig.parameters:
                argv[key] = getattr(args, key)
            return f(**argv)

        cmd.set_defaults(func=g)
        return f

    def main(self) -> int:
        args = self._parser.parse_args()

        if "func" not in args:
            self._parser.print_help()
            return 1

        return int(args.func(args))


cli = Cli(f"Modelmachine {__version__}")


@cli
def run(*, filename: str, protect_memory: bool = False) -> int:
    """Run program.

    filename -- file containing machine code, '-' for stdin
    protect_memory, -m -- halt, if program tries to read dirty memory
    """
    if filename == "-":
        cpu = source(sys.stdin.read())
    else:
        with open(filename) as fin:
            cpu = source(fin.read())

    cpu.control_unit.run()
    cpu.print_result(sys.stdout)

    return 0


@cli
def debug(*, filename: str, protect_memory: bool = False) -> int:
    """Debug the program.

    filename -- file containing machine code
    protect_memory, -m -- halt, if program tries to read dirty memory
    """
    with open(filename) as fin:
        cpu = source(fin.read())

    debug(cpu)

    return 0


# @cli
# def asm(*, input_file: str, output_file: str) -> int:
#     """Assemble program.
#
#     input_file -- asm source, '-' for stdin
#     output_file -- machine code file, '-' for stdout
#     """
#     return 0