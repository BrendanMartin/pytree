from pathlib import Path
import pytest

from pytree.cli import Tree

pytree_ignore_path = Path(__file__).parent.parent/'pytree/.pytreeignore'

@pytest.fixture
def pytree_ignore(fs):
    fs.add_real_file(pytree_ignore_path)
    yield fs

@pytest.mark.usefixtures("pytree_ignore")
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
    fs.create_file('/var/.git/logs/HEAD')
    output = Tree('/var', sort=True).build().stringify()
    # assert output.strip() == exp
    print(output)

@pytest.mark.usefixtures("pytree_ignore")
def test_ignore(fs):
    fs.create_file('/var/data/xx1.txt')
    fs.create_file('/var/data/xx2.txt')
    fs.create_file('/var/data/more/xx3.txt')
    fs.create_file('/var/other/yy1.txt')
    fs.create_file('/var/other/.idea/foo.bar')

    # Exclude entire folder
    ignore = ['*/data']
    exp = """
var/
  └── other/
      └── yy1.txt
      """.strip()
    output = Tree('/var', sort=True, ignore_patterns=ignore).build().stringify()
    assert output.strip() == exp

@pytest.mark.usefixtures("pytree_ignore")
def test_ignore_keep_folder_name(fs):
    fs.create_file('/var/data/xx1.txt')
    fs.create_file('/var/data/xx2.txt')
    fs.create_file('/var/data/more/xx3.txt')
    fs.create_file('/var/other/yy1.txt')
    fs.create_file('/var/other/.idea/foo.bar')

    ignore = ['*/data/*', '!*/data/']
    exp = """
var/
  ├── data/
  └── other/
      └── yy1.txt
      """.strip()
    output = Tree('/var', ignore_patterns=ignore, sort=True).build().stringify()
    assert output.strip() == exp


@pytest.mark.usefixtures("pytree_ignore")
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
    output = Tree('/var', sort=True, style='double').build().stringify()
    assert output.strip() == exp

@pytest.mark.usefixtures("pytree_ignore")
def test_pytree_ignore(fs):
    fs.create_file('/var/venv/Scripts/activate.bat')
    fs.create_file('/venv/Scripts/activate.bat')
    fs.create_file('/var/data/xx1.txt')
    output = Tree('/var', sort=True).build().stringify()
    print(output)

