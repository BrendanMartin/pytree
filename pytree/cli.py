import argparse
import os
from dataclasses import dataclass
from fnmatch import fnmatch
from typing import Literal


@dataclass
class StyleNormal():
    straight: str = '│'
    tee: str = '├──'
    elbow: str = '└──'
    space: str = ' '


@dataclass
class StyleHeavy():
    straight: str = '┃'
    tee: str = '┣━━'
    elbow: str = '┗━━'
    space: str = ' '


@dataclass
class StyleDouble():
    straight: str = '║'
    tee: str = '╠══'
    elbow: str = '╚══'
    space: str = ' '


styles = {
    'normal': StyleNormal(),
    'heavy':  StyleHeavy(),
    'double': StyleDouble(),
}

# skip_paths: list[re.Pattern] = [
#     re.compile(r'(?<![\w\-,_])\.(?!\S*ignore|env).*') # ignore dot files except .<service>ignore and .env
# ]

skip_patterns = [
    '*/.*[!ignore]',
    '*/.[!env]'
]


class Tree:
    def __init__(self, name, path, is_dir=True, exclude_dirs=None):
        self.name = name
        self.path = path
        self.is_dir = is_dir
        self.children: list[Tree] = []
        self.exclude_dirs = exclude_dirs or []

    def should_skip(self, path):
        # for skip in skip_paths:
        #     if skip.search(path):
        #         return True
        for skip in skip_patterns:
            if fnmatch(path, skip):
                return True
        for exc in self.exclude_dirs:
            if fnmatch(path, exc):
                return True
        return False

    def build(self):
        for name in sorted(os.listdir(self.path)):
            path = os.path.join(self.path, name)
            if self.should_skip(path):
                continue
            if os.path.isdir(path):
                subtree = Tree(name, path, is_dir=True, exclude_dirs=self.exclude_dirs)
                self.children.append(subtree)
                subtree.build()
            else:
                leaf = Tree(name, path, is_dir=False)
                self.children.append(leaf)

    def stringify(self, style):
        def walk(tree: Tree, all_lines: list, line: list):
            for i, child in enumerate(tree.children):
                this_line = [*line]
                next_line = [*line]
                if i < len(tree.children) - 1:
                    this_line.append(style.tee)
                    next_line.extend([style.straight, style.space * 3])
                else:
                    this_line.append(style.elbow)
                    next_line.append(style.space * 4)

                if child.is_dir:
                    this_line.append(f' {child.name}/')
                    all_lines.append(''.join(this_line))
                    walk(child, all_lines, next_line)
                else:
                    this_line.append(f' {child.name}')
                    all_lines.append(''.join(this_line))

        all_lines = ['\n' + self.name.lstrip('/') + '/']
        walk(self, all_lines, ['  '])
        return '\n'.join(all_lines)


def make_tree(dir, exclude_patterns=None, style: Literal['normal', 'heavy', 'double'] = 'normal'):
    tree = Tree(path=dir, name=dir, is_dir=True, exclude_dirs=exclude_patterns)
    tree.build()
    style = styles[style]
    output = tree.stringify(style)
    return output


def main():
    parser = argparse.ArgumentParser(description="Print directory tree")
    parser.add_argument("directory", nargs="?", default=".",
                        help="Directory to start from (default: current directory)")
    parser.add_argument("-e", "--exclude", nargs="+", default=[], help="Exclude folders and files using glob patterns")
    parser.add_argument('-s', '--style', default='normal', choices=['normal', 'heavy', 'double'],
                        help='The style of lines to draw')
    args = parser.parse_args()

    output = make_tree(args.directory, args.exclude, args.style)
    print(output)


if __name__ == "__main__":
    main()
