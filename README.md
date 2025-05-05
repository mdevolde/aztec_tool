# Aztec tool 🛸
[![aztec tool on pypi](https://badge.fury.io/py/aztec-tool.svg)](https://pypi.org/project/aztec-tool/)
[![Test with PyTest](https://github.com/mdevolde/aztec_tool/workflows/Test%20with%20PyTest/badge.svg)](https://github.com/mdevolde/aztec_tool/actions)
[![codecov](https://codecov.io/gh/mdevolde/aztec_tool/branch/master/graph/badge.svg)](https://codecov.io/gh/mdevolde/aztec_tool)
[![Python Versions](https://img.shields.io/pypi/pyversions/aztec-tool.svg)](https://devguide.python.org/versions/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg?style=flat)](https://github.com/mdevolde/aztec_tool/pulls)

*A fast, pure‑Python Aztec Code reader with auto‑orientation and Reed-Solomon correction.*

-------------
## Table of content
1. [Installation](#installation)
2. [Usage](#usage)
3. [Useful links](#useful-links)
   - [Contributing](#contributing)
   - [Security](#security)
   - [Changelog](#changelog)
   - [TODO](#todo)
   - [License](#license)
   - [Code of Conduct](#code-of-conduct)
6. [Resources](#Resources)

## Installation

This library is compatible with **Python 3.9** and above.

To install the latest version of Aztec tool, you can use pip. Open your terminal and run the following command (in a virtual environment if you want to keep your system clean):

```bash
pip install --upgrade aztec_tool
```

If you cloned the repository, you can install it using pip as well, in the root directory of the project:

```bash
pip install --upgrade .
```

This library installs the following dependencies:
- [OpenCV](https://pypi.org/project/opencv-python/) for image processing
- [NumPy](https://pypi.org/project/numpy/) for numerical operations
- [Reed-Solomon](https://pypi.org/project/reedsolo/) for error correction
- [toml](https://pypi.org/project/toml/) for version reading

## Usage
The library allows you to decode Aztec barcodes from images. First, you need to have your Aztec barcode perfectly cropped in an image.

The most common way to use the library is to use the `AztecDecoder` class. You can create an instance of the class and call the `decode` method with the path to the image file as an argument:

```python
>>> from aztec_tool import decode
>>> decode("welcome_lib.jpg")
'Welcome to Aztec tool lib !'
>>>
```

If you need to access more specific data, you can use the `AztecDecoder` class directly:

```python
>>> from aztec_tool import AztecDecoder
>>> decoder = AztecDecoder("welcome_lib.jpg")
>>> decoder.aztec_type
<AztecType.COMPACT: 0>
>>> decoder.mode_info
{'layers': 3, 'data_words': 21, 'ecc_bits': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0]}
>>> decoder.decode()
'Welcome to Aztec tool lib !'
```

When you're using the `decode` function or the `AztecDecoder` class, you can also pass three optional parameters:
- `auto_orient`: Default is `True`. If set to `True`, the image will be automatically rotated to the correct orientation before decoding. This is useful if the barcode is reversed or rotated.
- `auto_correct`: Default is `True`. If set to `True`, the data in the Aztec barcode will be automatically corrected. This is useful if the barcode is damaged or has errors.
- `auto_mode_correct`: Default is `True`. If set to `True`, the mode data in the Aztec barcode will be automatically corrected. This is useful if the barcode is damaged or has errors.

If you have some problems with the correction, it can be useful to set `auto_correct` and/or `auto_mode_correct` to `False`.

If you need very specific data, you can access the `AztecDecoder` class attributes, or directly the various classes used in the library.

This library has its own exceptions. You can find them in the `exceptions.py` file. The most common exception is `AztecDecoderError`, which is the parent class of all the exceptions in the library.

The tool is also available as a command line interface (CLI). You can use it by running the following command in your terminal:

```bash
$ aztec-tool welcome_lib.jpg
Welcome to Aztec tool lib !
```

If you want to print the metadata of the Aztec code, you can use the `--info` option:

```bash
$ aztec-tool welcome_lib.jpg --info
Type:         COMPACT
Layers:       3
Data words:   21
ECC bits:     01010101010010101000
```

You can view all available options by running `aztec-tool -h`.

## Useful links
### Contributing
Contributions are welcome! If you want to contribute to the project, please read the [CONTRIBUTING.md](CONTRIBUTING.md) file.

### Security
If you discover any security vulnerabilities, please read the procedure in the [SECURITY.md](SECURITY.md) file.

### Changelog
The full changelog is available in the [CHANGELOG.md](CHANGELOG.md) file.

### TODO
The plan for the next releases is available in the [TODO.md](TODO.md) file.

### License
The Aztec tool is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

### Code of Conduct
The Aztec tool is committed to providing a friendly, safe, and welcoming environment for all. Please read the [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) file for more details.

## Resources
These resources were very useful to understand the Aztec code and build this library:
- [Wikipedia - Aztec code](https://en.wikipedia.org/wiki/Aztec_Code)
- [Youtube - How to Decode the Aztec Code](https://www.youtube.com/watch?v=xtlqYx6e1TE)
- ISO/IEC 24778:2024: Information technology - Automatic identification and data capture techniques - Aztec Code bar code symbology specification
