import flask
import os
import shutil
import venv
import pip
import sys

from livereload import Server
from sphinx.application import Sphinx
from textwrap import dedent


def build(target, working_dir):
    """
    Rebuilds a target in a specified working directory. If the target is a
    directory, then all contents of the directory will be copied into the
    working directory prior to building. This function also builds a simplistic
    conf.py for sphinx-build
    """
    build_dir = os.path.join(working_dir, 'build')

    rm(build_dir)
    os.makedirs(build_dir)

    source_suffix = None
    original_path = target
    if os.path.isdir(original_path):
        found_index = False
        for element in os.listdir(original_path):
            (element_name, element_ext) = os.path.splitext(element)
            element_path = os.path.join(original_path, element)
            final_path = os.path.join(build_dir, element)
            if element_name == 'index' and not os.path.isdir(element_path):
                found_index = True
                source_suffix = element_ext
            copy(element_path, final_path)
        if not found_index:
            raise Exception("Couldn't find index in {}".format(original_path))
    else:
        (original_name, source_suffix) = os.path.splitext(original_path)
        final_path = os.path.join(build_dir, 'index' + source_suffix)
        copy(original_path, final_path)

    final_conf_path = os.path.join(build_dir, 'conf.py')
    conf_content = dedent("""
        source_suffix = '{}'
        master_doc = 'index'
        html_theme = 'alabaster'
        html_static_path = ['_static']
        extensions = ['sphinx.ext.autodoc']
    """).format(source_suffix)

    with open(final_conf_path, 'w') as conf_file:
        conf_file.write(conf_content)

    builder = Sphinx(build_dir, build_dir, build_dir, build_dir, 'html')
    builder.build()


def activate_this(venv_dir):
    """
    This function activates a virtual environment for the currently running
    python interpreter. This funciton is essentially a copy of
    'activate_this.py' from virtualenv, but since this application uses venv,
    this function had to be copied over. It has a few variations, but otherwise
    it has the same functionality
    """
    venv_dir = os.path.abspath(venv_dir)
    bin_dir = os.path.join(venv_dir, 'bin')
    old_os_path = os.environ.get('PATH', '')
    os.environ['PATH'] = bin_dir + os.pathsep + old_os_path
    if sys.platform == 'win32':
        site_packages = os.path.join(venv_dir, 'Lib', 'site-packages')
    else:
        site_packages = os.path.join(
            venv_dir, 'lib', 'python%s' % sys.version[:3], 'site-packages',
        )
    prev_sys_path = list(sys.path)
    import site
    site.addsitedir(site_packages)
    sys.real_prefix = sys.prefix
    sys.prefix = venv_dir
    # Move the added items to the front of the path:
    new_sys_path = []
    for item in list(sys.path):
        if item not in prev_sys_path:
            new_sys_path.append(item)
            sys.path.remove(item)
    sys.path[:0] = new_sys_path


def create_server(**config):
    """
    Creates a new flask app and wraps it in a livereload server. If the config
    calls for a package build, this funciton will also create and activate a
    virtual environment in the build directory so that autodoc can properly
    import needed modules
    """
    working_dir = config.get('WORKING_DIR')
    target_path = config.get('TARGET')
    package = config.get('PACKAGE')
    package_docs = config.get('PACKAGE_DOCS', 'docs')

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

    @app.route('/<path:page>')
    def subpage(page):
        return flask.render_template(page)

    app.logger.debug("configuring livereload server")
    server = Server(app.wsgi_app)

    watch_target_path = target_path
    build_target_path = target_path

    if package:
        if not os.path.isdir(target_path):
            raise Exception("Package build requires target to be a directory")

        app.logger.debug("Creating virtualenv for package")
        venv_dir = os.path.join(working_dir, 'env')
        venv.create(venv_dir)  # , with_pip=True)

        app.logger.debug("Using pip to install target package to virtualenv")
        pip.main(['install', '-e', target_path])

        app.logger.debug("setting build target path to package docs")
        build_target_path = os.path.join(target_path, package_docs)

        app.logger.debug("Activating virtual environment for package")
        activate_this(venv_dir)

    app.logger.debug("performing initial build")
    build(build_target_path, working_dir)

    app.logger.debug("setting watch for target: {}".format(target_path))
    server.watch(
        watch_target_path,
        lambda: build(build_target_path, working_dir),
    )

    app.logger.debug("finished building server")
    return server


def rm(dst):
    """
    This is a convenience function that deletes a file or directory
    """
    if os.path.exists(dst):
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        else:
            os.remove(dst)


def copy(src, dst):
    """
    This is a convenience function that copies a file or directory
    """
    if os.path.isdir(src):
        shutil.copytree(src, dst)
    else:
        shutil.copy(src, dst)
