#!/usr/bin/env python3
"""
Examples demonstrating how to use the TraceGenerator and pretty_print_traces.

This script provides several examples of different service topologies and how to 
generate and visualize traces using the pretty_print_traces method.
"""

from trace_generator import ServiceConfig, TraceGenerator

def simple_topology_example():
    """
    A simple topology with a gateway connected to a single backend service and database.
    """
    print("\n\n=========== SIMPLE TOPOLOGY EXAMPLE ===========")
    
    # Define services
    services = [
        ServiceConfig(name="gateway", service_type="proxy", connections=["backend"]),
        ServiceConfig(name="backend", service_type="web", connections=["database"]),
        ServiceConfig(name="database", service_type="database")
    ]
    
    # Create generator
    generator = TraceGenerator(services, randomization_level=0.2)
    
    # Generate a small number of traces
    traces = generator.generate_traces(num_traces=3)
    
    # Pretty print the traces
    generator.pretty_print_traces(traces)


def microservices_topology_example():
    """
    A microservices topology with multiple services and databases.
    """
    print("\n\n=========== MICROSERVICES TOPOLOGY EXAMPLE ===========")
    
    # Define services
    services = [
        ServiceConfig(name="api-gateway", service_type="proxy", connections=["auth-service", "user-service", "order-service"]),
        ServiceConfig(name="auth-service", service_type="web", connections=["user-service", "auth-db"]),
        ServiceConfig(name="user-service", service_type="web", connections=["user-db"]),
        ServiceConfig(name="order-service", service_type="web", connections=["inventory-service", "payment-service", "order-db"]),
        ServiceConfig(name="inventory-service", service_type="web", connections=["inventory-db"]),
        ServiceConfig(name="payment-service", service_type="web", connections=["payment-db"]),
        ServiceConfig(name="auth-db", service_type="database"),
        ServiceConfig(name="user-db", service_type="database"),
        ServiceConfig(name="order-db", service_type="database"),
        ServiceConfig(name="inventory-db", service_type="database"),
        ServiceConfig(name="payment-db", service_type="database"),
    ]
    
    # Create generator
    generator = TraceGenerator(services, randomization_level=0.4, num_groups=5)
    
    # Generate traces
    traces = generator.generate_traces(num_traces=10)
    
    # Pretty print only first 3 traces to avoid console overflow
    generator.pretty_print_traces(traces, max_traces=3)


def high_failure_rate_example():
    """
    An example with a higher randomization level to demonstrate error visualization.
    """
    print("\n\n=========== HIGH FAILURE RATE EXAMPLE ===========")
    
    # Define services
    services = [
        ServiceConfig(name="edge-router", service_type="proxy", connections=["api-service", "static-service"]),
        ServiceConfig(name="api-service", service_type="web", connections=["auth-db", "content-db"]),
        ServiceConfig(name="static-service", service_type="web"),
        ServiceConfig(name="auth-db", service_type="database"),
        ServiceConfig(name="content-db", service_type="database"),
    ]
    
    # Create generator with high randomization (more errors)
    generator = TraceGenerator(services, randomization_level=0.8, num_groups=2)
    
    # Generate traces
    traces = generator.generate_traces(num_traces=5)
    
    # Pretty print the traces
    generator.pretty_print_traces(traces)


def advanced_options_example():
    """
    Examples of using different options with the pretty_print_traces method.
    """
    print("\n\n=========== ADVANCED OPTIONS EXAMPLE ===========")
    
    # Define services
    services = [
        ServiceConfig(name="mobile-api", service_type="proxy", connections=["user-profile", "feed-service"]),
        ServiceConfig(name="user-profile", service_type="web", connections=["user-db"]),
        ServiceConfig(name="feed-service", service_type="web", connections=["feed-db", "cache-service"]),
        ServiceConfig(name="cache-service", service_type="web"),
        ServiceConfig(name="user-db", service_type="database"),
        ServiceConfig(name="feed-db", service_type="database"),
    ]
    
    # Create generator
    generator = TraceGenerator(services)
    
    # Generate a larger number of traces
    traces = generator.generate_traces(num_traces=15)
    
    # Example 1: Show just 1 trace
    print("\n=== Displaying a single trace ===")
    generator.pretty_print_traces(traces, max_traces=1)
    
    # Example 2: Show 5 traces
    print("\n=== Displaying 5 traces ===")
    generator.pretty_print_traces(traces, max_traces=5)
    
    # Example 3: Show all traces
    print("\n=== Displaying all traces ===")
    generator.pretty_print_traces(traces, max_traces=len(traces))


if __name__ == "__main__":
    print("Running TraceGenerator Examples")
    
    # Run examples
    simple_topology_example()
    microservices_topology_example()
    high_failure_rate_example()
    advanced_options_example()
    
    print("\nAll examples completed.") 