import os
from flask import abort, Flask, render_template, request, send_file

app = Flask(__name__)
app.config.from_object(os.environ.get('CONFIG', 'config.ProdConfig'))

@app.route('/')
@app.route('/<path:path>')
def file_list(path=''):
    basedir = app.config['FILE_PATH']
    real_path = os.path.realpath(os.path.join(basedir, path))
    human_path = path + '/'

    if not real_path.startswith(basedir):
        abort(400)
    if not os.path.exists(real_path):
        abort(404)

    if os.path.isdir(real_path):
        return render_template('list.html', path=human_path)
    elif os.path.isfile(real_path):
        return 'file handling not implemented'
        # return send_file(real_path)
    else:
        abort(403)
