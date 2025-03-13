#!/usr/bin/env python3
"""
Dataset Generation Examples

This script demonstrates how to use the trace_utils.py module to generate
different types of trace datasets and save them to files.
"""

from trace_generator import ServiceConfig, TraceGenerator
import trace_utils
import os
import json

# Create a dataset directory if it doesn't exist
os.makedirs("datasets", exist_ok=True)

def generate_simple_dataset():
    """Generate a small dataset with the simple topology."""
    print("\n=== Generating Simple Topology Dataset ===")
    
    # Use the predefined simple topology
    services = trace_utils.generate_example_services("simple")
    
    # Generate 100 traces
    traces = trace_utils.generate_dataset(
        services=services,
        num_traces=100,
        randomization_level=0.2,
        seed=42  # Use a seed for reproducibility
    )
    
    # Save to both JSON and CSV
    trace_utils.save_to_json(traces, "datasets/simple_topology_100.json")
    trace_utils.save_to_csv(traces, "datasets/simple_topology_100.csv")
    
    # Preview a few traces
    generator = TraceGenerator(services)
    print("\nPreview of the generated traces:")
    generator.pretty_print_traces(traces, max_traces=2)


def generate_microservices_dataset():
    """Generate a medium-sized dataset with the microservices topology."""
    print("\n=== Generating Microservices Topology Dataset ===")
    
    # Use the predefined microservices topology
    services = trace_utils.generate_example_services("microservices")
    
    # Generate 500 traces
    traces = trace_utils.generate_dataset(
        services=services,
        num_traces=500,
        randomization_level=0.3,
        num_groups=5,
        seed=43
    )
    
    # Save to both JSON and CSV
    trace_utils.save_to_json(traces, "datasets/microservices_topology_500.json")
    trace_utils.save_to_csv(traces, "datasets/microservices_topology_500.csv")
    
    # Preview a few traces
    generator = TraceGenerator(services)
    print("\nPreview of the generated traces:")
    generator.pretty_print_traces(traces, max_traces=2)


def generate_complex_dataset():
    """Generate a large dataset with the complex topology."""
    print("\n=== Generating Complex Topology Dataset ===")
    
    # Use the predefined complex topology
    services = trace_utils.generate_example_services("complex")
    
    # Generate 1000 traces with high randomization
    traces = trace_utils.generate_dataset(
        services=services,
        num_traces=1000,
        randomization_level=0.5,
        num_groups=8,
        seed=44
    )
    
    # Save to both JSON and CSV
    trace_utils.save_to_json(traces, "datasets/complex_topology_1000.json")
    trace_utils.save_to_csv(traces, "datasets/complex_topology_1000.csv")
    
    # Preview a few traces
    generator = TraceGenerator(services)
    print("\nPreview of the generated traces:")
    generator.pretty_print_traces(traces, max_traces=2)


def generate_custom_dataset():
    """Generate a dataset with a custom service topology."""
    print("\n=== Generating Custom Topology Dataset ===")
    
    # Define a custom service topology
    services = [
        ServiceConfig(name="load-balancer", service_type="proxy", 
                     connections=["app-server-1", "app-server-2", "app-server-3"]),
        ServiceConfig(name="app-server-1", service_type="web", 
                     connections=["cache", "primary-db"]),
        ServiceConfig(name="app-server-2", service_type="web", 
                     connections=["cache", "primary-db"]),
        ServiceConfig(name="app-server-3", service_type="web", 
                     connections=["cache", "read-replica-db"]),
        ServiceConfig(name="cache", service_type="web"),
        ServiceConfig(name="primary-db", service_type="database"),
        ServiceConfig(name="read-replica-db", service_type="database"),
    ]
    
    # Generate 300 traces
    traces = trace_utils.generate_dataset(
        services=services,
        num_traces=300,
        randomization_level=0.3,
        seed=45
    )
    
    # Save to both JSON and CSV
    trace_utils.save_to_json(traces, "datasets/custom_topology_300.json")
    trace_utils.save_to_csv(traces, "datasets/custom_topology_300.csv")
    
    # Preview a few traces
    generator = TraceGenerator(services)
    print("\nPreview of the generated traces:")
    generator.pretty_print_traces(traces, max_traces=2)


def load_and_analyze_dataset():
    """Demonstrate loading a dataset from a file and doing basic analysis."""
    print("\n=== Loading and Analyzing Dataset ===")
    
    # Load traces from the JSON file
    traces = trace_utils.load_from_json("datasets/microservices_topology_500.json")
    
    # Basic analysis: count traces by service type
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


def analyze_trace_hierarchies():
    """Demonstrate working with trace hierarchies."""
    print("\n=== Analyzing Trace Hierarchies ===")
    
    # Let's use the random medium-sized dataset
    file_path = "datasets/random_medium_topology_200.json"
    print(f"Loading traces from {file_path}...")
    traces = trace_utils.load_from_json(file_path)
    
    # Get an overall summary of the dataset
    trace_utils.print_trace_summary(traces, max_traces=3)
    
    # Find the first root trace with an error somewhere in its hierarchy
    root_traces = [t for t in traces if t.parent_trace_id is None]
    error_trace_ids = set(t.trace_id for t in traces if t.status == "error")
    error_parent_ids = set(t.parent_trace_id for t in traces if t.parent_trace_id and t.status == "error")
    error_root_ids = error_trace_ids.intersection(set(t.trace_id for t in root_traces))
    
    if error_root_ids:
        # Found a root trace with an error
        sample_error_root_id = list(error_root_ids)[0]
        print(f"\n=== Examining a trace hierarchy with errors (Root ID: {sample_error_root_id}) ===")
        trace_utils.print_trace_summary(traces, trace_id=sample_error_root_id)
    elif error_parent_ids:
        # Find a root trace that has a child with an error
        for parent_id in error_parent_ids:
            parent_trace = next((t for t in traces if t.trace_id == parent_id), None)
            if parent_trace:
                root_trace = parent_trace
                while root_trace.parent_trace_id:
                    root_trace = next((t for t in traces if t.trace_id == root_trace.parent_trace_id), None)
                    if not root_trace:
                        break
                
                if root_trace:
                    print(f"\n=== Examining a trace hierarchy with errors (Root ID: {root_trace.trace_id}) ===")
                    trace_utils.print_trace_summary(traces, trace_id=root_trace.trace_id)
                    break
    
    # Extract all trace hierarchies and analyze them
    print("\n=== Analyzing All Trace Hierarchies ===")
    
    # Group traces by root trace
    hierarchies = {}
    
    # Find all root traces
    for trace in traces:
        if trace.parent_trace_id is None:
            hierarchies[trace.trace_id] = trace_utils.extract_trace_hierarchy(traces, trace.trace_id)
    
    # Analyze each hierarchy
    hierarchy_stats = []
    for root_id, hierarchy in hierarchies.items():
        success_rate = sum(1 for t in hierarchy if t.status == "success") / len(hierarchy)
        depth = max((hierarchy.index(t) for t in hierarchy), default=0) + 1
        services_used = len(set(t.service_name for t in hierarchy))
        
        hierarchy_stats.append({
            "root_id": root_id,
            "root_service": next(t for t in hierarchy if t.trace_id == root_id).service_name,
            "trace_count": len(hierarchy),
            "success_rate": success_rate,
            "depth": depth,
            "services_used": services_used,
        })
    
    # Sort hierarchies by success rate
    hierarchy_stats.sort(key=lambda h: h["success_rate"])
    
    # Print stats for the least successful hierarchies
    print("\nLeast successful trace hierarchies:")
    for i, stat in enumerate(hierarchy_stats[:3]):
        print(f"  {i+1}. Root ID: {stat['root_id']} - {stat['root_service']}")
        print(f"     Traces: {stat['trace_count']}, Success Rate: {stat['success_rate']*100:.1f}%")
        print(f"     Depth: {stat['depth']}, Services Used: {stat['services_used']}")
    
    # Save a reorganized version of the dataset
    reorganized_file = "datasets/random_medium_topology_200_reorganized.json"
    print(f"\nSaving reorganized traces to {reorganized_file}...")
    trace_utils.save_to_json(traces, reorganized_file)


def generate_random_topology_dataset():
    """Generate datasets using randomly generated service topologies."""
    print("\n=== Generating Random Topology Datasets ===")
    
    # Example 1: Small random topology
    print("\n--- Small Random Topology (5 services) ---")
    services_small = trace_utils.generate_random_topology(
        num_services=5,
        max_depth=2,
        max_width=2,
        num_service_groups=1,
        variability=0.2,
        seed=50
    )
    
    # Show the generated topology
    print(f"Generated topology with {len(services_small)} services:")
    for svc in services_small:
        connections = ", ".join(svc.connections) if svc.connections else "none"
        print(f"  {svc.name} ({svc.service_type}) → {connections}")
    
    # Generate traces
    traces_small = trace_utils.generate_dataset(
        services=services_small,
        num_traces=50,
        randomization_level=0.2,
        seed=51
    )
    
    # Save to file
    trace_utils.save_to_json(traces_small, "datasets/random_small_topology_50.json")
    
    # Preview traces
    generator = TraceGenerator(services_small)
    print("\nPreview of the generated traces:")
    generator.pretty_print_traces(traces_small, max_traces=2)
    
    # Example 2: Medium random topology with more variability
    print("\n--- Medium Random Topology (15 services) ---")
    services_medium = trace_utils.generate_random_topology(
        num_services=15,
        max_depth=3,
        max_width=4,
        num_service_groups=3,
        variability=0.4,
        seed=52
    )
    
    # Generate traces
    traces_medium = trace_utils.generate_dataset(
        services=services_medium,
        num_traces=200,
        randomization_level=0.3,
        num_groups=4,
        seed=53
    )
    
    # Save to file
    trace_utils.save_to_json(traces_medium, "datasets/random_medium_topology_200.json")
    
    # Preview traces
    generator = TraceGenerator(services_medium)
    print("\nPreview of the generated traces:")
    generator.pretty_print_traces(traces_medium, max_traces=2)
    
    # Example 3: Large random topology with high complexity
    print("\n--- Large Random Topology (30 services) ---")
    services_large = trace_utils.generate_random_topology(
        num_services=30,
        max_depth=5,
        max_width=6,
        num_service_groups=5,
        variability=0.5,
        seed=54
    )
    
    # Generate traces
    traces_large = trace_utils.generate_dataset(
        services=services_large,
        num_traces=400,
        randomization_level=0.4,
        num_groups=6,
        seed=55
    )
    
    # Save to both JSON and CSV
    trace_utils.save_to_json(traces_large, "datasets/random_large_topology_400.json")
    trace_utils.save_to_csv(traces_large, "datasets/random_large_topology_400.csv")
    
    # Save topology for future reference
    topology_json = [s.model_dump() for s in services_large]
    with open("datasets/random_large_topology.json", 'w') as f:
        json.dump(topology_json, f, indent=2)
    
    # Preview traces
    generator = TraceGenerator(services_large)
    print("\nPreview of the generated traces:")
    generator.pretty_print_traces(traces_large, max_traces=2)


def generate_realistic_microservices_topology():
    """
    Generate a realistic, large-scale microservices topology that produces traces
    with 10-20 nodes per hierarchy while ensuring relationships follow microservice
    architecture principles.
    """
    print("\n=== Generating Realistic Large-Scale Microservices Topology ===")
    
    # Define a realistic e-commerce microservices architecture
    # Follow the pattern: frontend gateway → BFF → domain services → data access → databases
    services = [
        # API Gateways - entry points
        ServiceConfig(name="api-gateway", service_type="proxy", 
                     connections=["web-bff", "mobile-bff", "partner-api-bff"]),
        
        # Backend-for-Frontend (BFF) layer
        ServiceConfig(name="web-bff", service_type="proxy", 
                     connections=["auth-service", "product-service", "cart-service", "user-service"]),
        ServiceConfig(name="mobile-bff", service_type="proxy", 
                     connections=["auth-service", "product-service", "cart-service", "user-service"]),
        ServiceConfig(name="partner-api-bff", service_type="proxy", 
                     connections=["auth-service", "product-service", "inventory-service"]),
        
        # Core domain services
        ServiceConfig(name="auth-service", service_type="web", 
                     connections=["user-service", "auth-db", "token-service", "session-cache"]),
        ServiceConfig(name="user-service", service_type="web", 
                     connections=["user-db", "user-preferences-service", "notification-service"]),
        ServiceConfig(name="product-service", service_type="web", 
                     connections=["product-db", "catalog-service", "pricing-service", "review-service"]),
        ServiceConfig(name="cart-service", service_type="web", 
                     connections=["cart-db", "product-service", "pricing-service", "promotion-service"]),
        ServiceConfig(name="order-service", service_type="web", 
                     connections=["order-db", "payment-service", "inventory-service", "shipping-service"]),
        ServiceConfig(name="payment-service", service_type="web", 
                     connections=["payment-db", "payment-gateway-service", "fraud-detection-service"]),
        ServiceConfig(name="inventory-service", service_type="web", 
                     connections=["inventory-db", "warehouse-service"]),
        
        # Supporting services
        ServiceConfig(name="token-service", service_type="web", 
                     connections=["token-db"]),
        ServiceConfig(name="session-cache", service_type="web"),
        ServiceConfig(name="user-preferences-service", service_type="web", 
                     connections=["preferences-db"]),
        ServiceConfig(name="notification-service", service_type="web", 
                     connections=["notification-db", "email-service", "sms-service", "push-service"]),
        ServiceConfig(name="catalog-service", service_type="web", 
                     connections=["catalog-db"]),
        ServiceConfig(name="pricing-service", service_type="web", 
                     connections=["pricing-db", "tax-service"]),
        ServiceConfig(name="review-service", service_type="web", 
                     connections=["review-db"]),
        ServiceConfig(name="promotion-service", service_type="web", 
                     connections=["promotion-db"]),
        ServiceConfig(name="shipping-service", service_type="web", 
                     connections=["shipping-db", "logistics-service"]),
        ServiceConfig(name="payment-gateway-service", service_type="web"),
        ServiceConfig(name="fraud-detection-service", service_type="web", 
                     connections=["fraud-db"]),
        ServiceConfig(name="warehouse-service", service_type="web", 
                     connections=["warehouse-db"]),
        ServiceConfig(name="tax-service", service_type="web", 
                     connections=["tax-db"]),
        ServiceConfig(name="logistics-service", service_type="web", 
                     connections=["logistics-db"]),
        ServiceConfig(name="email-service", service_type="web"),
        ServiceConfig(name="sms-service", service_type="web"),
        ServiceConfig(name="push-service", service_type="web"),
        
        # Databases
        ServiceConfig(name="auth-db", service_type="database"),
        ServiceConfig(name="user-db", service_type="database"),
        ServiceConfig(name="product-db", service_type="database"),
        ServiceConfig(name="cart-db", service_type="database"),
        ServiceConfig(name="order-db", service_type="database"),
        ServiceConfig(name="payment-db", service_type="database"),
        ServiceConfig(name="inventory-db", service_type="database"),
        ServiceConfig(name="token-db", service_type="database"),
        ServiceConfig(name="preferences-db", service_type="database"),
        ServiceConfig(name="notification-db", service_type="database"),
        ServiceConfig(name="catalog-db", service_type="database"),
        ServiceConfig(name="pricing-db", service_type="database"),
        ServiceConfig(name="review-db", service_type="database"),
        ServiceConfig(name="promotion-db", service_type="database"),
        ServiceConfig(name="shipping-db", service_type="database"),
        ServiceConfig(name="fraud-db", service_type="database"),
        ServiceConfig(name="warehouse-db", service_type="database"),
        ServiceConfig(name="tax-db", service_type="database"),
        ServiceConfig(name="logistics-db", service_type="database"),
    ]
    
    print(f"Created a realistic microservices topology with {len(services)} services")
    
    # Generate traces with common flows
    generator = TraceGenerator(services, randomization_level=0.2, num_groups=4)
    
    # Checkout flow traces - these will have deeper hierarchies
    print("\nGenerating 50 checkout flow traces (deeper hierarchies)...")
    checkout_traces = []
    
    for _ in range(50):
        # Start a trace from the API gateway
        root_trace_id = f"checkout_trace_{_}"
        
        # Create the trace hierarchy manually to ensure we get realistic patterns
        # Web checkout flow: api-gateway → web-bff → [auth, product, cart, order] → many sub-services
        # This will ensure we get 10-20 nodes per trace
        
        # Level 1: API Gateway
        checkout_traces.append(generator._create_trace(
            trace_id=root_trace_id,
            service_name="api-gateway",
            service_type="proxy",
            parent_trace_id=None
        ))
        
        # Level 2: Web BFF
        bff_trace_id = f"{root_trace_id}_bff"
        checkout_traces.append(generator._create_trace(
            trace_id=bff_trace_id,
            service_name="web-bff",
            service_type="proxy",
            parent_trace_id=root_trace_id
        ))
        
        # Level 3: Auth service (authentication check)
        auth_trace_id = f"{bff_trace_id}_auth"
        checkout_traces.append(generator._create_trace(
            trace_id=auth_trace_id,
            service_name="auth-service",
            service_type="web",
            parent_trace_id=bff_trace_id
        ))
        
        # Level 4: Token and user services (called by auth)
        token_trace_id = f"{auth_trace_id}_token"
        checkout_traces.append(generator._create_trace(
            trace_id=token_trace_id,
            service_name="token-service",
            service_type="web",
            parent_trace_id=auth_trace_id
        ))
        
        # Level 5: Token DB
        checkout_traces.append(generator._create_trace(
            trace_id=f"{token_trace_id}_db",
            service_name="token-db",
            service_type="database",
            parent_trace_id=token_trace_id
        ))
        
        # Level 3: Cart service (get cart)
        cart_trace_id = f"{bff_trace_id}_cart"
        checkout_traces.append(generator._create_trace(
            trace_id=cart_trace_id,
            service_name="cart-service",
            service_type="web",
            parent_trace_id=bff_trace_id
        ))
        
        # Level 4: Cart DB
        checkout_traces.append(generator._create_trace(
            trace_id=f"{cart_trace_id}_db",
            service_name="cart-db",
            service_type="database",
            parent_trace_id=cart_trace_id
        ))
        
        # Level 4: Product service (called by cart to get product details)
        product_trace_id = f"{cart_trace_id}_product"
        checkout_traces.append(generator._create_trace(
            trace_id=product_trace_id,
            service_name="product-service",
            service_type="web",
            parent_trace_id=cart_trace_id
        ))
        
        # Level 5: Product DB
        checkout_traces.append(generator._create_trace(
            trace_id=f"{product_trace_id}_db",
            service_name="product-db",
            service_type="database",
            parent_trace_id=product_trace_id
        ))
        
        # Level 4: Pricing service (called by cart)
        pricing_trace_id = f"{cart_trace_id}_pricing"
        checkout_traces.append(generator._create_trace(
            trace_id=pricing_trace_id,
            service_name="pricing-service",
            service_type="web",
            parent_trace_id=cart_trace_id
        ))
        
        # Level 5: Tax service
        tax_trace_id = f"{pricing_trace_id}_tax"
        checkout_traces.append(generator._create_trace(
            trace_id=tax_trace_id,
            service_name="tax-service",
            service_type="web",
            parent_trace_id=pricing_trace_id
        ))
        
        # Level 6: Tax DB
        checkout_traces.append(generator._create_trace(
            trace_id=f"{tax_trace_id}_db",
            service_name="tax-db",
            service_type="database",
            parent_trace_id=tax_trace_id
        ))
        
        # Level 3: Order service (create order)
        order_trace_id = f"{bff_trace_id}_order"
        checkout_traces.append(generator._create_trace(
            trace_id=order_trace_id,
            service_name="order-service",
            service_type="web",
            parent_trace_id=bff_trace_id
        ))
        
        # Level 4: Order DB
        checkout_traces.append(generator._create_trace(
            trace_id=f"{order_trace_id}_db",
            service_name="order-db",
            service_type="database",
            parent_trace_id=order_trace_id
        ))
        
        # Level 4: Payment service
        payment_trace_id = f"{order_trace_id}_payment"
        checkout_traces.append(generator._create_trace(
            trace_id=payment_trace_id,
            service_name="payment-service",
            service_type="web",
            parent_trace_id=order_trace_id
        ))
        
        # Level 5: Payment gateway
        gateway_trace_id = f"{payment_trace_id}_gateway"
        checkout_traces.append(generator._create_trace(
            trace_id=gateway_trace_id,
            service_name="payment-gateway-service",
            service_type="web",
            parent_trace_id=payment_trace_id
        ))
        
        # Level 5: Fraud detection
        fraud_trace_id = f"{payment_trace_id}_fraud"
        checkout_traces.append(generator._create_trace(
            trace_id=fraud_trace_id,
            service_name="fraud-detection-service",
            service_type="web",
            parent_trace_id=payment_trace_id
        ))
        
        # Level 6: Fraud DB
        checkout_traces.append(generator._create_trace(
            trace_id=f"{fraud_trace_id}_db",
            service_name="fraud-db",
            service_type="database",
            parent_trace_id=fraud_trace_id
        ))
        
        # Level 4: Inventory service (check and update inventory)
        inventory_trace_id = f"{order_trace_id}_inventory"
        checkout_traces.append(generator._create_trace(
            trace_id=inventory_trace_id,
            service_name="inventory-service",
            service_type="web",
            parent_trace_id=order_trace_id
        ))
        
        # Level 5: Inventory DB
        checkout_traces.append(generator._create_trace(
            trace_id=f"{inventory_trace_id}_db",
            service_name="inventory-db",
            service_type="database",
            parent_trace_id=inventory_trace_id
        ))
        
        # Level 5: Warehouse service
        warehouse_trace_id = f"{inventory_trace_id}_warehouse"
        checkout_traces.append(generator._create_trace(
            trace_id=warehouse_trace_id,
            service_name="warehouse-service",
            service_type="web",
            parent_trace_id=inventory_trace_id
        ))
        
        # Level 6: Warehouse DB
        checkout_traces.append(generator._create_trace(
            trace_id=f"{warehouse_trace_id}_db",
            service_name="warehouse-db",
            service_type="database",
            parent_trace_id=warehouse_trace_id
        ))
        
        # Level 4: Shipping service
        shipping_trace_id = f"{order_trace_id}_shipping"
        checkout_traces.append(generator._create_trace(
            trace_id=shipping_trace_id,
            service_name="shipping-service",
            service_type="web",
            parent_trace_id=order_trace_id
        ))
        
        # Level 5: Shipping DB
        checkout_traces.append(generator._create_trace(
            trace_id=f"{shipping_trace_id}_db",
            service_name="shipping-db",
            service_type="database",
            parent_trace_id=shipping_trace_id
        ))
        
        # Level 5: Logistics service
        logistics_trace_id = f"{shipping_trace_id}_logistics"
        checkout_traces.append(generator._create_trace(
            trace_id=logistics_trace_id,
            service_name="logistics-service",
            service_type="web",
            parent_trace_id=shipping_trace_id
        ))
        
        # Level 6: Logistics DB
        checkout_traces.append(generator._create_trace(
            trace_id=f"{logistics_trace_id}_db",
            service_name="logistics-db",
            service_type="database",
            parent_trace_id=logistics_trace_id
        ))
        
        # Level 3: User notification (order confirmation)
        notification_trace_id = f"{bff_trace_id}_notification"
        checkout_traces.append(generator._create_trace(
            trace_id=notification_trace_id,
            service_name="notification-service",
            service_type="web",
            parent_trace_id=bff_trace_id
        ))
        
        # Level 4: Email service
        checkout_traces.append(generator._create_trace(
            trace_id=f"{notification_trace_id}_email",
            service_name="email-service",
            service_type="web", 
            parent_trace_id=notification_trace_id
        ))
    
    # Generate additional random traces
    print("Generating 150 additional random traces...")
    random_traces = generator.generate_traces(num_traces=150)
    
    # Combine all traces
    all_traces = checkout_traces + random_traces
    print(f"Total traces generated: {len(all_traces)}")
    
    # Save the traces and topology
    trace_utils.save_to_json(all_traces, "datasets/realistic_microservices_200.json")
    trace_utils.save_to_csv(all_traces, "datasets/realistic_microservices_200.csv")
    
    # Save the topology
    topology_json = [s.model_dump() for s in services]
    with open("datasets/realistic_microservices_topology.json", 'w') as f:
        json.dump(topology_json, f, indent=2)
    
    # Print statistics about the trace hierarchies
    root_traces = [t for t in all_traces if t.parent_trace_id is None]
    print(f"\nGenerated {len(root_traces)} root traces")
    
    # Let's analyze the size of each hierarchy
    hierarchy_sizes = {}
    for trace in root_traces:
        hierarchy = trace_utils.extract_trace_hierarchy(all_traces, trace.trace_id)
        hierarchy_sizes[trace.trace_id] = len(hierarchy)
    
    # Group by size ranges
    size_ranges = {
        "1-5": 0,
        "6-10": 0,
        "11-15": 0,
        "16-20": 0,
        "21+": 0
    }
    
    for size in hierarchy_sizes.values():
        if size <= 5:
            size_ranges["1-5"] += 1
        elif size <= 10:
            size_ranges["6-10"] += 1
        elif size <= 15:
            size_ranges["11-15"] += 1
        elif size <= 20:
            size_ranges["16-20"] += 1
        else:
            size_ranges["21+"] += 1
    
    print("\nTrace hierarchy size distribution:")
    for size_range, count in size_ranges.items():
        print(f"  {size_range} nodes: {count} traces ({count/len(root_traces)*100:.1f}%)")
    
    # Display a sample of the larger hierarchies
    large_hierarchies = [trace_id for trace_id, size in hierarchy_sizes.items() if size >= 10]
    
    if large_hierarchies:
        sample_trace_id = large_hierarchies[0]
        print(f"\nPreview of a large trace hierarchy (ID: {sample_trace_id}):")
        trace_utils.print_trace_summary(all_traces, trace_id=sample_trace_id)
    
    return all_traces, services


if __name__ == "__main__":
    print("=== Trace Generator Dataset Examples ===")
    
    # Generate different datasets
    generate_simple_dataset()
    generate_microservices_dataset()
    generate_complex_dataset()
    generate_custom_dataset()
    generate_random_topology_dataset()
    generate_realistic_microservices_topology()
    
    # Load and analyze datasets
    load_and_analyze_dataset()
    analyze_trace_hierarchies()
    
    print("\nAll examples completed!") 