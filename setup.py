import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="Kafthon",
    version="0.0.1",
    author="B. Versteeg",
    author_email="a.b.versteeg@gmail.com",
    description="High level Python wrapper for Kafka",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aabversteeg/kafthon",
    packages=[
        'kafthon.' + module_name
        for module_name in setuptools.find_packages('kafthon')
    ] + ['kafthon'],
    include_package_data=True,
    install_requires=['docker', 'kafka-python', 'msgpack', 'typeguard', 'temporenc'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
