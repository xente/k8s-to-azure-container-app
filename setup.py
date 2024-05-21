from setuptools import find_packages, setup


# Read the contents of your README file
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='k8s-to-azure-container-app',
    version='0.1',
    description=' Migrate Kubernetes deployments into Azure Container Apps',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/xente/K8sToAzureContainerApp',
    packages=find_packages(),
    install_requires=[
       'pyyaml>=6.0.1',
       'kubernetes>=29.0.0',
    ],
    entry_points={
        'console_scripts': [
            'K8sToAca=src.main:main',  # Create a command-line script
        ],
    },
    python_requires='>=3.6'
)