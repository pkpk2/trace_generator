#!/usr/bin/env python3
"""
Trace Generator Utilities

Utility functions for generating and saving trace datasets to different file formats.
These utilities allow for generating larger datasets suitable for analysis and testing.
"""

import os
import json
import csv
import argparse
from datetime import datetime
from typing import List, Dict, Optional, Union, Any
import random

from trace_generator import ServiceConfig, Trace, TraceGenerator


def generate_dataset(
    services: List[ServiceConfig],
    num_traces: int = 1000,
    randomization_level: float = 0.3,
    num_groups: int = 3,
    seed: Optional[int] = None
) -> List[Trace]:
    """
    Generate a dataset of traces based on the provided service configuration.
    
    Args:
        services: List of ServiceConfig objects defining the service topology
        num_traces: Number of traces to generate
        randomization_level: Level of randomization (0.0 to 1.0)
        num_groups: Number of performance groups
        seed: Random seed for reproducibility
    
    Returns:
        List of generated Trace objects
    """
    if seed is not None:
        random.seed(seed)
    
    generator = TraceGenerator(services, randomization_level, num_groups)
    traces = generator.generate_traces(num_traces)
    
    return traces


def save_to_json(traces: List[Trace], output_file: str, pretty: bool = True) -> None:
    """
    Save traces to a JSON file.
    
    Args:
        traces: List of Trace objects to save
        output_file: Path to the output file
        pretty: Whether to format the JSON with indentation (pretty print)
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # Group traces by hierarchy to ensure related traces are together
    grouped_traces = []
    trace_map = {trace.trace_id: trace for trace in traces}
    
    # Find root traces (those without parents)
    root_traces = [trace for trace in traces if trace.parent_trace_id is None]
    
    # Build a child map to easily find children of a trace
    child_map = {}
    for trace in traces:
        if trace.parent_trace_id:
            if trace.parent_trace_id not in child_map:
                child_map[trace.parent_trace_id] = []
            child_map[trace.parent_trace_id].append(trace)
    
    # Recursive function to collect traces in hierarchical order
    def collect_traces(trace):
        collected = [trace]
        if trace.trace_id in child_map:
            for child in child_map[trace.trace_id]:
                collected.extend(collect_traces(child))
        return collected
    
    # Collect all traces in proper hierarchical order
    for root_trace in root_traces:
        grouped_traces.extend(collect_traces(root_trace))
    
    # Convert traces to dictionaries, with datetime objects converted to ISO format
    trace_dicts = []
    for trace in grouped_traces:
        trace_dict = trace.model_dump()
        trace_dict["start_time"] = trace_dict["start_time"].isoformat()
        trace_dict["end_time"] = trace_dict["end_time"].isoformat()
        trace_dicts.append(trace_dict)
    
    # Save to file
    with open(output_file, 'w') as f:
        if pretty:
            json.dump(trace_dicts, f, indent=2)
        else:
            json.dump(trace_dicts, f)
    
    print(f"Saved {len(traces)} traces to {output_file} (grouped by trace hierarchy)")


def save_to_csv(traces: List[Trace], output_file: str) -> None:
    """
    Save traces to a CSV file for easy import into spreadsheet or data analysis tools.
    
    Args:
        traces: List of Trace objects to save
        output_file: Path to the output file
    """
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # Group traces by hierarchy (same as in save_to_json)
    grouped_traces = []
    
    # Find root traces (those without parents)
    root_traces = [trace for trace in traces if trace.parent_trace_id is None]
    
    # Build a child map to easily find children of a trace
    child_map = {}
    for trace in traces:
        if trace.parent_trace_id:
            if trace.parent_trace_id not in child_map:
                child_map[trace.parent_trace_id] = []
            child_map[trace.parent_trace_id].append(trace)
    
    # Recursive function to collect traces in hierarchical order
    def collect_traces(trace):
        collected = [trace]
        if trace.trace_id in child_map:
            for child in child_map[trace.trace_id]:
                collected.extend(collect_traces(child))
        return collected
    
    # Collect all traces in proper hierarchical order
    for root_trace in root_traces:
        grouped_traces.extend(collect_traces(root_trace))
    
    # Define CSV headers
    fieldnames = [
        "trace_id", "service_name", "service_type", "start_time", "end_time", 
        "duration_seconds", "status", "parent_trace_id", "hierarchy_level"
    ]
    
    # Add potential metadata fields (we'll take all distinct metadata keys from traces)
    metadata_keys = set()
    for trace in grouped_traces:
        metadata_keys.update(trace.metadata.keys())
    
    # Sort metadata keys for consistent column ordering
    metadata_keys = sorted(metadata_keys)
    fieldnames.extend([f"metadata_{key}" for key in metadata_keys])
    
    # Write to CSV
    with open(output_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        # Determine hierarchy level for each trace
        hierarchy_levels = {}
        for trace in grouped_traces:
            if trace.parent_trace_id is None:
                hierarchy_levels[trace.trace_id] = 0
            else:
                parent_level = hierarchy_levels.get(trace.parent_trace_id, 0)
                hierarchy_levels[trace.trace_id] = parent_level + 1
        
        for trace in grouped_traces:
            # Create row with base trace data
            row = {
                "trace_id": trace.trace_id,
                "service_name": trace.service_name,
                "service_type": trace.service_type,
                "start_time": trace.start_time.isoformat(),
                "end_time": trace.end_time.isoformat(),
                "duration_seconds": (trace.end_time - trace.start_time).total_seconds(),
                "status": trace.status,
                "parent_trace_id": trace.parent_trace_id or "",
                "hierarchy_level": hierarchy_levels.get(trace.trace_id, 0)
            }
            
            # Add metadata fields
            for key in metadata_keys:
                row[f"metadata_{key}"] = trace.metadata.get(key, "")
            
            writer.writerow(row)
    
    print(f"Saved {len(traces)} traces to {output_file} (grouped by trace hierarchy)")


def load_from_json(input_file: str) -> List[Trace]:
    """
    Load traces from a JSON file.
    
    Args:
        input_file: Path to the JSON file containing traces
        
    Returns:
        List of Trace objects
    """
    with open(input_file, 'r') as f:
        trace_dicts = json.load(f)
    
    traces = []
    for trace_dict in trace_dicts:
        # Convert ISO datetime strings back to datetime objects
        trace_dict["start_time"] = datetime.fromisoformat(trace_dict["start_time"])
        trace_dict["end_time"] = datetime.fromisoformat(trace_dict["end_time"])
        traces.append(Trace(**trace_dict))
    
    print(f"Loaded {len(traces)} traces from {input_file}")
    return traces


def generate_random_topology(
    num_services: int = 10,
    max_depth: int = 3,
    max_width: int = 3,
    num_service_groups: int = 2,
    variability: float = 0.3,
    seed: Optional[int] = None
) -> List[ServiceConfig]:
    """
    Generate a random service topology based on the specified parameters.
    
    Args:
        num_services: Total number of services to generate
        max_depth: Maximum depth of the service call chain (layers)
        max_width: Maximum number of services that can be called from one service
        num_service_groups: Number of different logical service groups
        variability: Degree of variability within each group (0.0 to 1.0)
        seed: Random seed for reproducibility
    
    Returns:
        List of ServiceConfig objects defining the generated topology
    """
    if seed is not None:
        random.seed(seed)
    
    if num_services < 3:
        raise ValueError("Number of services must be at least 3 (proxy, web, database)")
    
    if max_depth < 2:
        raise ValueError("Max depth must be at least 2")
    
    # Calculate number of services per type
    # At least one proxy, at least one database, the rest are web services
    num_proxy = max(1, int(num_services * 0.2))  # 20% proxy services
    num_db = max(1, int(num_services * 0.3))     # 30% database services
    num_web = num_services - num_proxy - num_db  # Remaining are web services
    
    # Generate service names for each type
    proxy_names = [f"proxy-{i+1}" for i in range(num_proxy)]
    web_names = [f"service-{i+1}" for i in range(num_web)]
    db_names = [f"db-{i+1}" for i in range(num_db)]
    
    # Create groups of services
    all_services = proxy_names + web_names + db_names
    random.shuffle(all_services)
    
    service_groups = []
    services_per_group = max(1, num_services // num_service_groups)
    
    for i in range(num_service_groups):
        start_idx = i * services_per_group
        end_idx = start_idx + services_per_group if i < num_service_groups - 1 else num_services
        service_groups.append(all_services[start_idx:end_idx])
    
    # Generate connections based on depth and width
    connections = {}
    
    for proxy in proxy_names:
        # Proxy services can connect to web services, respecting max_width
        available_targets = web_names.copy()
        random.shuffle(available_targets)
        width = min(max_width, len(available_targets))
        connections[proxy] = available_targets[:width]
    
    for web in web_names:
        # Web services can connect to other web services or databases
        available_targets = []
        
        # Add some web services (but avoid circular dependencies by using indices)
        web_idx = web_names.index(web)
        later_webs = web_names[web_idx+1:] if web_idx < len(web_names) - 1 else []
        if later_webs and random.random() < 0.7:  # 70% chance to connect to another web service
            available_targets.extend(later_webs)
        
        # Add databases
        available_targets.extend(db_names)
        
        random.shuffle(available_targets)
        width = min(max_width, len(available_targets))
        connections[web] = available_targets[:width]
    
    for db in db_names:
        # Database services don't connect to anything
        connections[db] = []
    
    # Apply depth limitation (ensure we don't exceed max_depth by pruning connections)
    for _ in range(max_depth, 10):  # Cap at 10 iterations to avoid infinite loops
        for service in all_services:
            # Skip if no connections or already at acceptable depth
            if not connections[service]:
                continue
                
            # Check for paths that exceed max_depth
            for target in connections[service][:]:  # Create a copy to modify during iteration
                path_length = find_longest_path(connections, service)
                if path_length > max_depth:
                    # Remove some connections to reduce depth
                    connections[service].remove(target)
                    break
    
    # Apply variability by randomly adding/removing connections
    if variability > 0:
        for service in all_services:
            if random.random() < variability and service not in db_names:
                # Maybe add a connection
                available_targets = []
                if service in proxy_names:
                    available_targets = [s for s in web_names if s not in connections[service]]
                elif service in web_names:
                    available_targets = [s for s in web_names + db_names if s not in connections[service] and s != service]
                
                if available_targets and len(connections[service]) < max_width:
                    connections[service].append(random.choice(available_targets))
                
            if random.random() < variability and connections[service]:
                # Maybe remove a connection
                connections[service].pop(random.randrange(len(connections[service])))
    
    # Create the ServiceConfig objects
    service_configs = []
    
    for service in proxy_names:
        service_configs.append(
            ServiceConfig(name=service, service_type="proxy", connections=connections[service])
        )
    
    for service in web_names:
        service_configs.append(
            ServiceConfig(name=service, service_type="web", connections=connections[service])
        )
    
    for service in db_names:
        service_configs.append(
            ServiceConfig(name=service, service_type="database", connections=[])
        )
    
    return service_configs


def find_longest_path(connections, start_service, visited=None):
    """Helper function to find the longest path from a service in the topology."""
    if visited is None:
        visited = set()
    
    if start_service in visited:
        return 0  # Avoid cycles
    
    visited.add(start_service)
    
    if not connections[start_service]:
        return 1  # Leaf node
    
    max_length = 0
    for next_service in connections[start_service]:
        path_length = find_longest_path(connections, next_service, visited.copy())
        max_length = max(max_length, path_length)
    
    return max_length + 1


def extract_trace_hierarchy(traces: List[Trace], root_trace_id: str) -> List[Trace]:
    """
    Extract a complete trace hierarchy starting from the given root trace ID.
    
    Args:
        traces: List of all Trace objects
        root_trace_id: The ID of the root trace to extract the hierarchy for
        
    Returns:
        List of Trace objects representing the complete hierarchy
    """
    trace_map = {trace.trace_id: trace for trace in traces}
    
    if root_trace_id not in trace_map:
        print(f"Warning: Trace ID {root_trace_id} not found in traces")
        return []
    
    # Find all traces in this hierarchy
    result = []
    
    # Build a child map to easily find children of a trace
    child_map = {}
    for trace in traces:
        if trace.parent_trace_id:
            if trace.parent_trace_id not in child_map:
                child_map[trace.parent_trace_id] = []
            child_map[trace.parent_trace_id].append(trace)
    
    # Recursive function to collect traces in hierarchical order
    def collect_traces(trace_id):
        if trace_id not in trace_map:
            return []
        
        trace = trace_map[trace_id]
        collected = [trace]
        
        if trace_id in child_map:
            for child in child_map[trace_id]:
                collected.extend(collect_traces(child.trace_id))
        
        return collected
    
    # Start collecting from the root trace
    result = collect_traces(root_trace_id)
    
    return result


def print_trace_summary(traces: List[Trace], trace_id: Optional[str] = None, max_traces: int = 10):
    """
    Print a summary of traces, optionally filtering to a specific trace_id and its hierarchy.
    
    Args:
        traces: List of Trace objects
        trace_id: Optional trace ID to filter by (showing only this trace and its children)
        max_traces: Maximum number of root traces to display
    """
    if not traces:
        print("No traces to display.")
        return
    
    # Group traces by their root trace
    trace_map = {trace.trace_id: trace for trace in traces}
    traces_by_parent = {}
    root_traces = []
    
    for trace in traces:
        if trace.parent_trace_id is None:
            root_traces.append(trace)
        else:
            if trace.parent_trace_id not in traces_by_parent:
                traces_by_parent[trace.parent_trace_id] = []
            traces_by_parent[trace.parent_trace_id].append(trace)
    
    # If a specific trace_id is provided, filter to just that trace and its hierarchy
    if trace_id:
        filtered_traces = extract_trace_hierarchy(traces, trace_id)
        if filtered_traces:
            print(f"\n=== Trace Hierarchy for ID: {trace_id} ===")
            
            # Create a temporary TraceGenerator to use its pretty_print_traces method
            from trace_generator import TraceGenerator
            
            # We need to find all services mentioned in the traces
            service_names = set()
            service_types = {}
            service_connections = {}
            
            for t in filtered_traces:
                service_names.add(t.service_name)
                service_types[t.service_name] = t.service_type
            
            # Create minimal ServiceConfig objects
            from trace_generator import ServiceConfig
            services = [
                ServiceConfig(
                    name=name,
                    service_type=service_types.get(name, "web"),
                    connections=[]
                )
                for name in service_names
            ]
            
            generator = TraceGenerator(services)
            generator.pretty_print_traces(filtered_traces)
        else:
            print(f"No traces found with ID {trace_id}")
        return
    
    # Print summary
    print(f"\n=== Trace Summary ===")
    print(f"Total traces: {len(traces)}")
    print(f"Unique services: {len(set(t.service_name for t in traces))}")
    print(f"Root traces: {len(root_traces)}")
    
    # Count by service type
    service_type_counts = {}
    for trace in traces:
        if trace.service_type not in service_type_counts:
            service_type_counts[trace.service_type] = 0
        service_type_counts[trace.service_type] += 1
    
    print("\nCounts by service type:")
    for service_type, count in service_type_counts.items():
        print(f"  {service_type}: {count} traces")
    
    # Count success vs error
    success_count = sum(1 for trace in traces if trace.status == "success")
    error_count = len(traces) - success_count
    
    print(f"\nSuccess rate: {success_count/len(traces)*100:.1f}% ({success_count}/{len(traces)})")
    print(f"Error rate: {error_count/len(traces)*100:.1f}% ({error_count}/{len(traces)})")
    
    # Show sample of root traces
    if root_traces:
        print(f"\nSample of root traces (first {min(max_traces, len(root_traces))}):")
        for i, trace in enumerate(root_traces[:max_traces]):
            children_count = len(traces_by_parent.get(trace.trace_id, []))
            duration = (trace.end_time - trace.start_time).total_seconds()
            print(f"  {i+1}. {trace.trace_id} - {trace.service_name} ({trace.service_type}) - "
                  f"Status: {trace.status}, Children: {children_count}, Duration: {duration:.3f}s")
    
    print("\nUse print_trace_summary(traces, trace_id='...') to view a specific trace hierarchy")


def generate_example_services(topology_type: str = "microservices") -> List[ServiceConfig]:
    """
    Generate example service configurations based on predefined topologies.
    
    Args:
        topology_type: Type of topology to generate. Options:
            - "simple": A simple 3-service topology
            - "microservices": A microservices architecture
            - "complex": A more complex service mesh
    
    Returns:
        List of ServiceConfig objects defining the services
    """
    if topology_type == "simple":
        return [
            ServiceConfig(name="gateway", service_type="proxy", connections=["backend"]),
            ServiceConfig(name="backend", service_type="web", connections=["database"]),
            ServiceConfig(name="database", service_type="database")
        ]
    
    elif topology_type == "microservices":
        return [
            ServiceConfig(name="api-gateway", service_type="proxy", 
                         connections=["auth-service", "user-service", "order-service"]),
            ServiceConfig(name="auth-service", service_type="web", 
                         connections=["user-service", "auth-db"]),
            ServiceConfig(name="user-service", service_type="web", 
                         connections=["user-db"]),
            ServiceConfig(name="order-service", service_type="web", 
                         connections=["inventory-service", "payment-service", "order-db"]),
            ServiceConfig(name="inventory-service", service_type="web", 
                         connections=["inventory-db"]),
            ServiceConfig(name="payment-service", service_type="web", 
                         connections=["payment-db"]),
            ServiceConfig(name="auth-db", service_type="database"),
            ServiceConfig(name="user-db", service_type="database"),
            ServiceConfig(name="order-db", service_type="database"),
            ServiceConfig(name="inventory-db", service_type="database"),
            ServiceConfig(name="payment-db", service_type="database"),
        ]
    
    elif topology_type == "complex":
        return [
            ServiceConfig(name="edge-gateway", service_type="proxy", 
                         connections=["web-frontend", "mobile-api", "partner-api"]),
            ServiceConfig(name="web-frontend", service_type="proxy", 
                         connections=["auth-service", "user-service", "product-service"]),
            ServiceConfig(name="mobile-api", service_type="proxy", 
                         connections=["auth-service", "user-service", "product-service"]),
            ServiceConfig(name="partner-api", service_type="proxy", 
                         connections=["auth-service", "product-service", "analytics-service"]),
            ServiceConfig(name="auth-service", service_type="web", 
                         connections=["user-service", "auth-db", "cache-service"]),
            ServiceConfig(name="user-service", service_type="web", 
                         connections=["user-db", "notification-service"]),
            ServiceConfig(name="product-service", service_type="web", 
                         connections=["product-db", "inventory-service", "cache-service"]),
            ServiceConfig(name="inventory-service", service_type="web", 
                         connections=["inventory-db", "supplier-service"]),
            ServiceConfig(name="supplier-service", service_type="web", 
                         connections=["supplier-db"]),
            ServiceConfig(name="notification-service", service_type="web", 
                         connections=["notification-db", "email-service", "sms-service"]),
            ServiceConfig(name="analytics-service", service_type="web", 
                         connections=["analytics-db", "reporting-service"]),
            ServiceConfig(name="reporting-service", service_type="web", 
                         connections=["reporting-db"]),
            ServiceConfig(name="cache-service", service_type="web"),
            ServiceConfig(name="email-service", service_type="web"),
            ServiceConfig(name="sms-service", service_type="web"),
            ServiceConfig(name="auth-db", service_type="database"),
            ServiceConfig(name="user-db", service_type="database"),
            ServiceConfig(name="product-db", service_type="database"),
            ServiceConfig(name="inventory-db", service_type="database"),
            ServiceConfig(name="supplier-db", service_type="database"),
            ServiceConfig(name="notification-db", service_type="database"),
            ServiceConfig(name="analytics-db", service_type="database"),
            ServiceConfig(name="reporting-db", service_type="database"),
        ]
    
    else:
        raise ValueError(f"Unknown topology type: {topology_type}")


def main():
    """
    Command-line interface for generating and saving trace datasets.
    """
    parser = argparse.ArgumentParser(description="Generate and save trace datasets")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate trace datasets")
    
    # Dataset generation parameters
    topology_group = gen_parser.add_mutually_exclusive_group()
    topology_group.add_argument("--topology", type=str, default="",
                        choices=["simple", "microservices", "complex"],
                        help="Type of predefined service topology to generate")
    topology_group.add_argument("--random-topology", action="store_true",
                        help="Generate a random topology instead of using predefined ones")
    
    gen_parser.add_argument("--num-traces", type=int, default=1000,
                        help="Number of traces to generate")
    gen_parser.add_argument("--randomization", type=float, default=0.3,
                        help="Randomization level (0.0 to 1.0)")
    gen_parser.add_argument("--num-groups", type=int, default=3,
                        help="Number of performance groups")
    gen_parser.add_argument("--seed", type=int, default=None,
                        help="Random seed for reproducible generation")
    
    # Random topology parameters
    random_topo_group = gen_parser.add_argument_group("Random Topology Options")
    random_topo_group.add_argument("--num-services", type=int, default=10,
                            help="Number of services in random topology")
    random_topo_group.add_argument("--max-depth", type=int, default=3,
                            help="Maximum depth of service call chains")
    random_topo_group.add_argument("--max-width", type=int, default=3,
                            help="Maximum number of services one service can call")
    random_topo_group.add_argument("--service-groups", type=int, default=2,
                            help="Number of logical service groups")
    random_topo_group.add_argument("--variability", type=float, default=0.3,
                            help="Degree of connection variability (0.0 to 1.0)")
    
    # Output parameters
    gen_parser.add_argument("--json", type=str, default="",
                        help="Output JSON file path")
    gen_parser.add_argument("--csv", type=str, default="",
                        help="Output CSV file path")
    gen_parser.add_argument("--no-pretty", action="store_true",
                        help="Don't pretty-print JSON output")
    gen_parser.add_argument("--preview", action="store_true",
                        help="Preview the generated traces in the console")
    gen_parser.add_argument("--preview-max", type=int, default=5,
                        help="Maximum number of traces to preview")
    gen_parser.add_argument("--save-topology", type=str, default="",
                        help="Save the service topology to a JSON file")
    
    # Analyze command
    analyze_parser = subparsers.add_parser("analyze", help="Analyze existing trace datasets")
    analyze_parser.add_argument("input_file", type=str, help="JSON file containing traces to analyze")
    analyze_parser.add_argument("--trace", type=str, default=None,
                               help="Specific trace ID to analyze (shows the full hierarchy)")
    analyze_parser.add_argument("--max-traces", type=int, default=10,
                               help="Maximum number of root traces to include in summary")
    analyze_parser.add_argument("--regroup", action="store_true",
                               help="Re-group and save traces by hierarchy (reorganize the file)")
    analyze_parser.add_argument("--output", type=str, default="",
                               help="Output file for regrouped traces (required with --regroup)")
    
    # Convert command
    convert_parser = subparsers.add_parser("convert", help="Convert between trace file formats")
    convert_parser.add_argument("input_file", type=str, help="Input trace file (JSON)")
    convert_parser.add_argument("output_file", type=str, help="Output file path (.json or .csv)")
    convert_parser.add_argument("--no-pretty", action="store_true",
                               help="Don't pretty-print JSON output")
    
    args = parser.parse_args()
    
    # Default to generate command if none specified
    if not args.command:
        args.command = "generate"
    
    # Process generate command
    if args.command == "generate":
        # Generate services based on topology or random parameters
        if args.random_topology:
            print(f"Generating random topology with {args.num_services} services, max depth {args.max_depth}, max width {args.max_width}...")
            services = generate_random_topology(
                num_services=args.num_services,
                max_depth=args.max_depth,
                max_width=args.max_width,
                num_service_groups=args.service_groups,
                variability=args.variability,
                seed=args.seed
            )
            topology_name = "random"
        else:
            # Default to microservices if not specified
            topology_type = args.topology if args.topology else "microservices"
            services = generate_example_services(topology_type)
            topology_name = topology_type
            print(f"Using predefined {topology_type} topology with {len(services)} services")
        
        # Save topology if requested
        if args.save_topology:
            topology_file = args.save_topology
            service_dicts = [s.model_dump() for s in services]
            with open(topology_file, 'w') as f:
                json.dump(service_dicts, f, indent=2)
            print(f"Saved service topology to {topology_file}")
        
        # Generate dataset
        print(f"Generating {args.num_traces} traces...")
        traces = generate_dataset(
            services=services,
            num_traces=args.num_traces,
            randomization_level=args.randomization,
            num_groups=args.num_groups,
            seed=args.seed
        )
        
        # Preview traces if requested
        if args.preview:
            generator = TraceGenerator(services)
            print("\n=== Trace Preview ===")
            generator.pretty_print_traces(traces, max_traces=args.preview_max)
        
        # Save to JSON if path provided
        if args.json:
            save_to_json(traces, args.json, pretty=not args.no_pretty)
        
        # Save to CSV if path provided
        if args.csv:
            save_to_csv(traces, args.csv)
        
        # If no output specified, save to default files
        if not args.json and not args.csv:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_json = f"traces_{topology_name}_{args.num_traces}_{timestamp}.json"
            save_to_json(traces, default_json, pretty=not args.no_pretty)
    
    # Process analyze command
    elif args.command == "analyze":
        print(f"Loading traces from {args.input_file}...")
        traces = load_from_json(args.input_file)
        
        # Print summary or specific trace hierarchy
        print_trace_summary(traces, trace_id=args.trace, max_traces=args.max_traces)
        
        # Regroup and save if requested
        if args.regroup:
            if not args.output:
                print("Error: --output is required with --regroup")
                return
            
            print(f"Regrouping traces and saving to {args.output}...")
            save_to_json(traces, args.output, pretty=True)
    
    # Process convert command
    elif args.command == "convert":
        print(f"Converting {args.input_file} to {args.output_file}...")
        traces = load_from_json(args.input_file)
        
        if args.output_file.endswith(".json"):
            save_to_json(traces, args.output_file, pretty=not args.no_pretty)
        elif args.output_file.endswith(".csv"):
            save_to_csv(traces, args.output_file)
        else:
            print(f"Error: Unsupported output format. Use .json or .csv extension.")


if __name__ == "__main__":
    main() 