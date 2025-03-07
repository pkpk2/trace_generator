from trace_generator import TraceGenerator, ServiceConfig
from datetime import datetime
import json

def main():
    # Define the service architecture
    services = [
        ServiceConfig(
            name="frontend-proxy",
            service_type="proxy",
            connections=["auth-service", "user-service"]
        ),
        ServiceConfig(
            name="auth-service",
            service_type="web",
            connections=["auth-db"]
        ),
        ServiceConfig(
            name="user-service",
            service_type="web",
            connections=["user-db"]
        ),
        ServiceConfig(
            name="auth-db",
            service_type="database",
            connections=[]
        ),
        ServiceConfig(
            name="user-db",
            service_type="database",
            connections=[]
        )
    ]

    # Create the trace generator
    generator = TraceGenerator(
        services=services,
        randomization_level=0.3,  # 30% randomization
        num_groups=3  # Three distinct trace patterns
    )

    # Generate traces
    traces = generator.generate_traces(num_traces=10)

    # Print traces in a readable format
    for trace in traces:
        print(f"\nTrace ID: {trace.trace_id}")
        print(f"Service: {trace.service_name} ({trace.service_type})")
        print(f"Duration: {(trace.end_time - trace.start_time).total_seconds():.3f}s")
        print(f"Status: {trace.status}")
        print(f"Parent Trace: {trace.parent_trace_id or 'None'}")
        print("Metadata:")
        for key, value in trace.metadata.items():
            print(f"  {key}: {value}")

if __name__ == "__main__":
    main() 