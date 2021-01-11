from typing import Optional
from pathlib import Path

import cadquery as cq
import typer

from .types import Dimensions, BoxParameters


def floor_tile(dims: Dimensions, workplane: cq.Workplane):
    return (
        workplane.box(dims.width, dims.length, dims.height + 0.001)
        .edges("<Z")
        .chamfer(dims.height)
    )


def add_label_tab(params: BoxParameters, storage_box: cq.Workplane) -> cq.Workplane:
    tab_dims = Dimensions(width=20, length=7.5, height=11)

    label_workplane = (
        storage_box.faces("<X[2]").edges(">Z").translate((0.5 * tab_dims.length, 0, 0))
    )

    label_insert = (
        label_workplane.box(
            tab_dims.length - 0.5 * params.wall_thickness,
            tab_dims.width - params.wall_thickness,
            params.line_width,
            combine=False,
            centered=(False, True, True),
        )
        .translate((-0.5 * tab_dims.length, 0, -0.5 * params.line_width))
        .edges("|Z and >X")
        .fillet(params.default_fillet - (0.5 * params.wall_thickness))
    )

    result_w_label_box = (
        label_workplane.translate((0, 0, -0.5 * tab_dims.height))
        .box(tab_dims.length, tab_dims.width, tab_dims.height)
        .faces(">Z[-2]")
        .edges(">X")
        .chamfer(tab_dims.length - 1e-4)
        .faces("<X[-3]")
        .edges("|Z")
        .fillet(params.default_fillet)
    ).cut(label_insert)

    return result_w_label_box


def make_storage_box(
    params: BoxParameters, workplane: cq.Workplane, label: bool = True
) -> cq.Workplane:
    floor_tile_dims = Dimensions(
        width=params.unit_extent,
        length=params.unit_extent,
        height=params.base_height,
    )

    floor_tile_ = floor_tile(floor_tile_dims, workplane).translate(
        (
            (0.5 - 0.5 * params.columns) * params.unit_extent,
            (0.5 - 0.5 * params.rows) * params.unit_extent,
            -params.base_height,
        )
    )

    result = floor_tile_

    for x in range(params.columns):
        for y in range(params.rows):
            if x == 0 and y == 0:
                continue
            translation = (x * params.unit_extent, y * params.unit_extent)
            result = result.union(floor_tile_.translate(translation))

    result = (
        result.faces(">Z")
        .box(
            params.columns * params.unit_extent,
            params.rows * params.unit_extent,
            params.height - params.base_height,
            centered=(True, True, False),
        )
        .edges("|Z and (>X or >Y or <X or <Y)")
        .fillet(2)
        .faces(">Z")
        .shell(-params.wall_thickness)
    )
    if not label:
        return result
    else:
        return add_label_tab(params, result)


def make_storage_tray(
    params: BoxParameters, workplane: cq.Workplane, chamfer_bottom: bool = True
):
    dims = Dimensions(
        width=params.unit_extent,
        length=params.unit_extent,
        height=params.base_height,
    )

    floor_tile_ = (
        workplane.box(
            dims.width, dims.length, dims.height + 0.5 * params.wall_thickness
        )
        .edges("<Z")
        .chamfer(dims.height)
    )

    if chamfer_bottom:
        tray = floor_tile_.faces(">Z or <Z").shell(-params.wall_thickness)
    else:
        tray = workplane.box(dims.width, dims.length, dims.height).cut(floor_tile_)
    result = tray

    for x in range(params.columns):
        for y in range(params.rows):
            if x == 0 and y == 0:
                continue
            translation = (x * dims.width, y * dims.length)
            result = result.union(tray.translate(translation))

    return result.translate(
        (
            (0.5 - 0.5 * params.columns) * params.unit_extent,
            (0.5 - 0.5 * params.rows) * params.unit_extent,
            0.5 * params.base_height,
        )
    )


def main(
    output_dir: Path,
    unit_extent: Optional[float] = None,
    height: Optional[float] = None,
):
    base_parameters = {
        # k: v
        # for k, v in [("unit_extent", unit_extent), ("height", height)]
        # if v is not None
    }
    storage_boxes = {}
    for rows in range(1, 5):
        for columns in range(1, 5):
            if columns < rows:
                continue
            box_parameters = BoxParameters(
                columns=columns,
                rows=rows,
            )
            storage_boxes[(rows, columns)] = make_storage_box(
                box_parameters,
                cq.Workplane("XY"),
            )

    for (rows, columns), storage_box in storage_boxes.items():
        namebase = f"storage_box-{rows}x{columns}"
        print(namebase)
        storage_box.val().exportStl(str(output_dir.joinpath(f"{namebase}.stl")))
        storage_box.val().exportStep(str(output_dir.joinpath(f"{namebase}.step")))

    trays = {}
    for chamfered in (True, False):
        for rows in range(1, 5):
            for columns in range(1, 5):
                if columns < rows:
                    continue
                trays[(chamfered, rows, columns)] = make_storage_tray(
                    BoxParameters(
                        columns=columns,
                        rows=rows,
                    ),
                    cq.Workplane("XY"),
                    chamfer_bottom=chamfered,
                )

    for (chamfered, rows, columns), tray in trays.items():
        chamfer_prefix = "no_" if not chamfered else ""
        namebase = f"storage_tray-{chamfer_prefix}chamfer-{rows}x{columns}"
        print(namebase)
        tray.val().exportStl(str(output_dir.joinpath(f"{namebase}.stl")))
        tray.val().exportStep(str(output_dir.joinpath(f"{namebase}.step")))


if __name__ == "__main__":
    typer.run(main)