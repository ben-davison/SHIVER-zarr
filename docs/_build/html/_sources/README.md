# SHIVER docs

This directory contains the files necessary for Jupyter Book to construct the Read the Docs website (https://shiver-zarr.readthedocs.io/).

Unless you want to edit the website, you shouldn't need to modify anything in this directory. To edit the website structure or markdown files, please refer to the [Jupyter Book documentation](https://jupyterbook.org/)

Website updates will be automatically ingested by Read the Docs and updated on https://shiver-zarr.readthedocs.io/en/latest/ site every time you push to the main branch. At every version update, the 'latest' site will be saved as the 'stable' version.

## Buildng the Docs locally
If you wish to ensure the website compiles correctly before uploading to Read the Docs, you can build it locally.

First, ensure you have activated the project's Conda environment (which contains `jupyter-book` and all the dependencies required to execute the example notebooks):

```bash
conda activate shiver_env
```

Then, navigate to this directory (or the root directory containing your _toc.yml) and build the website:

```bash
jupyter-book build .
```

The compiled website will then be available to view by opening `_build/html/index.html` in your web browser.

If it's struggling to compile, or if you have renamed/deleted chapters and the navigation looks broken, clearing the cached build files often fixes things:

```bash
jupyter-book clean .
```

## Deploying
When you are happy with how the local build looks, simply push your changes to GitHub (ensuring you include `git add .` if you have created new files).

> _Note: There will always be some minor quirks between the local Jupyter Book compilation and the live Read the Docs version. It is highly recommended to check any new or edited pages on the 'latest' version of the live website before a new tool version is released and a 'stable' version of the docs is locked in_

