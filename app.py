import os
import time

import humanize
import markdown

from flask import abort, Flask, render_template, request, safe_join, send_from_directory, url_for

README_NAME = 'README.md'

app = Flask(__name__)
app.config.from_object(os.environ.get('CONFIG', 'config.ProdConfig'))

fa_icons = {
    'txt': 'file-alt',
    'zip': 'file-archive',
    'tar': 'file-archive',
    'pdf': 'file-pdf',
}
def guess_fa_icon(filename, is_folder=False):
    if is_folder:
        return 'folder-open'
    for part in reversed(filename.split('.')):
        if part in fa_icons:
            return fa_icons[part]
    return 'file'

@app.template_filter('humanize_size')
def humanize_size(size):
    return humanize.naturalsize(size)

@app.template_filter('date_time')
def date_time_filter(raw):
    return time.strftime('%c %Z', time.localtime(raw))

@app.route('/')
@app.route('/<path:path>')
def file_list(path=''):
    real_path = safe_join(app.config['FILE_PATH'], path)
    human_path = path.rstrip('/') + '/'

    if not os.path.exists(real_path):
        abort(404)

    if os.path.isdir(real_path):
        if not path.endswith('/'):
            path += '/'
        entries = [{
                'name': e.name,
                'is_file': e.is_file(),
                'url': url_for('file_list', path=os.path.join(path, e.name) +
                    ('/' if not e.is_file() else '')),
                'stat': e.stat(),
                'icon': guess_fa_icon(e.name, not e.is_file()),
            } for e in list(os.scandir(real_path))
                if e.name != README_NAME and not e.name.startswith('.')]
        # folders on top, then alphabetically
        entries.sort(key=lambda e: (e['is_file'], e['name']))

        path_parts = list(filter(bool, path.split('/')))
        breadcrumbs = [{
            'name': 'Root',
            'url': url_for('file_list'),
            'last': False,
        }]
        for i in range(len(path_parts)):
            breadcrumbs.append({
                'name': path_parts[i],
                'url': url_for('file_list', path='/'.join(path_parts[:i+1]) + '/'),
                'last': False,
            })
        breadcrumbs[-1]['last'] = True

        readme_path = os.path.join(real_path, README_NAME)
        readme_html = ''
        try:
            if os.path.isfile(readme_path):
                with open(readme_path) as f:
                    readme_html = markdown.markdown(f.read())
        except Exception:
            readme_html = '<div class="alert alert-warning">Could not parse folder description</div>'

        return render_template('list.html', path=human_path, entries=entries,
            breadcrumbs=breadcrumbs, readme_html=readme_html)
    elif os.path.isfile(real_path):
        return send_from_directory(app.config['FILE_PATH'], path)
    else:
        abort(403)
