Caleenbourg
===========

Caleenbourg is a command line utility producinc word sequences which sound like an input sentence.

For the moment only french language is supported through the ["Open Lexicon" database](http://www.lexique.org/).

## Quick start 

You can start using this program by installing it with pip:

```sh
pip install git+https://github.com/fbessou/caleenbourg
```

You can now run it with the following command:

```
caleenbourg "cale en bourg"
```

## Development

Clone this repository and run the following commands:

```sh
python3 -m virtualenv -p python3 env
. env/bin/activate
pip install -e .
```

You can now start modifying the code and run it.

```sh
caleenbourg "cale en bourg"
```
