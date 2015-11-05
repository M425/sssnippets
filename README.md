# Super Simple Snippets CLI Tool

## Description

Snip is a CLI tool which can fastly store and read short snippet.

Every snippet is identified by a description (DESC), a list of tags (TAGS) and the snippet itself (SNIP).

## Feature

- Store a snip `snip i` this tool take the snippet from the system clipboard and ask to insert the DESCRIPTIONS and the TAGS
- List of all snips `snip s`
- Filter the search by tags with a regex `snip s <regex>`
- Copy a snip to the clipboard `snip s <regex> <index` the index of the resulting list is actually copied to the system clipboard
- Add a tag to all the snips found by a regex `snip t <tag> <regex>`
- Remove a tag to all the snips found by a regex `snip r <tag> <regex>`
- Delete all snips found by a regex `snip d <regex>` or just an entry with `snip d <regex> <index>`

## Modifiers and args

By default only the description is shown to the output.

- `-s | --output-search` show the Snippet to the output
- `-t | --output-tags` show the Tags to the output
- `-o | --output-all` show the Everythong to the output
- `-a | --search-all` the regex search is done among each field

## Configuration

The configuration file is named `snip.conf.yaml`
- and_chars: the chars which correspond to `and` in the regex (& is the default, but writing \& each time could be boring, <tag1>+<tag2> could be better)
- data_file: the file to store the the snippets

## Dependencies

Install the dependencies with `requirements.txt`. Even if they are not mandatory, the script checks if the libraries are installed otherwise it raises its fallback.

## Installation

No installation required, just python.
Recommended alias `alias snip="some/venv/python /path/to/snip.py"`

## Licence

GPLv3

##

I wrote this simple python script just to fit my needs, I really hope you hack this to fit yours.
