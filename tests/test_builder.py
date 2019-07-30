import os
import sys

from sview.builder import Builder


class TestBuilder:

    def test_init_for_single(self, tmpdir, find_data_file):
        config = {
            'WORKING_DIR': str(tmpdir),
            'TARGET': find_data_file('single.rst'),
        }
        builder = Builder(**config)
        assert builder is not None
        assert builder.working_dir == str(tmpdir)
        assert builder.target == find_data_file('single.rst')
        assert builder.build_dir == os.path.join(str(tmpdir), 'build')

    def test_init_for_dir(self, tmpdir, find_data_file):
        config = {
            'WORKING_DIR': str(tmpdir),
            'TARGET': find_data_file('directory'),
        }
        builder = Builder(**config)
        assert builder is not None
        assert builder.working_dir == str(tmpdir)
        assert builder.target == find_data_file('directory')
        assert builder.build_dir == os.path.join(str(tmpdir), 'build')

    def test_init_for_package(self, tmpdir, find_data_file):
        target = find_data_file('package')
        config = {
            'WORKING_DIR': str(tmpdir),
            'TARGET': target,
            'PACKAGE': True,
            'PACKAGE_DOCS': 'docs',
        }
        builder = Builder(**config)
        assert builder is not None
        assert builder.working_dir == str(tmpdir)
        assert builder.target == os.path.join(target, 'docs')
        assert builder.build_dir == os.path.join(str(tmpdir), 'build')
        assert os.path.exists(os.path.join(str(tmpdir), 'env'))
        assert sys.prefix == os.path.join(str(tmpdir), 'env')

    def test_copy_dir(self, tmpdir, find_data_file):
        target = find_data_file('package')
        config = {
            'WORKING_DIR': str(tmpdir),
            'TARGET': target,
            'PACKAGE': True,
            'PACKAGE_DOCS': 'docs',
        }
        builder = Builder(**config)
        builder.remake_dirs()
        builder.copy_dir()
        assert os.path.exists(os.path.join(str(tmpdir), 'build', 'index.rst'))

    def test_copy_file(self, tmpdir, find_data_file):
        target = find_data_file('single.rst')
        config = {
            'WORKING_DIR': str(tmpdir),
            'TARGET': target,
        }
        builder = Builder(**config)
        builder.remake_dirs()
        builder.copy_file()
        final_path = os.path.join(str(tmpdir), 'build', 'index.rst')
        assert os.path.exists(final_path)

        with open(target) as original_file:
            with open(final_path) as final_file:
                assert original_file.read() == final_file.read()

    def test_copy_literal_includes(self, tmpdir, find_data_file):
        target = find_data_file('package')
        config = {
            'WORKING_DIR': str(tmpdir),
            'TARGET': target,
            'PACKAGE': True,
            'PACKAGE_DOCS': 'docs',
        }
        builder = Builder(**config)
        builder.remake_dirs()
        builder.copy_dir()
        builder.copy_literal_includes()
        assert os.path.exists(os.path.join(str(tmpdir), 'build', 'dummy.py'))
        final_path = os.path.join(str(tmpdir), 'build', 'index.rst')
        with open(final_path) as final_file:
            assert '.. literalinclude:: dummy.py' in final_file.read()

    def test_fetch_ext_from_index(self, tmpdir, find_data_file):
        target = find_data_file('single.rst')
        config = {
            'WORKING_DIR': str(tmpdir),
            'TARGET': target,
        }
        builder = Builder(**config)
        builder.remake_dirs()
        builder.copy_file()
        assert builder.fetch_ext_from_index() == '.rst'

        target = find_data_file('single.md')
        config = {
            'WORKING_DIR': str(tmpdir),
            'TARGET': target,
        }
        builder = Builder(**config)
        builder.remake_dirs()
        builder.copy_file()
        assert builder.fetch_ext_from_index() == '.md'

    def test_build_conf_file(self, tmpdir, find_data_file):
        target = find_data_file('single.rst')
        config = {
            'WORKING_DIR': str(tmpdir),
            'TARGET': target,
        }
        builder = Builder(**config)
        builder.remake_dirs()
        builder.copy_file()
        builder.build_conf_file()

        final_path = os.path.join(str(tmpdir), 'build', 'conf.py')
        with open(final_path) as final_file:
            assert "source_suffix = '.rst'" in final_file.read()

    def test_build_single(self, tmpdir, find_data_file):
        target = find_data_file('single.rst')
        config = {
            'WORKING_DIR': str(tmpdir),
            'TARGET': target,
        }
        builder = Builder(**config)
        builder.build()

        final_path = os.path.join(str(tmpdir), 'build', 'index.html')
        assert os.path.exists(final_path)

    def test_build_directory(self, tmpdir, find_data_file):
        config = {
            'WORKING_DIR': str(tmpdir),
            'TARGET': find_data_file('directory'),
        }
        builder = Builder(**config)
        builder.build()

        final_path = os.path.join(str(tmpdir), 'build', 'index.html')
        assert os.path.exists(final_path)

    def test_build_package(self, tmpdir, find_data_file):
        target = find_data_file('package')
        config = {
            'WORKING_DIR': str(tmpdir),
            'TARGET': target,
            'PACKAGE': True,
            'PACKAGE_DOCS': 'docs',
        }
        builder = Builder(**config)
        builder.build()

        build_dir = os.path.join(str(tmpdir), 'build')
        assert os.path.exists(os.path.join(build_dir, 'index.html'))
        assert os.path.exists(os.path.join(build_dir, 'modules.html'))
        assert os.path.exists(os.path.join(build_dir, 'svdummy.html'))
