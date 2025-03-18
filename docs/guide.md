# Process data

Turn data from each file in a directory into an `Activity` dataclass:

```
>>> import pathlib
>>> from strava_map import graph, process_activities
>>> data_path = getfixture("test_data")
>>> activities = process_activities.parse_all_files_in_dir(data_path)

```

`Activity` dataclasses have a variety of data, most importantly the name of an activity, GPS coordinates that were recorded during the activity, and the type of activity if known. 

```python
>>> for activity in activities:
...     print(activity.name, ", ", activity.type.value)
test data ,  cycling
some test data ,  running
test_fit_file ,  unknown
more test data ,  running

```

# Plot data

You can make a plotly figure to plot gps coordinates of given activities. Optionally, a dictionary can beprovided with figure styling details, in accordance with plotly's figure styling options. See [plotly docs](https://plotly.com/python/styling-plotly-express/) for more help.

```python
>>> style = {"title": "my activities"}
>>> fig = process_activities.plot_activities(activities, fig_style=style)

```

# Generate Routes

You can find the best path between two points by putting all your activities into a graph data structure:

```
>>> g = graph.make_graph(activities, max_edge_length=10)
>>> print(g)
DiGraph with 1727 nodes and 2838 edges

```

And then calling the `find_route` function:

```
>>> cost, route = graph.find_route(g, start=(1.5, 2.5), goal=(1, 2))
>>> route
[(1.5, 2.5), (3.5, 4.5), (1, 2)]

```

This best path is determined by finding the shortest path between the two points, with node weight determined by reciprocol scaling for the number of times an activity has recorded at each coordinate. This should result in routes generated that use prefered roads, as indicated by previous behavior.

# Plot Route

You can add the route to your figure to visuaalize in red, overlaid the other gps coordinates:

```python
>>> process_activities.plot_path(fig, route)
Figure({
    ...
})

```