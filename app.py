import os
from flask import abort, Flask, render_template, request, send_file, url_for

app = Flask(__name__)
app.config.from_object(os.environ.get('CONFIG', 'config.ProdConfig'))

@app.route('/')
@app.route('/<path:path>')
def file_list(path=''):
    basedir = app.config['FILE_PATH']
    real_path = os.path.realpath(os.path.join(basedir, path))
    human_path = path.rstrip('/') + '/'

    if not real_path.startswith(basedir):
        abort(400)
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
            } for e in list(os.scandir(real_path))]

        path_parts = list(filter(bool, path.split('/')))
        breadcrumbs = []
        if path and path != '/':
            breadcrumbs.append({
                'name': 'Root',
                'url': url_for('file_list'),
                'last': False,
            })
            for i in range(len(path_parts) - 1):
                breadcrumbs.append({
                    'name': path_parts[i],
                    'url': url_for('file_list', path='/'.join(path_parts[:i+1]) + '/'),
                    'last': False,
                })
            breadcrumbs[-1]['last'] = True

        return render_template('list.html', path=human_path, entries=entries,
            breadcrumbs=breadcrumbs)
    elif os.path.isfile(real_path):
        return 'file handling not implemented'
        # return send_file(real_path)
    else:
        abort(403)
