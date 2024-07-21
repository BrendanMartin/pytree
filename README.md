# pytree

`pytree` is a CLI tool for printing a directory tree. Originally created to replicate the `tree` Unix command on Windows, and to display project directories in tutorials on [learndatasci.com](https://www.learndatasci.com) and [brmartin.com](https://brmartin.com)

## Installation

To install `pytree`, you can use `pip`:

```
pip install pytree
```

## Usage

```
pytree [directory] [options]
```

### Arguments

- `directory` (optional): The directory to start from. If not specified, the current directory is used by default.

### Options

- `-i`, `--ignore`: Ignore folders and files using glob patterns. You can specify multiple patterns to exclude.
- `-s`, `--sort`: Sort directory contents alphabetically.
- `-st`, `--style`: The style of lines to draw in the tree. Choices are:
    - `normal`: Standard line style (default). Ex: '│'
    - `heavy`: Heavy line style for a bolder look. Ex: '┃'
    - `double`: Double line style for fun. Ex: '║'

## Examples

Print the directory tree for the current directory

```
pytree
```

Print the directory tree for a specified directory

```
pytree /path/to/directory
```

Ignore specific folders and files using .gitignore style glob patterns

```
pytree -i "*.pyc" "__pycache__"
```

Ignore the contents of a folder but keep the folder's name

```
pytree -i "*/dir/*" "!*/dir/"
```

Sort directory contents alphabetically

```
pytree -s
```

Use a different line style

```
pytree -st heavy
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.