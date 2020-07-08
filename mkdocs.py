#!/usr/bin/env python3

import markdown
import os
import re
import shutil
import sys
import webbrowser

root_dir = os.path.abspath(os.path.dirname(__file__))
docs_dir = os.path.join(root_dir, 'docs')
html_dir = os.path.join(root_dir, 'html')

local = '--deploy' not in sys.argv
preview = '-p' in sys.argv

if local:
    base_url = 'file://%s/' % os.path.normpath(os.path.join(os.getcwd(), html_dir))
    suffix = '.html'
    index = 'index.html'
else:
    base_url = 'http://django-vanilla-views.org'
    suffix = ''
    index = ''


main_header = '<li class="main"><a href="#{{ anchor }}">{{ title }}</a></li>'
sub_header = '<li><a href="#{{ anchor }}">{{ title }}</a></li>'
code_label = r'<a class="github" href="https://github.com/tomchristie/django-vanilla-views/tree/master/vanilla/\1"><span class="label label-info">\1</span></a>'

with open(os.path.join(docs_dir, 'template.html'), 'r') as fp:
    page = fp.read()

# Hacky, but what the hell, it'll do the job
path_list = [
    'index.md',
    'api/base-views.md',
    'api/model-views.md',
    'migration/base-views.md',
    'migration/model-views.md',
    'topics/frequently-asked-questions.md',
    'topics/django-braces-compatibility.md',
    'topics/django-extra-views-compatibility.md',
    'topics/release-notes.md',
]

prev_url_map = {}
next_url_map = {}
for idx in range(len(path_list)):
    path = path_list[idx]
    rel = '../' * path.count('/')

    if idx > 0:
        prev_url_map[path] = rel + path_list[idx - 1][:-3] + suffix

    if idx < len(path_list) - 1:
        next_url_map[path] = rel + path_list[idx + 1][:-3] + suffix


for (dirpath, dirnames, filenames) in os.walk(docs_dir):
    relative_dir = dirpath.replace(docs_dir, '').lstrip(os.path.sep)
    build_dir = os.path.join(html_dir, relative_dir)

    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    for filename in filenames:
        path = os.path.join(dirpath, filename)
        relative_path = os.path.join(relative_dir, filename)

        if not filename.endswith('.md'):
            if relative_dir:
                output_path = os.path.join(build_dir, filename)
                shutil.copy(path, output_path)
            continue

        output_path = os.path.join(build_dir, filename[:-3] + '.html')

        toc = ''
        with open(path, 'r') as fp:
            text = fp.read()
        main_title = None
        description = 'Django, CBV, GCBV, Generic class based views'
        for line in text.splitlines():
            if line.startswith('# '):
                title = line[2:].strip()
                template = main_header
                description = description + ', ' + title
            elif line.startswith('## '):
                title = line[3:].strip()
                template = sub_header
            else:
                continue

            if not main_title:
                main_title = title
            anchor = title.lower().replace(' ', '-').replace(':-', '-').replace("'", '').replace('?', '').replace('.', '')
            template = template.replace('{{ title }}', title)
            template = template.replace('{{ anchor }}', anchor)
            toc += template + '\n'

        if filename == 'index.md':
            main_title = 'Django Vanilla Views - Beautifully simple class based views'
        else:
            main_title = 'Django Vanilla Views - ' + main_title

        prev_url = prev_url_map.get(relative_path)
        next_url = next_url_map.get(relative_path)

        content = markdown.markdown(text, extensions=['toc'])

        output = page.replace('{{ content }}', content).replace('{{ toc }}', toc).replace('{{ base_url }}', base_url).replace('{{ suffix }}', suffix).replace('{{ index }}', index)
        output = output.replace('{{ title }}', main_title)
        output = output.replace('{{ description }}', description)
        output = output.replace('{{ page_id }}', filename[:-3])

        if prev_url:
            output = output.replace('{{ prev_url }}', prev_url)
            output = output.replace('{{ prev_url_disabled }}', '')
        else:
            output = output.replace('{{ prev_url }}', '#')
            output = output.replace('{{ prev_url_disabled }}', 'disabled')

        if next_url:
            output = output.replace('{{ next_url }}', next_url)
            output = output.replace('{{ next_url_disabled }}', '')
        else:
            output = output.replace('{{ next_url }}', '#')
            output = output.replace('{{ next_url_disabled }}', 'disabled')

        output = re.sub(r'a href="([^"]*)\.md"', r'a href="\1%s"' % suffix, output)
        output = re.sub(r'<pre><code>:::bash', r'<pre class="prettyprint lang-bsh">', output)
        output = re.sub(r'<pre>', r'<pre class="prettyprint lang-py">', output)
        output = re.sub(r'<a class="github" href="([^"]*)"></a>', code_label, output)
        with open(output_path, 'w') as fp:
            fp.write(output)

if preview:
    webbrowser.open_new_tab('html/index.html')
