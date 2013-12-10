import os


def fullsplit(path, result=None):
    '''Split a pathname into components (the opposite of os.path.join)
    in a platform-neutral way.
    '''
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, package_data = [], {}

root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)


for dirpath, dirnames, filenames in os.walk('marathoner'):
    # Ignore PEP 3147 cache dirs and those whose names start with '.'
    dirnames[:] = [d for d in dirnames if not d.startswith('.') and d != '__pycache__']
    parts = fullsplit(dirpath)
    package_name = '.'.join(parts)
    if '__init__.py' in filenames:
        packages.append(package_name)
    elif filenames:
        relative_path = []
        while '.'.join(parts) not in packages:
            relative_path.append(parts.pop())
        relative_path.reverse()
        path = os.path.join(*relative_path)
        package_files = package_data.setdefault('.'.join(parts), [])
        package_files.extend([os.path.join(path, f) for f in filenames])


scripts = ['bin/marathoner']
if os.name == 'nt':
    scripts.append('bin/marathoner.bat')

version = __import__('marathoner').__version__


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.md') as f:
    readme = f.read()
with open('LICENSE') as f:
    license = f.read()


setup(
    name='marathoner',
    version=version,
    description='Testing tool for TopCoder marathon matches.',
    long_description=readme,
    author='Michal Mimino Danilak',
    author_email='michal.danilak@gmail.com',
    url='https://github.com/Mimino666/tc-marathoner',
    packages=packages,
    package_data=package_data,
    scripts=scripts,
    install_requires=[
        'six',
    ],
    license=license,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Environment :: Console',
        'Topic :: Scientific/Engineering',
    ],
)
