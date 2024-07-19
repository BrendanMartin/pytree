import argparse
import os

straight = '│'
tee = '├──'
elbow = '└──'
space = ' '


class Tree:
    def __init__(self, name, path, is_dir=True, exclude_dirs=None):
        self.name = name
        self.path = path
        self.is_dir = is_dir
        self.children: list[Tree] = []
        self.exclude_dirs = exclude_dirs or []

    def build(self):
        for name in sorted(os.listdir(self.path)):
            path = os.path.join(self.path, name)
            if os.path.isdir(path):
                if name in self.exclude_dirs:
                    continue
                subtree = Tree(name, path, is_dir=True, exclude_dirs=self.exclude_dirs)
                self.children.append(subtree)
                subtree.build()
            else:
                leaf = Tree(name, path, is_dir=False)
                self.children.append(leaf)


def print_tree(tree: Tree):
    def walk(tree: Tree, line: list):
        for i, child in enumerate(tree.children):
            this_line = [*line]
            next_line = [*line]
            if i < len(tree.children) - 1:
                this_line.append(tee)
                next_line.extend([straight, space * 3])
            else:
                this_line.append(elbow)
                next_line.append(space * 4)

            if child.is_dir:
                this_line.append(child.name + '/')
                print(''.join(this_line))
                walk(child, next_line)
            else:
                this_line.append(child.name)
                print(''.join(this_line))

    print('\n', tree.name.lstrip('/') + '/')
    walk(tree, ['  '])


def make_tree(dir, exclude_dirs=None):
    tree = Tree(path=dir, name=dir, is_dir=True, exclude_dirs=exclude_dirs)
    tree.build()
    print_tree(tree)


def main():
    parser = argparse.ArgumentParser(description="Print directory tree with exclusions")
    parser.add_argument("directory", nargs="?", default=".",
                        help="Directory to start from (default: current directory)")
    parser.add_argument("-e", "--exclude", nargs="+", default=[], help="Directories to exclude contents from")
    args = parser.parse_args()

    # print(f"{args.directory}/")
    # print_tree(args.directory, args.exclude)
    make_tree(args.directory, args.exclude)


if __name__ == "__main__":
    main()
