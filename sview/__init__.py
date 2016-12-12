import flask
import os
import re
import shutil
import sys

from pathlib import Path
from livereload import Server
from sphinx.application import Sphinx
from textwrap import dedent

def find_includes(original_path):
    print("looking for includes in {}".format(original_path.parent))
    with open(str(original_path), 'r') as original_file:
        for line in original_file.readlines():
            match = re.search(r'\.\. (?:literal)?include::\s*([^\s]+)', line)
            if match is not None:
                print("found a match in in {}".format(line))
                include = match.group(1)
                print("match was {}".format(include))
                include_path = original_path.parent / include
                print("include path {}".format(include_path))
                yield include_path

def rm(dst):
    if dst.exists():
        if dst.is_dir():
            shutil.rmtree(str(dst))
        else:
            os.remove(str(dst))

def copy(src, dst):
    if src.is_dir():
        shutil.copytree(str(src), str(dst))
    else:
        shutil.copy(str(src), str(dst))

def build(target, working_dir, source_dir):
    """
    Rebuilds a target in a specified working directory

    .. todo::
        - replace .. in paths with 'up' (also in source files)
        - recursive includes
        - link copy as well
        - replace prints with logging
    """
    build_dir = Path(working_dir, 'build')

    rm(build_dir)
    build_dir.mkdir(parents=True)

    source_suffix = None
    original_path = Path(target)
    if original_path.is_dir():
        found_index = False
        for element_path in original_path.glob('*'):
            final_path = build_dir / element_path.name
            print("Final path is: {}".format(final_path))
            if element_path.stem == 'index' and not element_path.is_dir():
                found_index = True
                source_suffix = element_path.suffix
            copy(element_path, final_path)
        if not found_index:
            raise Exception("Couldn't find index in {}".format(original_path))
    else:
        source_suffix = original_path.suffix
        final_path = build_dir / ('index' + source_suffix)
        copy(original_path, final_path)

        for include_path in find_includes(original_path):
            rel_include_path = include_path.relative_to(original_path.parent)
            print("relative include path: {}".format(rel_include_path))
            final_include_path = build_dir / rel_include_path
            final_include_path.parent.mkdir(parents=True)
            print("copying {} to {}".format(include_path, final_include_path))
            copy(include_path, final_include_path)

    conf_content = dedent("""
        source_suffix = '{}'
        master_doc = 'index'
        html_theme = 'alabaster'
        html_static_path = ['_static']
    """).format(source_suffix)

    if source_dir is not None:
        conf_content = conf_content + dedent("""
            extensions = ['sphinx.ext.autodoc']
            import sys
            sys.path.insert(0, '{}')
        """).format(source_dir)

    conf_path = build_dir / 'conf.py'
    with open(str(conf_path), 'w') as conf_file:
        conf_file.write(conf_content)

    build_dir_str = str(build_dir)
    build_dir_str = str(build_dir)
    builder = Sphinx(build_dir_str, build_dir_str, build_dir_str, build_dir_str, 'html')
    builder.build()


def create_server(**config):
    """
    Creates a new flask app and wraps it in a livereload server
    """
    working_dir = config.get('WORKING_DIR')
    target_path = config.get('TARGET')
    source_dir = config.get('SOURCE_DIR')
    template_folder = os.path.join(working_dir, 'build')
    static_folder = os.path.join(template_folder, '_static')

    build(target_path, working_dir, source_dir)

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

    @app.route('/<path:page>')
    def subpage(page):
        return flask.render_template(page)

    app.logger.debug("configuring livereload server")
    server = Server(app.wsgi_app)
    app.logger.debug("setting watch for target: {}".format(target_path))
    server.watch(
        target_path,
        lambda: build(target_path, working_dir, source_dir),
    )
    app.logger.debug("Finished creating server")
    return server
