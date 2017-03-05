import flask
import os
import mimetypes

from livereload import Server
from sview.builder import Builder


def create_server(**config):
    """
    Creates a new flask app and wraps it in a livereload server. If the config
    calls for a package build, this funciton will also create and activate a
    virtual environment in the build directory so that autodoc can properly
    import needed modules
    """
    working_dir = config['WORKING_DIR']
    target_path = config['TARGET']

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

    def process_page(page_path):
        # Don't allow Jinja templating to interfere with rendering the page
        with open(os.path.join(template_folder, page_path), 'rb') as page_file:
            page_content = page_file.read()

        response = flask.make_response(page_content)
        _, page_extension = os.path.splitext(page_path)
        response.mimetype = mimetypes.types_map[page_extension]
        return response

    @app.route('/')
    def index():
        return process_page('index.html')

    @app.route('/<path:page>')
    def subpage(page):
        return process_page(page)

    app.logger.debug("configuring livereload server")
    server = Server(app.wsgi_app)

    app.logger.debug("Setting up the builder")
    builder = Builder(logger=app.logger, **config)

    app.logger.debug("performing initial build")
    builder.build()

    app.logger.debug("setting watch for target: {}".format(target_path))
    server.watch(target_path, builder.build)

    app.logger.debug("finished creating server")
    return (server, builder)
