# storage-boxes

A CadQuery fork of the awesome [assortment boxes][0] (video [here][1]) by [Alexandre Chappel][2].

If you find these boxes useful, please consider supporting [Alexandre Chappel][2] by purchasing the original digital download of the box design [here][0].


[0]: https://www.alch.shop/shop/p/assortment-boxes-v2
[1]: https://youtu.be/VntGnLuwoeY
[2]: https://www.alch.shop/


# Install

```
git clone 
cd ...
conda env create -n cadquery-boxes --file environment.yml 
conda activate cadquery-boxes
```

# Usage

```
> cd src
> python -m storage_boxes.models --help
Usage: models.py [OPTIONS] OUTPUT_DIR

Arguments:
  OUTPUT_DIR  [required]

Options:
  --unit-extent FLOAT
  --height FLOAT
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.

  --help                Show this message and exit.
> # Write all box sizes and base frames from 1x1 to 4x4 to specified output directory.
> python -m storage_boxes.models <output_dir>
```

# Development

```
# See https://github.com/bernhard-42/jupyter-cadquery#installation
wget -O jupyter-cadquery-environment.yml https://raw.githubusercontent.com/bernhard-42/jupyter-cadquery/v2.0.0-beta3/environment.yml
wget https://raw.githubusercontent.com/bernhard-42/jupyter-cadquery/v2.0.0-beta3/labextensions.txt
conda env update -n cadquery-boxes --file jupyter-cadquery-environment.yml 
jupyter-labextension install --no-build $(cat labextensions.txt)
jupyter lab build --dev-build=False --minimize=False
jupyter lab
```