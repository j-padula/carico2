"""
3-D truck loading visualisation using Plotly.
Accepts a translator function `t` for multilingual axis/title labels.
"""

import plotly.graph_objects as go
import numpy as np
from typing import List, Dict, Callable


def _noop(key, **kw):
    return key


def _box_mesh(x, y, z, l, w, h, color, name, opacity=0.85):
    vx = [x,   x+l, x+l, x,   x,   x+l, x+l, x  ]
    vy = [y,   y,   y+w, y+w, y,   y,   y+w, y+w]
    vz = [z,   z,   z,   z,   z+h, z+h, z+h, z+h]
    i  = [0,0, 1,1, 2,2, 3,3, 4,4, 5,5]
    j  = [1,3, 2,5, 3,6, 0,7, 5,7, 6,4]
    k  = [2,2, 5,6, 6,7, 7,4, 6,0, 7,1]
    return go.Mesh3d(
        x=vx, y=vy, z=vz,
        i=i, j=j, k=k,
        color=color, opacity=opacity,
        name=name, showlegend=True, legendgroup=name,
        hovertemplate=(
            f"<b>{name}</b><br>"
            f"Pos: ({x:.2f}, {y:.2f}, {z:.2f})<br>"
            f"Dims: {l:.2f}×{w:.2f}×{h:.2f}<br>"
            "<extra></extra>"
        ),
    )


def _truck_wireframe(truck_l, truck_w, truck_h, label="Truck"):
    corners = np.array([
        [0,       0,       0      ],
        [truck_l, 0,       0      ],
        [truck_l, truck_w, 0      ],
        [0,       truck_w, 0      ],
        [0,       0,       truck_h],
        [truck_l, 0,       truck_h],
        [truck_l, truck_w, truck_h],
        [0,       truck_w, truck_h],
    ])
    edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]
    xs, ys, zs = [], [], []
    for a, b in edges:
        xs += [corners[a,0], corners[b,0], None]
        ys += [corners[a,1], corners[b,1], None]
        zs += [corners[a,2], corners[b,2], None]
    return go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode="lines",
        line=dict(color="#1a1a2e", width=4),
        name=label, showlegend=False, hoverinfo="skip",
    )


def build_figure(
    truck_l: float, truck_w: float, truck_h: float,
    packed_boxes: List[Dict], unpacked_boxes: List[Dict],
    efficiency: float,
    t: Callable = _noop,
) -> go.Figure:

    fig = go.Figure()
    fig.add_trace(_truck_wireframe(truck_l, truck_w, truck_h, label=t("plot_truck")))

    seen = set()
    for b in packed_boxes:
        name = b["name"]
        mesh = _box_mesh(
            b["x"], b["y"], b["z"],
            b["placed_l"], b["placed_w"], b["placed_h"],
            b["color"], name,
        )
        mesh.showlegend = name not in seen
        seen.add(name)
        fig.add_trace(mesh)

    max_dim = max(truck_l, truck_w, truck_h)

    eff_txt   = t("plot_eff_label")
    load_txt  = t("plot_loaded_label")
    unload_txt= t("plot_unloaded_label")

    title_str = (
        f"<b>{t('plot_title')}</b>  |  "
        f"{eff_txt}<b>{efficiency:.1f}%</b>  |  "
        f"{load_txt}<b>{len(packed_boxes)}</b>"
        + (f"  |  {unload_txt}<b>{len(unpacked_boxes)}</b>" if unpacked_boxes else "")
    )

    fig.update_layout(
        scene=dict(
            xaxis=dict(title=t("plot_x"), range=[0, truck_l], showgrid=True, gridcolor="#e0e0e0"),
            yaxis=dict(title=t("plot_y"), range=[0, truck_w], showgrid=True, gridcolor="#e0e0e0"),
            zaxis=dict(title=t("plot_z"), range=[0, truck_h], showgrid=True, gridcolor="#e0e0e0"),
            aspectmode="manual",
            aspectratio=dict(x=truck_l/max_dim, y=truck_w/max_dim, z=truck_h/max_dim),
            camera=dict(eye=dict(x=1.6, y=-1.6, z=1.2)),
            bgcolor="#f8f9fa",
        ),
        title=dict(text=title_str, font=dict(size=16)),
        legend=dict(
            title=t("plot_legend"),
            bgcolor="rgba(255,255,255,0.9)", bordercolor="#ccc", borderwidth=1,
        ),
        margin=dict(l=0, r=0, t=50, b=0),
        height=600,
    )
    return fig


def build_2d_layers(
    truck_l: float, truck_w: float, truck_h: float,
    packed_boxes: List[Dict],
    t: Callable = _noop,
) -> go.Figure:

    layers = sorted({round(b["z"], 3) for b in packed_boxes})
    if not layers:
        return go.Figure()

    fig = go.Figure()

    for i, layer_z in enumerate(layers):
        visible     = (i == 0)
        layer_boxes = [b for b in packed_boxes if abs(b["z"] - layer_z) < 1e-3]

        fig.add_shape(
            type="rect", x0=0, y0=0, x1=truck_l, y1=truck_w,
            line=dict(color="#1a1a2e", width=3),
            fillcolor="rgba(240,240,255,0.3)",
            visible=visible,
        )
        for b in layer_boxes:
            fig.add_shape(
                type="rect",
                x0=b["x"], y0=b["y"],
                x1=b["x"]+b["placed_l"], y1=b["y"]+b["placed_w"],
                fillcolor=b["color"], line=dict(color="white", width=1.5),
                opacity=0.8, visible=visible,
            )
            cx = b["x"] + b["placed_l"] / 2
            cy = b["y"] + b["placed_w"] / 2
            fig.add_annotation(
                x=cx, y=cy, text=b["name"][:10],
                showarrow=False, font=dict(size=9, color="white"),
                visible=visible,
            )

    fig.update_layout(
        title=t("plot_2d_title"),
        xaxis=dict(title=t("plot_x"), range=[0, truck_l * 1.02]),
        yaxis=dict(title=t("plot_y"), range=[0, truck_w * 1.02], scaleanchor="x"),
        height=420,
        plot_bgcolor="#f8f9fa",
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig
