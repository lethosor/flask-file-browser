import os
import time

import humanize
import markdown

from flask import abort, Flask, render_template, request, safe_join, send_from_directory, url_for

README_NAME = 'README.md'

app = Flask(__name__)
app.config.from_object('config')

fa_icons = {
    ('txt'): 'file-alt',
    ('zip', 'tar', 'gz', 'bz2', 'xz', 'Z', 'rar', '7z'): 'file-archive',
    ('pdf'): 'file-pdf',
    ('doc', 'docx'): 'file-word',
    ('xls', 'xlsx'): 'file-excel',
    ('ppt', 'pptx'): 'file-powerpoint',
    ('jpg', 'jpeg', 'gif', 'png', 'bmp', 'tif', 'tiff', 'ico', 'icn', 'icns'): 'file-image',
    ('webm', 'mkv', 'flv', 'flv', 'vob', 'ogv', 'ogg', 'drc', 'gif', 'gifv',
        'mng', 'avi', 'mov', 'qt', 'wmv', 'yuv', 'rm', 'rmvb', 'asf', 'amv',
        'mp4', 'm4p', 'm4v', 'mpg', 'mp2', 'mpeg', 'mpe', 'mpv', 'mpg', 'mpeg',
        'm2v', 'm4v', 'svi', '3gp', '3g2', 'mxf', 'roq', 'nsv', 'flv', 'f4v',
        'f4p', 'f4a', 'f4b'): 'file-video',
}
def guess_fa_icon(filename, is_folder=False):
    if is_folder:
        return 'folder-open'
    for part in reversed(filename.split('.')):
        for k, v in fa_icons.items():
            if k == part or (isinstance(k, tuple) and part in k):
                return v
    return 'file'

@app.template_filter('humanize_size')
def humanize_size(size):
    return humanize.naturalsize(size)

@app.template_filter('date_time')
def date_time_filter(raw):
    return time.strftime('%c %Z', time.localtime(raw))

@app.errorhandler(404)
def handle_404(*_):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404

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
            'name': app.config['SITE_NAME'],
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
