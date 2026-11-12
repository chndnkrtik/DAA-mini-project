# RouteWise - Smart Travel Route Optimizer

## Requirements
- Python 3.10 or newer
- pip

## Setup (Windows)
Open Command Prompt or the VS Code terminal in this folder:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Open the address printed in the terminal (normally http://127.0.0.1:5000).

## Run tests
```bash
pytest
```

## Files
- `main.py`: Flask application and request handling.
- `travel_optimizer/models.py`: Edge, RouteLeg and RouteResult data classes.
- `travel_optimizer/data.py`: sample city-route data.
- `travel_optimizer/algorithms.py`: Dijkstra, Kruskal, route enumeration, budget filtering, merge sort and quick sort.
- `templates/index.html`: web interface.
- `static/style.css`: page styling.
- `tests/test_travel_optimizer.py`: basic tests.

## Note about the report
The supplied PDF shows only partial source code and does not include complete implementations for all imported modules or the HTML/CSS template. Those missing parts have been completed here so the project can run as a standalone example. The route data is illustrative/simulated, not live traffic or fare data.
