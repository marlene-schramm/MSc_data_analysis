''' This script contains functions for plotting observational data'''
import numpy as np
import plotly.graph_objects as go

### Surface animation function for 2D fields

def surface_animation(ds, var, model_run, time_dim, x_dim, y_dim, colorscale):
    ''' Create an animated surface plot for a given variable showing its time evolution.'''
    # Extract coordinate arrays
    x_coords = ds[x_dim].values
    y_coords = ds[y_dim].values

    # Determine global min/max
    var_min = float(ds[var].min())
    var_max = float(ds[var].max())

    frames = []
    time_values = ds[time_dim].values
    num_frames = len(time_values)

    for i in range(num_frames):
        # plot label for each time step (currently simple integer)
        time_label = str(i + 1)

        # Select Data slice for current timestep
        frame_data_slice = ds[var].isel({time_dim: i})
        
        z_data = frame_data_slice.values
        
        trace = go.Contour(
            z=z_data,
            x=x_coords,
            y=y_coords,
            colorscale=colorscale,
            showscale=True,
            colorbar=dict(title=var, thickness=20),
            zmin=var_min,
            zmax=var_max,
            contours=dict(showlines=False, coloring='fill'),
            line=dict(width=0),
            hovertemplate=(
                f"Time: {time_label}<br>" +  # Removed .2f since it's a string now
                "X: %{x:.2f}<br>" +
                "Y: %{y:.2f}<br>" +
                f"{var}: %{{z:.2f}}<extra></extra>"
            )
        )
        
        frames.append(
            go.Frame(
                data=[trace],
                name=str(i)
            )
        )

    fig = go.Figure(data=frames[0].data, frames=frames)

    fig.update_layout(
        title="Model Run " + model_run + "<br>Time Evolution of " + var,
        xaxis_title="XC",
        yaxis_title="YC",
        width=1500,
        height=1200,
        margin=dict(l=50, r=50, t=60, b=80),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            buttons=[
                dict(label="▶ Play", method="animate", args=[None, {"frame": {"duration": 500, "redraw": True}, "mode": "immediate"}]),
                dict(label="⏸ Pause", method="animate", args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}])
            ]
        )],
        sliders=[dict(
            steps=[
                dict(
                    method="animate",
                    args=[[str(i)], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}}],
                    # label in unit day
                    label=str(int(i+1))
                )
                for i in range(num_frames)
            ],
            currentvalue={"visible": False},
            pad={"t": 50},
            len=0.9,
            x=0.1,
            y=0
        )]  
    )

    # fig.show(renderer="plotly_mimetype")
    return fig
