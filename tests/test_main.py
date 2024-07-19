from pytree.cli import make_tree

def test_main(fs):
    fs.create_file("/var/data/xx1.txt")
    fs.create_file("/var/data/xx2.txt")
    fs.create_file("/var/data/more/xx3.txt")
    fs.create_file("/var/other/yy1.txt")
    make_tree("/var")
