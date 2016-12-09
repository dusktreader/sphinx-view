import flask
import os
import shutil

from livereload import Server
from sphinx.application import Sphinx
from textwrap import dedent


def build(target, working_dir):
    """
    Rebuilds a target in a specified working directory
    """
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


def create_server(**config):
    """
    Creates a new flask app and wraps it in a livereload server
    """
    working_dir = config.get('WORKING_DIR')
    target = config.get('TARGET')
    template_folder = os.path.join(working_dir, 'build')
    static_folder = os.path.join(template_folder, '_static')
    app = flask.Flask(
        __name__,
        static_folder=static_folder,
        template_folder=template_folder,
    )
    app.debug = True
    app.config.from_mapping(**config)

    app.logger.debug("Registering route")

    @app.route('/')
    def index():
        return flask.render_template('index.html')

    app.logger.debug("configuring livereload server")
    server = Server(app.wsgi_app)
    app.logger.debug("setting watch for target: {}".format(target))
    server.watch(target, lambda: build(target, working_dir))
    app.logger.debug("Finished creating server")
    return server
