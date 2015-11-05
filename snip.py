#!/usr/bin/python
import json
import yaml
import sys
import re
import importlib
from os.path import expanduser
home = expanduser("~")
escape_chars = {
    '+': '\+'
    }

'''
OPTIONALS PACKAGES; pyperclip and colorama
'''


imported_libs = {
    'pyperclip': False,
    'colorama': False
}


class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

colorama = Struct(**{
    'Fore': Struct(**dict(zip(
        ['GREEN', 'RED', 'MAGENTA', 'YELLOW', 'CYAN', 'BLUE', 'RESET'],
        ['']*7))),
    'Style': Struct(**dict(zip(
        ['BRIGHT', 'RESET', 'RESET_ALL'],
        ['']*3)))
})
pyperclip = None


def imp_package(package):
    global imported_libs
    try:
        globals()[package] = importlib.import_module(package)
        imported_libs[package] = True
    except ImportError:
        pass
imp_package('pyperclip')
imp_package('colorama')


'''
GLOBAL DATA
'''


filename = home+"/.snipdata.json"
and_chars = ['&', '+']
try:
    with open("snip.conf.yaml", "r") as stream:
        conf_data = yaml.load(stream)
        filename = conf_data['data_file']
        if filename[0] == '~':
            filename = home + filename[1:]
        and_chars = conf_data['and_chars']
except IOError:
    print_fail('No conf file found')
    pass
args = sys.argv[1:]
data = []
add_tag_added, add_tag_total = 0, 0
options = {
    'show-desc': True,
    'show-tags': False,
    'show-snip': False,
    'search': 'tags'
}
options_arg = [{
        'args': ['-s', '--output-search'],
        'desc': 'shows snippet in output',
        'fields': ['show-snip'],
        'setto': [True]
    }, {
        'args': ['-t', '--output-tags'],
        'desc': 'shows tags in output',
        'fields': ['show-tags'],
        'setto': [True]
    }, {
        'args': ['-o', '--output-all'],
        'desc': 'shows all in output',
        'fields': ['show-tags', 'show-snip'],
        'setto': [True, True]
    }, {
        'args': ['-a', '--search-all'],
        'desc': 'search in all fields',
        'fields': ['search'],
        'setto': ['all']
    }
]


'''
CUSTOM EXCEPTION
'''


class InvalidArgs(Exception):
    pass


def args_must_be(n):
    global args
    if len(args) < n:
        raise InvalidArgs('Invalid args number')


'''
PRETTY PRINT UTILS
'''


def print_ok(s):
    print ''+colorama.Fore.GREEN + s + colorama.Fore.RESET


def print_fail(s):
    print ''+colorama.Fore.RED + s + colorama.Fore.RESET


def print_warning(s):
    print ''+colorama.Fore.YELLOW + s + colorama.Fore.RESET


def print_input(s):
    print ''+colorama.Fore.MAGENTA + s + colorama.Fore.RESET


def print_cyan(s):
    print ''+colorama.Fore.CYAN + s + colorama.Fore.RESET


def print_options():
    global options_arg
    for o in options_arg:
        print_cyan('--> '+'|'.join(o['args'])+' --> '+o['desc'])


def show_entries(output):
    global options
    if len(output) == 0:
        print_warning('no matches')
        return
    c = 0
    for entry in output:
        print colorama.Style.BRIGHT + '%3d)' % (c) + '-'.join([' ']*20) + colorama.Style.RESET_ALL
        if options['show-desc']:
            print colorama.Fore.CYAN + '     DESC: ' +\
                colorama.Style.BRIGHT + ' %s' % (entry['desc']) +\
                colorama.Style.RESET_ALL + colorama.Fore.RESET
        if options['show-tags']:
            print colorama.Fore.YELLOW + '     TAGS: ' +\
                colorama.Style.BRIGHT + ' %s' % ' - '.join(sorted(entry['tags'])) +\
                colorama.Style.RESET_ALL + colorama.Fore.RESET
        if options['show-snip']:
            rows = entry['snip'].split('\n')
            if len(rows) == 0:
                print colorama.Fore.BLUE + '     SNIP: ' +\
                      colorama.Style.BRIGHT + ' %s' % entry['snip'] +\
                      colorama.Style.RESET_ALL + colorama.Fore.RESET
            else:
                print colorama.Fore.BLUE + '     SNIP: ' +\
                      colorama.Style.BRIGHT + ' %s' % '\n            '.join(rows) +\
                      colorama.Style.RESET_ALL + colorama.Fore.RESET
        c += 1


def short(s, maxlen=20):
    shorts = s
    if len(s) > maxlen:
        shorts = s[:maxlen-3] + '...'
    return shorts

'''
DATA HANDLING FUNCTIONS
'''


def copy_func(output, index):
    global imported_libs
    s = output[index]['snip']
    if imported_libs['pyperclip']:
        pyperclip.copy(s)
        print_ok('Copyied #'+str(index)+' to clipboard: "'+short(s)+'"')
    else:
        print_fail('Clipboard module is not active')


def meta_search(regex):
    global data
    global options
    global and_chars
    global escape_chars
    pattern, output, index_list, counter = [], [], [], 0

    for i in range(0, len(and_chars)):
        if and_chars[i] in escape_chars:
            and_chars[i] = escape_chars[and_chars[i]]
    for r in re.split(r""+'|'.join(and_chars), regex):
        pattern.append(re.compile(r, re.IGNORECASE))
    for entry in data:
        matching = True
        if options['search'] == 'all':
            analyzed = entry['desc']+' '+entry['snip']+' '+' '.join(entry['tags'])
        else:
            analyzed = ' '.join(entry['tags'])
        for p in pattern:
            matching = matching and bool(p.search(analyzed))
        if matching:
            output.append(entry)
            index_list.append(counter)
        counter += 1
    return output, index_list


'''
READ and WRITE DATA
'''


def data_read():
    global data
    try:
        datafile_in = open(filename, "r")
        data = json.loads(datafile_in.read())
        datafile_in.close()
    except IOError:
        print_fail('No data found')
        pass
    return data


def data_dump():
    global data
    datafile_out = open(filename, "w")
    datafile_out.write(json.dumps(data))
    datafile_out.close()


'''
ARGS HANDLING
'''


def read_arg():
    global options
    global options_arg
    global args
    if len(args) == 0:
        return None
    if args[0][0] == '-':
        # is an option
        if args[0][1] != '-':
            # is a short option
            inp_args = set(['-' + _ for _ in list(args[0][1:])])
            done = False
            for oa in options_arg:
                if len(inp_args.intersection(set(oa['args']))) > 0:
                    done = True
                    for f in range(0, len(oa['fields'])):
                        options[oa['fields'][f]] = oa['setto'][f]
        else:
            # is a long option
            done = False
            for oa in options_arg:
                if args[0] in oa['args']:
                    done = True
                    for f in range(0, len(oa['fields'])):
                        options[oa['fields'][f]] = oa['setto'][f]
        if not done:
            raise InvalidArgs('Invalid options')
        args = args[1:]
        return read_arg()
    toret = args[0].strip()
    args = args[1:]
    return toret


'''
MAIN
'''


def main():
    global data
    global options
    global args
    global add_tag_added
    global add_tag_total
    try:
        if len(args) < 1 or args[0] == 'h' or args[0] == 'help':
            print_warning('usage: snip [options] cmd <args>')
            print_cyan('usage: <*arg> mandatory argument')
            print_cyan('usage: <arg> optional argument')
            print_ok('options:')
            print_options()
            print_ok('cmd and args:')
            print_cyan('--> s|search <regex>\n' +
                       '    list all entries or filter by <regex>')

            print_cyan('--> i|insert\n' +
                       '    insert an entry, snippet must already be in clipboard')
            print_cyan('--> d|delete <*regex> <index>\n' +
                       '    delete all entries identified by <regex>, or only the\n' +
                       '    one in the <index> position')

            print_cyan('--> t|attach <*tag> <*regex>\n' +
                       '    append the <tag> to entries identifies by <regex>')
            print_cyan('--> r|remtag <*tag> <*regex>\n' +
                       '    to remove the <tag> to all entries identifies by <regex>')

            print_cyan('--> h|help: print this snip')
            return
        data = data_read()

        cmd = read_arg()
        if cmd in ['s', 'search']:
            args_must_be(0)
            to_search = '.*'
            if len(args) >= 1:
                to_search = args[0]
            output, _ = meta_search(to_search)
            show_entries(output)
            if len(args) == 2:
                copy_func(output, int(args[1]))
        elif cmd in ['t', 'attach']:
            args_must_be(2)
            tag, regex = args[0], args[1]
            output, index_list = meta_search(regex)
            for i in reversed(index_list):
                add_tag_total += 1
                if tag not in data[i]['tags']:
                    add_tag_added += 1
                    data[i]['tags'].append(tag)
            show_entries(output)
            print_ok('Added tag "%s" to %d/%d entry' % (tag, add_tag_added, add_tag_total))
            data_dump()
        elif cmd in ['i', 'insert']:
            print_input('Desc: ')
            desc = raw_input()
            if imported_libs['pyperclip']:
                snip = pyperclip.paste()
                print_input('Snip: \n'+snip+'\n')
            else:
                print_input('Snip: ')
                snip = raw_input()
            print_input('Tags: ')
            tags = re.split(r'-| |,', raw_input())
            data.append({'desc': desc, 'tags': tags, 'snip': snip})
            data_dump()
            print_ok('Inserted')
        elif cmd in ['d', 'delete']:
            args_must_be(1)
            regex = args[0]
            index = -1 if len(args) < 2 else int(args[1])
            output, index_list = meta_search(regex)
            show_entries(output)
            if index != -1:
                del data[index_list[index]]
                print_ok('Deleted 1 entry')
            else:
                for i in reversed(index_list):
                    del data[i]
                print_ok("Deleted %d entries" % (len(index_list)))
            data_dump()
        else:
            raise InvalidArgs('Command "%s" not found' % cmd)

    except InvalidArgs as e:
        print_fail(str(e))

    finally:
        pass

if __name__ == "__main__":
    main()
