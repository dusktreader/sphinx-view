import os
import tempfile
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser

from sview.server import create_server


def expand_path(path):
    return os.path.abspath(os.path.expanduser(path))


def main():
    parser = ArgumentParser(
        formatter_class=ArgumentDefaultsHelpFormatter,
        description="Provides a live view of sphinx or restructuredtext docs",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=5656,
        help="Set the flask webserver port",
    )
    parser.add_argument(
        "-P",
        "--package",
        action="store_true",
        help="Generate documentation for a python package (include apidocs)",
    )
    parser.add_argument(
        "-d",
        "--package-docs",
        default="docs",
        help="Set the subfolder of package where the docs to build are found",
    )
    parser.add_argument(
        "-b",
        "--build-dir",
        help="""
            Set the directory where the documentation will be built.
            Defaults to a temp directory that is cleaned up on completion
        """,
    )
    parser.add_argument(
        "-c",
        "--config",
        help="""
            Set the config file to use when building docs.
            Defaults to an internal hard-coded basic sphinx config.
        """,
        default=None,
    )
    parser.add_argument(
        "target",
        help="The target to view",
    )
    args = parser.parse_args()
    print(args.target)

    config = dict(
        TARGET=expand_path(args.target),
        SERVER_PORT=args.port,
        PACKAGE=args.package,
        PACKAGE_DOCS=args.package_docs,
        CONFIG=args.config,
    )

    if args.build_dir is not None:
        config["WORKING_DIR"] = expand_path(args.build_dir)
        (server, builder) = create_server(**config)
        server.serve(port=args.port, host="localhost", open_url_delay=0.5)
    else:
        with tempfile.TemporaryDirectory() as working_dir:
            config["WORKING_DIR"] = working_dir
            (server, builder) = create_server(**config)
            server.serve(port=args.port, host="localhost", open_url_delay=0.5)


if __name__ == "__main__":
    main()
