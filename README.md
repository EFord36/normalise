![Title Logo](logo.png)

> A module for normalising text. 

## Introduction

This module takes a text as input, and returns it in a fully normalised form, *ie.* expands everything that is not in a standard, readable format. Non-standard words (NSWs) are detected, classified and expanded. Examples of NSWs that are normalised include:

* Numbers - percentages, dates, currency amounts, ranges, telephone numbers.
* Abbreviations and acronyms.
* Web addresses and hashtags.


## Table of Contents
* [Installation](#installation)
* [Usage](#usage)
* [Authors](#authors)
* [License](#license)
* [Acknowledgements](#acknows)


## <a name="installation"><a/>Installation

To install the module (on Windows, Mac OS X, Linux, etc.) and to ensure that you have the latest version of pip and setuptools:

```
$ pip install --upgrade pip setuptools

$ pip install normalise
```

If `pip` installation fails, you can try `easy_install normalise`. 


## <a name="usage"><a/>Usage

Your input text can be a list of words, or a string. 

To normalise your text, use the `normalise` function. This will return the text with NSWs replaced by their expansions:

```python
text = ["On", "the", "28", "Apr.", "2010", ",", "Dr.", "Banks", "bought", "a", "chair", "for", "£35", "."]

normalise(text, verbose=True)

Out: 
['On',
 'the',
 'twenty-eighth of',
 'April',
 'twenty ten',
 ',',
 'Doctor',
 'Banks',
 'bought',
 'a',
 'chair',
 'for',
 'thirty five pounds',
 '.']
```

`verbose=True` displays the stages of the normalisation process, so you can monitor its progress. To turn this off, use `verbose=False`. 

If your input is a string, you can use our basic tokenizer. For best results, input your own custom tokenizer.

```python
normalise(text, tokenizer=tokenize_basic, verbose=True)
```

In order to see a list of all NSWs in your text, along with their index, tags, and expansion, use the `list_NSWs` function:

```python
list_NSWs(text)

Out:
({3: ('Apr.', 'ALPHA', 'EXPN', 'April'),
  6: ('Dr.', 'ALPHA', 'EXPN', 'Doctor')},
 {2: ('28', 'NUMB', 'NORD', 'twenty-eighth of'),
  4: ('2010', 'NUMB', 'NYER', 'twenty ten'),
  12: ('£35', 'NUMB', 'MONEY', 'thirty five pounds')}
 ```

## <a name="authors"><a/>Authors

* **Elliot Ford** - [EFord36](https://github.com/EFord36)
* **Emma Flint** - [emmaflint27](https://github.com/emmaflint27)

## <a name="license"><a/>License

This project is licensed under the terms of the GNU General Public License version 3.0 or later.

Please see [LICENSE.txt](https://github.com/EFord36/normalise/blob/master/LICENSE.txt) for more information. 

## <a name="acknows"><a/>Acknowledgements

This project builds on the work described in [Sproat et al (2001)](http://www.cs.toronto.edu/~gpenn/csc2518/sproatetal01.pdf). 

We would like to thank Andrew Caines and Paula Buttery for supervising us during this project. 
