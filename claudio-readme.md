# napari-utrack-loader

This a Napari plugin image sequences as well as detections and tracks produced by the u-track software into napari. 

Here are the main Features
-  visualization of trajectories and detection  along with raw data. 
-  Double-clicking on a trajectory creates a plot of its intensity on all the currently opened channel. 

## Installation

This code in this repositories requires the installation of several libraries (a.k.a. dependencies). Here are the installation on how to install it on Windows, Mac OS or Linux. 

### Installing the present git repository on your machine

*If you do not have git installed on your machine*. Install git using this basic tutorial: https://github.com/git-guides/install-git . Then open the git command prompt (or any command prompt), execute the following command in a software of your choice: 

``` shell
git clone git@github.com:bioimage-mining-group/napari-utrack-loader.git
```

### Creating a Conda environment

*If you do not have conda installed already*. You can use the simple instructions at the link below to install **miniconda**, a version of conda that comes with the basic tools you need. 

https://docs.anaconda.com/miniconda/miniconda-install/

To create and activate an environment dedicated for your software, open your command line prompt (using the instruction at the link above to find what is your prompt, that depends on your operating system). Then type

```
conda create -n napari-u-track-loader-v1 python=3.9
conda activate napari-u-track-loader-v1
``` 

Then install napari and the software with its other dependencies: 

```
conda install -c conda-forge napari pyqt
pip install -e . 
``` 

Note: we do not use 'pip install' for napari due to some problem in mac os. 

**What is conda environment?**

Python is a very popular language. As such, many code libaries have been developped by the community and almost all pieces of code relies on those libraries that must be installed beforehand on your machine (for example, in this plugin, we use napari for image display and matplotlib for plotting graphs). One of the challenge brought by this diversity is in making sure the code is using the libraries it was developped with. To solve this issue, conda is tool that enable the creation of "environnent" where we can specify the exact versions of the libraries that must be installed. That way a conda user can be working on different software using different library versions. There is several alternative to conda for the same task, such as Poetry or Rye. 

### Installing the code and dependency

## Usage

Activate the environment in your command prompt. 

```
conda activate napari-u-track-loader-v1
``` 

Launch napari: 
```
napari 
``` 

Follow this video for a tutorial: 
https://resana.numerique.gouv.fr/public/information/consulterAccessUrl?cle_url=1717858798VD4BYVVZBDhdMFcxVjhQcAc5CDUAIQNqUDsFOFQ1DTcCNlNuVTACZQQ1AjZQYg==


The data used for the demo is at 
https://resana.numerique.gouv.fr/public/information/consulterAccessUrl?cle_url=1501984592CGIAYAMPAT0Ga1I0AW8DI1xiCzYAIQZvAGsHOgRlXWdXYlVlAWYBYlNlU2ZSZg==


## Updating the code 

To update the code through git, just go in the repository folder and download the latest version with git pull. No additional changes are needed. 

```
git pull
``` 

## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [MIT] license,
"napari-utrack-loader" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed description.

[napari]: https://github.com/napari/napari
[Cookiecutter]: https://github.com/audreyr/cookiecutter
[@napari]: https://github.com/napari
[MIT]: http://opensource.org/licenses/MIT
[BSD-3]: http://opensource.org/licenses/BSD-3-Clause
[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt
[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt
[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0
[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt
[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[file an issue]: https://github.com/jules-vanaret/napari-utrack-loader/issues

[napari]: https://github.com/napari/napari
[tox]: https://tox.readthedocs.io/en/latest/
[pip]: https://pypi.org/project/pip/
[PyPI]: https://pypi.org/
