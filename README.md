# Trace Generator

A Python library for generating realistic distributed trace data for testing, visualization, and analysis of microservice architectures.

## Features

- Generate synthetic distributed trace data with realistic properties
- Configure service topologies with different service types (proxy, web, database)
- **Create random service topologies** with configurable depth, width, and complexity
- Visualize trace topologies in the console with color-coded statuses
- Control randomization and performance characteristics of generated traces
- Export trace data to JSON and CSV formats for further analysis
- **Organize traces hierarchically** for better analysis and visualization
- Command-line interface for bulk trace generation and analysis

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/trace_generator.git
cd trace_generator

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```python
from trace_generator import ServiceConfig, TraceGenerator

# Define your service topology
services = [
    ServiceConfig(name="gateway", service_type="proxy", connections=["backend"]),
    ServiceConfig(name="backend", service_type="web", connections=["database"]),
    ServiceConfig(name="database", service_type="database")
]

# Create a trace generator
generator = TraceGenerator(services, randomization_level=0.3)

# Generate traces
traces = generator.generate_traces(num_traces=5)

# Pretty print the generated traces
generator.pretty_print_traces(traces)
```

## Visualizing Traces

The `pretty_print_traces` method provides a nice console visualization of trace topologies:

```python
# Generate traces
traces = generator.generate_traces(num_traces=10)

# Print all traces
generator.pretty_print_traces(traces)

# Limit the number of traces displayed
generator.pretty_print_traces(traces, max_traces=3)
```

This will output a hierarchical view of the traces with color coding for successful/failed traces and detailed information about each service call.

## Generating Random Service Topologies

You can generate random service topologies with specific characteristics:

```python
import trace_utils

# Generate a random topology with 15 services
services = trace_utils.generate_random_topology(
    num_services=15,       # Total number of services
    max_depth=3,           # Maximum call chain depth
    max_width=4,           # Maximum number of connections per service
    num_service_groups=3,  # Number of logical service groups
    variability=0.4,       # Connection variability
    seed=42                # For reproducibility
)

# Generate traces with this topology
traces = trace_utils.generate_dataset(
    services=services,
    num_traces=200
)

# Visualize the traces
generator = TraceGenerator(services)
generator.pretty_print_traces(traces, max_traces=3)

# Save the topology for future use
import json
topology_json = [s.model_dump() for s in services]
with open("random_topology.json", 'w') as f:
    json.dump(topology_json, f, indent=2)
```

The random topology generator automatically:
- Creates services with appropriate names and types
- Establishes connections between services respecting depth and width constraints
- Avoids circular dependencies
- Maintains proper service hierarchy (proxy → web → database)

## Working with Trace Hierarchies

Traces are hierarchically organized in parent-child relationships to represent the full request flow:

```python
import trace_utils

# Generate traces
services = trace_utils.generate_example_services("microservices")
traces = trace_utils.generate_dataset(services=services, num_traces=100)

# Save to JSON (traces are automatically grouped by their hierarchy)
trace_utils.save_to_json(traces, "traces.json")

# Load traces from a file
loaded_traces = trace_utils.load_from_json("traces.json")

# Get a summary of the trace dataset
trace_utils.print_trace_summary(loaded_traces)

# Extract and view a specific trace hierarchy by its ID
root_trace_id = loaded_traces[0].trace_id  # Get the ID of the first trace
hierarchy = trace_utils.extract_trace_hierarchy(loaded_traces, root_trace_id)
print(f"Extracted hierarchy with {len(hierarchy)} traces")

# Print a specific trace hierarchy
trace_utils.print_trace_summary(loaded_traces, trace_id=root_trace_id)
```

When saving traces to JSON or CSV, the library automatically:
- Groups related traces together (parent-child relationships)
- Maintains proper hierarchical structure
- Preserves the logical flow of requests

## Generating Datasets

You can use the utility functions to generate larger datasets and save them to files:

```python
import trace_utils

# Generate a large dataset
services = trace_utils.generate_example_services("microservices")
traces = trace_utils.generate_dataset(
    services=services,
    num_traces=1000,
    randomization_level=0.3,
    seed=42  # For reproducibility
)

# Save to JSON
trace_utils.save_to_json(traces, "traces_dataset.json")

# Save to CSV for data analysis
trace_utils.save_to_csv(traces, "traces_dataset.csv")

# Load traces back from a file
loaded_traces = trace_utils.load_from_json("traces_dataset.json")
```

## Command-line Interface

The trace generator provides a comprehensive command-line interface:

### Generating Traces

```bash
# Generate a dataset with the default microservices topology
python trace_utils.py generate --num-traces 1000 --json traces.json --csv traces.csv

# Generate a complex topology with high randomization
python trace_utils.py generate --topology complex --num-traces 2000 --randomization 0.5 --json complex_traces.json

# Generate a random topology
python trace_utils.py generate --random-topology --num-services 20 --max-depth 4 --max-width 5 --json random_traces.json

# Save the random topology for future reference
python trace_utils.py generate --random-topology --num-services 20 --save-topology my_topology.json

# Preview the generated traces in the console
python trace_utils.py generate --random-topology --num-services 8 --preview
```

### Analyzing Traces

```bash
# View a summary of traces in a file
python trace_utils.py analyze traces.json

# View a specific trace hierarchy
python trace_utils.py analyze traces.json --trace TRACE_ID_HERE

# Reorganize a trace file to ensure proper hierarchical grouping
python trace_utils.py analyze traces.json --regroup --output reorganized_traces.json

# Limit the number of traces shown in the summary
python trace_utils.py analyze traces.json --max-traces 20
```

### Converting Between Formats

```bash
# Convert from JSON to CSV
python trace_utils.py convert traces.json traces.csv

# Convert and regroup traces (reorganize hierarchically)
python trace_utils.py convert unorganized.json organized.json
```

## Examples

Explore the provided examples to see how to use the trace generator:

```bash
# Run the basic examples
python examples.py

# Generate various datasets
python generate_datasets.py
```

## Service Configuration

Services are defined using the `ServiceConfig` class with the following attributes:

- `name`: Service name (string)
- `service_type`: Type of service - one of "proxy", "web", or "database"
- `connections`: List of service names that this service connects to

## Trace Properties

Each generated trace includes:

- `trace_id`: Unique identifier for the trace
- `service_name`: Name of the service that generated the trace
- `service_type`: Type of service (proxy, web, database)
- `start_time`: Start time of the trace
- `end_time`: End time of the trace
- `status`: Status of the trace (success or error)
- `parent_trace_id`: ID of the parent trace (if applicable)
- `metadata`: Additional metadata specific to the service type

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

The MIT License is a permissive license that is short and to the point. It lets people do almost anything they want with your project, like making and distributing closed source versions, as long as they include the original copyright and license notice in any copy of the project.