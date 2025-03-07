# Service Trace Generator

A Python-based tool for generating artificial service traces that simulate real-world distributed system behavior. This tool creates synthetic traces for different types of services (proxy, web services, databases) and their interactions.

## Features

- Generate traces for multiple service types (proxy, web service, database)
- Configurable randomization levels
- Group-based trace generation
- Customizable service connections and dependencies
- Time-based trace generation

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

```python
from trace_generator import TraceGenerator, ServiceConfig

# Define your services
services = [
    ServiceConfig(
        name="frontend-proxy",
        service_type="proxy",
        connections=["web-service-1", "web-service-2"]
    ),
    ServiceConfig(
        name="web-service-1",
        service_type="web",
        connections=["db-1"]
    ),
    ServiceConfig(
        name="db-1",
        service_type="database",
        connections=[]
    )
]

# Create generator
generator = TraceGenerator(
    services=services,
    randomization_level=0.3,  # 30% randomization
    num_groups=3  # Number of distinct trace patterns
)

# Generate traces
traces = generator.generate_traces(num_traces=100)
```

## Configuration

The trace generator accepts the following parameters:

- `services`: List of service configurations
- `randomization_level`: Float between 0 and 1, controlling trace variation
- `num_groups`: Number of distinct trace patterns to generate
- `num_traces`: Number of traces to generate

## Service Types

- `proxy`: Frontend/API gateway services
- `web`: Web application services
- `database`: Database services