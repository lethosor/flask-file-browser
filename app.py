import hashlib
import os
import time

import humanize
import jinja2
import markdown
import redis

from flask import abort, Flask, render_template, request, safe_join, send_from_directory, url_for

README_NAME = 'README.md'

app = Flask(__name__)
app.config.from_object('config')

redis_client = redis.Redis('redis')

fa_icons = {
    ('txt', 'md', 'rst', 'log', 'conf', 'ini'): 'file-alt',
    ('zip', 'tar', 'gz', 'bz2', 'xz', 'z', 'rar', '7z'): 'file-archive',
    ('pdf'): 'file-pdf',
    ('doc', 'docx'): 'file-word',
    ('xls', 'xlsx'): 'file-excel',
    ('ppt', 'pptx'): 'file-powerpoint',
    ('jpg', 'jpeg', 'gif', 'png', 'bmp', 'tif', 'tiff', 'ico', 'icn', 'icns'): 'file-image',
    ('mp3', 'ogg', 'wav', 'aac', 'aif', 'aifc', 'aiff', 'flac', 'm4a', 'mid',
        'midi', 'mp2', 'mpa', 'oga', 'snd', 'swa', 'w64', 'wma'): 'file-audio',
    ('mp4', 'webm', 'mkv', 'flv', 'vob', 'ogv', 'drc', 'gifv', 'mng', 'avi',
        'mov', 'qt', 'wmv', 'yuv', 'rm', 'rmvb', 'asf', 'amv', 'm4p', 'm4v',
        'mpg', 'mp2', 'mpeg', 'mpe', 'mpv', 'mpg', 'mpeg', 'm2v', 'svi', '3gp',
        '3g2', 'mxf', 'roq', 'nsv', 'f4v', 'f4p', 'f4a', 'f4b'): 'file-video',
}
def guess_fa_icon(filename, is_folder=False):
    if is_folder:
        return 'folder-open'
    for part in map(str.lower, reversed(filename.split('.'))):
        for k, v in fa_icons.items():
            if k == part or (isinstance(k, tuple) and part in k):
                return v
    return 'file'

def get_download_count(path):
    if not os.path.isfile(path):
        return None
    count = redis_client.hget('file:' + path, 'downloads')
    try:
        return int(count)
    except (TypeError, ValueError):
        return 0

def incr_download_count(path):
    return redis_client.hincrby('file:' + path, 'downloads', 1)


def process_dir_entry(e, url_path, disk_path):
    downloads = get_download_count(os.path.join(disk_path, e.name))
    if downloads is None:
        downloads = ''
    return {
        'name': e.name,
        'is_file': e.is_file(),
        'url': url_for('file_list', path=os.path.join(url_path, e.name) +
            ('/' if not e.is_file() else '')),
        'stat': e.stat(),
        'icon': guess_fa_icon(e.name, not e.is_file()),
        'downloads': downloads,
    }

_static_hash_cache = {}
def append_static_file_hash(file):
    full_path = os.path.join(app.static_folder, file)
    url = app.static_url_path + '/' + file
    if os.path.isfile(full_path):
        if full_path not in _static_hash_cache:
            md5 = hashlib.md5()
            with open(full_path, 'rb') as f:
                while (chunk := f.read(2 ** 16)):
                    md5.update(chunk)
            _static_hash_cache[full_path] = md5.hexdigest()
        url += '?' + _static_hash_cache[full_path]
    return url

@app.template_filter('humanize_size')
def humanize_size(size):
    return humanize.naturalsize(size)

@app.template_filter('date_time')
def date_time_filter(raw):
    return time.strftime('%c %Z', time.localtime(raw))

@app.context_processor
def add_utils():
    return {'static_path': append_static_file_hash}

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
        entries = [process_dir_entry(e, path, real_path)
            for e in list(os.scandir(real_path))
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
            breadcrumbs=breadcrumbs, readme_html=jinja2.Markup(readme_html))
    elif os.path.isfile(real_path):
        incr_download_count(real_path)
        return send_from_directory(app.config['FILE_PATH'], path)
    else:
        abort(403)
