import flask
import os
import re
import shutil

from livereload import Server
from sphinx.application import Sphinx
from textwrap import dedent


def find_includes(target_path):
    includes = []
    print("reading lines from {}".format(target_path))
    with open(target_path, 'r') as target_file:
        for line in target_file.readlines():
            match = re.search(r'\.\. (?:literal)?include::\s*([^\s]+)', line)
            if match is not None:
                print("found a match in in {}".format(line))
                include_path = match.group(1)
                print("match was {}".format(include_path))
                includes.append(include_path)
    print("includes found: {}".format(includes))
    return includes


def build(target_path, working_dir):
    """
    Rebuilds a target in a specified working directory

    .. todo::
        - replace .. in paths with 'up' (also in source files)
        - recursive includes
        - link copy as well
        - replace prints with logging
    """
    build_dir = os.path.join(working_dir, 'build')
    source_dir = os.path.join(working_dir, 'source')
    if not os.path.exists(source_dir):
        os.mkdir(source_dir)

    (target_dir, target) = os.path.split(target_path)
    (target_name, target_ext) = os.path.splitext(target)
    print("target_path is {}".format(target_path))
    print("target_dir is {}".format(target_dir))
    print("target is {}".format(target))
    print("target_name is {}".format(target_name))
    print("target_ext is {}".format(target_ext))
    new_target_path = os.path.join(source_dir, target)
    print("new target path is {}".format(new_target_path))
    shutil.copyfile(target_path, new_target_path)

    for include_path in find_includes(target_path):
        include_source_path = os.path.join(target_dir, include_path)
        print("include_source_path: {}".format(include_source_path))
        include_target_path = os.path.join(source_dir, include_path)
        include_target_dir = os.path.dirname(include_target_path)
        print("making: {}".format(include_target_dir))
        os.makedirs(include_target_dir, exist_ok=True)
        shutil.copyfile(include_source_path, include_target_path)

    conf_path = os.path.join(source_dir, 'conf.py')
    with open(conf_path, 'w') as conf_file:
        conf_file.write(dedent(
            """
            source_suffix = '{}'
            master_doc = '{}'
            html_theme = 'alabaster'
            html_static_path = ['_static']
            """.format(target_ext, target_name)
        ))

    builder = Sphinx(source_dir, source_dir, build_dir, build_dir, 'html')
    builder.build()


def create_server(**config):
    """
    Creates a new flask app and wraps it in a livereload server
    """
    working_dir = config.get('WORKING_DIR')
    target_path = config.get('TARGET')
    (target_dir, target) = os.path.split(target_path)
    (target_name, target_ext) = os.path.splitext(target)
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
        return flask.render_template('{}.html'.format(target_name))

    app.logger.debug("configuring livereload server")
    server = Server(app.wsgi_app)
    app.logger.debug("setting watch for target: {}".format(target))
    server.watch(target, lambda: build(target, working_dir))
    app.logger.debug("Finished creating server")
    return server
