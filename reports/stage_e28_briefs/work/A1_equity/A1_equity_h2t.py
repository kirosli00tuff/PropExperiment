"""A1_equity: strip HTML to text, write <file>.txt beside it, print line count."""
import re
import sys
from html.parser import HTMLParser

BLOCK = {'br', 'p', 'div', 'tr', 'li', 'h1', 'h2', 'h3', 'h4', 'td', 'th', 'dt', 'dd', 'section', 'table'}


class Stripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.out = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ('script', 'style', 'noscript'):
            self.skip += 1
        if tag in BLOCK:
            self.out.append('\n')

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript') and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.out.append(data)


for path in sys.argv[1:]:
    p = Stripper()
    p.feed(open(path, encoding='utf-8', errors='replace').read())
    text = re.sub(r'[ \t\r\f\v]+', ' ', ''.join(p.out))
    text = re.sub(r'\n\s*\n+', '\n', text)
    with open(path + '.txt', 'w') as fh:
        fh.write(text)
    print(path.rsplit('/', 1)[-1], len(text.splitlines()))
