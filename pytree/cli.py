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
            is_dir: bool = False,
            ignore_patterns=None,
            ignore_file: str | Path | None = 'default',
            collapse_patterns=None,
            collapse_ellipses=False,
            sort=False,
            style: Style | Literal['normal', 'heavy', 'double'] = 'normal'
    ):
        self.path = Path(path) if isinstance(path, str) else path
        self.is_dir = is_dir
        self.children: list[Tree] = []
        self.ignore_patterns = ignore_patterns or []
        self.ignore_file = ignore_file
        self.exclude_patterns = []
        self.negate_patterns = []
        self.collapse_patterns = collapse_patterns or []
        self.collapse_ellipses = collapse_ellipses
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

    def check_pattern(self, name: str, resolved_path, is_dir, pat: str) -> bool:
        dir_name = name + '/' if is_dir else ''
        dir_path = resolved_path + '/' if is_dir else ''
        if '/' in pat:
            ignore = fnmatch(resolved_path, pat) \
                     or fnmatch(dir_path, pat) \
                     or fnmatch(dir_name, pat)
        else:
            ignore = fnmatch(name, pat) or fnmatch(dir_name, pat)
        if ignore:
            return True

    def should_ignore(self, path: Path, resolved_path: str, is_dir: bool):
        name = path.name
        ignore = False
        for pat in self.exclude_patterns:
            ignore = self.check_pattern(name, resolved_path, is_dir, pat)
            if ignore:
                break

        negate = False
        if ignore:
            for pat in self.negate_patterns:
                negate = self.check_pattern(name, resolved_path, is_dir, pat)
                if negate:
                    break
        return ignore and not negate

    def should_collapse(self, path: Path, resolved_path: str):
        name = path.name
        for pat in self.collapse_patterns:
            if self.check_pattern(name, resolved_path, True, pat):
                return True

    def build(self, collapse=False):
        if collapse:
            if self.collapse_ellipses:
                self.children.append(Tree('...', is_dir=False, style=self.style))
            return

        contents = Path(self.path).iterdir()

        if self.sort:
            contents = sorted(contents)

        for item in contents:
            is_dir = item.is_dir()
            resolved_path = item.resolve().as_posix()
            if self.should_ignore(item, resolved_path, is_dir):
                continue

            subtree = Tree(item, is_dir=is_dir, sort=self.sort, style=self.style)
            subtree.exclude_patterns = self.exclude_patterns
            subtree.negate_patterns = self.negate_patterns
            subtree.collapse_patterns = self.collapse_patterns
            subtree.collapse_ellipses = self.collapse_ellipses

            self.children.append(subtree)
            if is_dir:
                should_collapse = self.should_collapse(item, resolved_path)
                subtree.build(should_collapse)
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

                if child.is_dir:
                    this_line.append(f' {child.path.name}/')
                    all_lines.append(''.join(this_line))
                    walk(child, all_lines, next_line)
                else:
                    this_line.append(f' {child.path.name}')
                    all_lines.append(''.join(this_line))

        root_name = self.path.name or self.path.resolve().name
        root_name = root_name.lstrip('/') + '/'
        all_lines = ['\n' + root_name]
        walk(self, all_lines, [])
        return '\n'.join(all_lines)


def main():
    parser = argparse.ArgumentParser(description="Print directory tree")
    parser.add_argument("directory", nargs="?", default=".",
                        help="Directory to start from (default: current directory)")
    parser.add_argument("-i", "--ignore", nargs="+", default=[], help="Ignore folders and files using glob patterns")
    parser.add_argument("-c", "--collapse", nargs="+", default=[], help="Collapse folders using glob patterns")
    parser.add_argument("-e", "--ellipses", action='store_true', default=False,
                        help="Show ellipses for collapsed folder's file contents")
    parser.add_argument('-s', '--sort', action='store_true', default=False,
                        help="Sort directory contents alphabetically")
    parser.add_argument('-st', '--style', default='normal', choices=['normal', 'heavy', 'double'],
                        help='The style of lines to draw')
    args = parser.parse_args()

    output = Tree(
            path=args.directory,
            ignore_patterns=args.ignore,
            collapse_patterns=args.collapse,
            collapse_ellipses=args.ellipses,
            sort=args.sort,
            style=args.style
    ).build().stringify()

    print(output)


if __name__ == "__main__":
    main()
