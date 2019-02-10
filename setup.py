from setuptools import find_packages, setup

# Full details here:
#   https://packaging.python.org/tutorials/distributing-packages/
# Install in venv in editable mode with:
#   pip install -e .


setup(
    name='flaskr',
    version='1.0.0',
    packages=find_packages(),
    # What modules/directories needed? find_packages identifies automatically
    include_package_data=True,
    # This pulls in the additional non-code paths (e.g. templates directory)
    # This requires a MANIFEST.in file. Also tells to exclude bytecode
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)
