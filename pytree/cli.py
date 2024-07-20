import argparse
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Literal


class Style:
    pass

@dataclass
class StyleNormal(Style):
    straight: str = '│'
    tee: str = '├──'
    elbow: str = '└──'
    space: str = ' '


@dataclass
class StyleHeavy(Style):
    straight: str = '┃'
    tee: str = '┣━━'
    elbow: str = '┗━━'
    space: str = ' '


@dataclass
class StyleDouble(Style):
    straight: str = '║'
    tee: str = '╠══'
    elbow: str = '╚══'
    space: str = ' '


styles = {
    'normal': StyleNormal(),
    'heavy':  StyleHeavy(),
    'double': StyleDouble(),
}




class Tree:
    def __init__(
            self,
            path: str | Path,
            ignore_patterns=None,
            ignore_file: str | Path | None = 'default',
            sort=False,
            style: Style | Literal['normal', 'heavy', 'double'] = 'normal'
    ):
        self.path = Path(path) if isinstance(path, str) else path
        self.children: list[Tree] = []
        self.ignore_patterns = ignore_patterns or []
        self.ignore_file = ignore_file
        self.exclude_patterns = []
        self.negate_patterns = []
        self.init_patterns()
        self.sort = sort
        self.style = styles[style] if isinstance(style, str) else style

    def load_pytreeignore(self):
        patterns = []
        if self.ignore_file is None:
            return patterns

        path = Path(__file__).parent / '.pytreeignore'
        if self.ignore_file != 'default':
            path = Path(self.ignore_file)

        with open(path, 'r') as f:
            for line in f.read().splitlines():
                if line.startswith('#') or len(line.strip()) == 0:
                    continue
                patterns.append(line)
        return patterns

    def init_patterns(self):
        ignore_file_patterns = self.load_pytreeignore()
        for pat in self.ignore_patterns + ignore_file_patterns:
            if pat.startswith('!'):
                self.negate_patterns.append(pat.lstrip('!'))
            else:
                self.exclude_patterns.append(pat)

    def should_ignore(self, path: Path):
        def check_pattern(path: Path, pat: str) -> bool:
            dir_name = path.name + '/' if path.is_dir() else ''
            dir_path = path.as_posix() + '/' if path.is_dir() else ''
            if '/' in pat:
                ignore = fnmatch(path.as_posix(), pat) or fnmatch(dir_path, pat)
            else:
                ignore = fnmatch(path.name, pat) or fnmatch(dir_name, pat)
            if ignore:
                return True

        ignore = False
        for pat in self.exclude_patterns:
            ignore = check_pattern(path, pat)
            if ignore:
                break

        negate = False
        if ignore:
            for pat in self.negate_patterns:
                negate = check_pattern(path, pat)
                if negate:
                    break

        return ignore and not negate

    def build(self):
        contents = Path(self.path).iterdir()
        if self.sort:
            contents = sorted(contents)

        for item in contents:
            if self.should_ignore(item):
                continue

            subtree = Tree(item, sort=self.sort, style=self.style)
            subtree.exclude_patterns = self.exclude_patterns
            subtree.negate_patterns = self.negate_patterns

            self.children.append(subtree)
            if item.is_dir():
                subtree.build()
        return self

    def stringify(self):
        def walk(tree: Tree, all_lines: list, line: list):
            for i, child in enumerate(tree.children):
                this_line = [*line]
                next_line = [*line]
                if i < len(tree.children) - 1:
                    this_line.append(self.style.tee)
                    next_line.extend([self.style.straight, self.style.space * 3])
                else:
                    this_line.append(self.style.elbow)
                    next_line.append(self.style.space * 4)

                if child.path.is_dir():
                    this_line.append(f' {child.path.name}/')
                    all_lines.append(''.join(this_line))
                    walk(child, all_lines, next_line)
                else:
                    this_line.append(f' {child.path.name}')
                    all_lines.append(''.join(this_line))

        all_lines = ['\n' + self.path.name.lstrip('/') + '/']
        walk(self, all_lines, ['  '])
        return '\n'.join(all_lines)


def main():
    parser = argparse.ArgumentParser(description="Print directory tree")
    parser.add_argument("directory", nargs="?", default=".",
                        help="Directory to start from (default: current directory)")
    parser.add_argument("-i", "--ignore", nargs="+", default=[], help="Ignore folders and files using glob patterns")
    parser.add_argument('-s', '--sort', default=False, help="Sort directory contents alphabetically")
    parser.add_argument('-st', '--style', default='normal', choices=['normal', 'heavy', 'double'],
                        help='The style of lines to draw')
    args = parser.parse_args()

    output = Tree(
            path=args.directory,
            ignore_patterns=args.ignore,
            sort=args.sort,
            style=args.style
    ).build().stringify()
    print(output)


if __name__ == "__main__":
    main()
