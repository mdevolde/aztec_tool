# Aztec decoder 🛸
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*A fast, pure‑Python Aztec Code reader with auto‑orientation and Reed–Solomon correction.*

-------------
## Table of content
1. [Installation](#installation)
2. [Usage](#usage)
3. [Changelog](#changelog)
4. [TODO](#todo)
5. [License](#license)
6. [Resources](#Resources)

## Installation

This library is compatible with **Python 3.9** and above.

To install the latest version of Aztec decoder, you can use pip. Open your terminal and run the following command (in a virtual environment if you want to keep your system clean):

```bash
pip install --upgrade aztec_decoder
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
>>> from aztec_decoder import decode
>>> decode("welcome_lib.jpg")
'Welcome to Aztec decoder lib !'
>>>
```

If you need to access more specific data, you can use the `AztecDecoder` class directly:

```python
>>> from aztec_decoder import AztecDecoder
>>> decoder = AztecDecoder("welcome_lib.jpg")
>>> decoder.aztec_type
<AztecType.COMPACT: 0>
>>> decoder.mode_info
{'layers': 3, 'data_words': 21, 'ecc_bits': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0]}
>>> decoder.decode()
'Welcome to Aztec decoder lib !'
```

When you're using the `decode` function or the `AztecDecoder` class, you can also pass three optional parameters:
- `auto_orient`: Default is `True`. If set to `True`, the image will be automatically rotated to the correct orientation before decoding. This is useful if the barcode is reversed or rotated.
- `auto_correct`: Default is `True`. If set to `True`, the data in the Aztec barcode will be automatically corrected. This is useful if the barcode is damaged or has errors.
- `auto_mode_correct`: Default is `True`. If set to `True`, the mode data in the Aztec barcode will be automatically corrected. This is useful if the barcode is damaged or has errors.

If you have some problems with the correction, it can be useful to set `auto_correct` and/or `auto_mode_correct` to `False`.

If you need very specific data, you can access the `AztecDecoder` class attributes, or directly the various classes used in the library.

This library has his own exceptions. You can find them in the `exceptions.py` file. The most common exception is `AztecDecoderError`, which is the parent class of all the exceptions in the library.

## Changelog
The full changelog is available in the [CHANGELOG.md](CHANGELOG.md) file.

## TODO
The plan for the next releases is available in the [TODO.md](TODO.md) file.

## License
The Aztec decoder is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Resources
These resources were very useful to understand the Aztec code and build this library:
- [Wikipedia - Aztec code](https://en.wikipedia.org/wiki/Aztec_Code)
- [Youtube - How to Decode the Aztec Code](https://www.youtube.com/watch?v=xtlqYx6e1TE)
- ISO/IEC 24778:2024: Information technology - Automatic identification and data capture techniques - Aztec Code bar code symbology specification
