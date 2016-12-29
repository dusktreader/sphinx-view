import logging
import os
import pip
import setuptools
import shutil
import sphinx.apidoc
import sphinx.application
import sys
import textwrap
import types
import venv

from sview.exceptions import SviewError


class Builder:

    def __init__(self, logger=None, **config):
        self.working_dir = config.get('WORKING_DIR')
        self.target = config.get('TARGET')
        self.package = config.get('PACKAGE')
        self.package_docs = config.get('PACKAGE_DOCS', 'docs')
        self.build_dir = os.path.join(self.working_dir, 'build')

        if logger is None:
            self.logger = logging.getLogger(__name__)
        else:
            self.logger = logger

        if self.package:
            self.setup_venv()

    def setup_venv(self):
        SviewError.require_condition(
            os.path.isdir(self.target),
            "Package build requires target to be a directory",
        )

        self.logger.debug("Creating virtualenv for package")
        venv_dir = os.path.join(self.working_dir, 'env')
        venv.create(venv_dir)  # , with_pip=True)

        self.logger.debug("Using pip to install target package to virtualenv")
        pip.main(['install', self.target])

        self.logger.debug("setting build target path to package docs")
        self.root_dir = self.target
        self.target = os.path.join(self.target, self.package_docs)

        self.logger.debug("Activating virtual environment for package")
        activate_this(venv_dir)

    def copy_dir(self):
        for element in os.listdir(self.target):
            element_path = os.path.join(self.target, element)
            final_path = os.path.join(self.build_dir, element)
            print("copying ", element_path, " to ", final_path)
            copy(element_path, final_path)

    def copy_file(self):
        ext = os.path.splitext(self.target)[1]
        final_path = os.path.join(self.build_dir, 'index' + ext)
        copy(self.target, final_path)

    def fetch_ext_from_index(self, include_dot=True):
        self.logger.debug("getting extension from index doc")
        possible_exts = []
        for file in os.listdir(self.build_dir):
            file_path = os.path.join(self.build_dir, file)
            (file_name, file_ext) = os.path.splitext(file)
            if file_name == 'index' and not os.path.isdir(file_path):
                possible_exts.append(file_ext)
        SviewError.require_condition(
            len(possible_exts) == 1,
            "Couldn't find one index file the build directory",
        )
        ext = possible_exts.pop()
        if not include_dot:
            ext = ext.lstrip('.')
        self.logger.debug("found index extension was '{}'".format(ext))
        return ext

    def remake_build_dir(self):
        rm(self.build_dir)
        os.makedirs(self.build_dir)

    def build_conf_file(self):
        final_conf_path = os.path.join(self.build_dir, 'conf.py')
        conf_content = textwrap.dedent("""
            source_suffix = '{ext}'
            master_doc = 'index'
            html_theme = 'alabaster'
            html_static_path = ['_static']
            extensions = ['sphinx.ext.autodoc']
        """).format(
            ext=self.fetch_ext_from_index(),
        )

        with open(final_conf_path, 'w') as conf_file:
            conf_file.write(conf_content)

    def build_api_doc(self):
        self.logger.debug("Generating documentation for package api")
        opts = types.SimpleNamespace(
            destdir=self.build_dir,
            maxdepth=2,
            force=True,
            no_toc=True,
            modulefirst=True,
            suffix=self.fetch_ext_from_index(include_dot=False),
            implicit_namespaces=False,
            noheadings=False,
            dryrun=False,
            separatemodules=False,
            header=os.path.basename(self.root_dir),
        )
        self.logger.debug("Finding packages starting at " + self.root_dir)
        packages = setuptools.find_packages(
            where=self.root_dir, exclude=('test*', ),
        )
        if len(packages) == 0:
            self.logger.debug("Couldn't find any packages")
            return
        else:
            self.logger.debug("Found packages: {}".format(packages))

        self.logger.debug("Finding unique root packages")
        unique_roots = set([p.split('.')[0] for p in packages])
        self.logger.debug("Found unique roots: {}".format(unique_roots))

        modules = []
        self.logger.debug("Searching for modules in packages")
        for package in unique_roots:
            package_dir = os.path.join(self.root_dir, package)
            modules.extend(sphinx.apidoc.recurse_tree(package_dir, [], opts))
        self.logger.debug("Found the following modules: {}".format(modules))
        sphinx.apidoc.create_modules_toc_file(modules, opts)

    def build(self):
        """
        Rebuilds a target in a specified working directory. If the target is a
        directory, then all contents of the directory will be copied into the
        working directory prior to building. This function also builds a
        simplistic conf.py for sphinx-build
        """
        self.remake_build_dir()

        if os.path.isdir(self.target):
            self.copy_dir()
        else:
            self.copy_file()
        self.build_conf_file()

        if self.package:
            self.build_api_doc()

        sphinx.application.Sphinx(
            self.build_dir,
            self.build_dir,
            self.build_dir,
            self.build_dir,
            'html',
        ).build()


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
