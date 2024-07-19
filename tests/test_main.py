from pytree.cli import make_tree

def test_main(fs):
    exp = """
 var/
  ├── .gitignore
  ├── data/
  │   ├── more/
  │   │   └── xx3.txt
  │   ├── xx1.txt
  │   └── xx2.txt
  └── other/
      └── yy1.txt
      """.strip()

    fs.create_file('/var/data/xx1.txt')
    fs.create_file('/var/data/xx2.txt')
    fs.create_file('/var/data/more/xx3.txt')
    fs.create_file('/var/other/yy1.txt')
    fs.create_file('/var/.idea/zz1.txt')
    fs.create_file('/var/.gitignore')
    output = make_tree('/var')
    assert output.strip() == exp

def test_exclude(fs):
    fs.create_file('/var/data/xx1.txt')
    fs.create_file('/var/data/xx2.txt')
    fs.create_file('/var/data/more/xx3.txt')
    fs.create_file('/var/other/yy1.txt')
    fs.create_file('/var/other/.idea/foo.bar')

    # Exclude entire folder
    exclude = ['*/data']
    exp = """
var/
  └── other/
      └── yy1.txt
      """.strip()
    output = make_tree('/var', exclude_patterns=exclude)
    assert output.strip() == exp

    # Exclude contents but keep folder name
    exclude = ['*/data/*']
    exp = """
var/
  ├── data/
  └── other/
      └── yy1.txt
      """.strip()
    output = make_tree('/var', exclude_patterns=exclude)
    assert output.strip() == exp


def test_style(fs):
    fs.create_file('/var/data/xx1.txt')
    fs.create_file('/var/other/yy1.txt')
    exp = """
var/
  ╠══ data/
  ║   ╚══ xx1.txt
  ╚══ other/
      ╚══ yy1.txt
    """.strip()
    output = make_tree('/var', style='double')
    assert output.strip() == exp

