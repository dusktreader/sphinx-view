import flask
import os

from sphinx.application import Sphinx
from textwrap import dedent
import shutil
import webbrowser


def build(target, working_dir):
    build_dir = os.path.join(working_dir, 'build')
    source_dir = os.path.join(working_dir, 'source')
    if not os.path.exists(source_dir):
        os.mkdir(source_dir)
    target_path = os.path.join(source_dir, 'index.rst')
    shutil.copyfile(target, target_path)
    conf_path = os.path.join(source_dir, 'conf.py')
    with open(conf_path, 'w') as conf_file:
        conf_file.write(dedent(
            """
            source_suffix = '.rst'
            master_doc = 'index'
            html_theme = 'alabaster'
            html_static_path = ['_static']
            """
        ))

    builder = Sphinx(source_dir, source_dir, build_dir, build_dir, 'html')
    builder.build()


def create_app(**config):
    working_dir = config.get('WORKING_DIR')
    template_folder = os.path.join(working_dir, 'build')
    static_folder = os.path.join(template_folder, '_static')
    app = flask.Flask(
        __name__,
        static_folder=static_folder,
        template_folder=template_folder,
    )
    app.config.from_mapping(**config)

    @app.route('/')
    def index():
        return flask.render_template('index.html')

    webbrowser.open('localhost:{}'.format(app.config['SERVER_PORT']))

    return app
