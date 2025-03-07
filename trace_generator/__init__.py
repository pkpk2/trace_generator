from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import random
import numpy as np
from pydantic import BaseModel, Field

class ServiceConfig(BaseModel):
    name: str
    service_type: str = Field(..., pattern="^(proxy|web|database)$")
    connections: List[str] = Field(default_factory=list)

class Trace(BaseModel):
    trace_id: str
    service_name: str
    service_type: str
    start_time: datetime
    end_time: datetime
    status: str = Field(..., pattern="^(success|error)$")
    parent_trace_id: Optional[str] = None
    metadata: Dict[str, str] = Field(default_factory=dict)

class TraceGenerator:
    def __init__(
        self,
        services: List[ServiceConfig],
        randomization_level: float = 0.3,
        num_groups: int = 3
    ):
        self.services = {s.name: s for s in services}
        self.randomization_level = max(0.0, min(1.0, randomization_level))
        self.num_groups = max(1, num_groups)
        self._validate_connections()
        
    def _validate_connections(self):
        """Validate that all service connections exist."""
        for service in self.services.values():
            for conn in service.connections:
                if conn not in self.services:
                    raise ValueError(f"Service {service.name} connects to non-existent service {conn}")

    def _generate_trace_id(self) -> str:
        """Generate a unique trace ID."""
        return f"trace_{random.randint(1000, 9999)}_{datetime.now().timestamp()}"

    def _generate_duration(self, service_type: str, group: int) -> float:
        """Generate duration based on service type and group."""
        base_durations = {
            "proxy": 0.1,
            "web": 0.3,
            "database": 0.2
        }
        
        base_duration = base_durations[service_type]
        group_factor = 1.0 + (group / self.num_groups) * 0.5
        random_factor = 1.0 + (random.random() - 0.5) * self.randomization_level
        
        return base_duration * group_factor * random_factor

    def _generate_status(self, group: int) -> str:
        """Generate status based on group and randomization."""
        base_success_rate = 0.95 - (group / self.num_groups) * 0.1
        success_rate = base_success_rate * (1 - self.randomization_level)
        return "success" if random.random() < success_rate else "error"

    def _generate_metadata(self, service_type: str) -> Dict[str, str]:
        """Generate metadata based on service type."""
        metadata = {}
        if service_type == "proxy":
            metadata["http_method"] = random.choice(["GET", "POST", "PUT", "DELETE"])
            metadata["endpoint"] = f"/api/v{random.randint(1, 3)}/resource/{random.randint(1, 100)}"
        elif service_type == "web":
            metadata["component"] = random.choice(["auth", "user", "order", "payment"])
            metadata["operation"] = random.choice(["process", "validate", "transform"])
        elif service_type == "database":
            metadata["query_type"] = random.choice(["SELECT", "INSERT", "UPDATE", "DELETE"])
            metadata["table"] = random.choice(["users", "orders", "products", "inventory"])
        return metadata

    def generate_traces(self, num_traces: int = 100) -> List[Trace]:
        """Generate a list of traces."""
        traces = []
        base_time = datetime.now()
        
        for _ in range(num_traces):
            group = random.randint(0, self.num_groups - 1)
            trace_id = self._generate_trace_id()
            
            # Start with a proxy service
            proxy_service = next(s for s in self.services.values() if s.service_type == "proxy")
            start_time = base_time + timedelta(seconds=random.random() * 3600)
            
            # Generate proxy trace
            proxy_duration = self._generate_duration("proxy", group)
            proxy_trace = Trace(
                trace_id=trace_id,
                service_name=proxy_service.name,
                service_type="proxy",
                start_time=start_time,
                end_time=start_time + timedelta(seconds=proxy_duration),
                status=self._generate_status(group),
                metadata=self._generate_metadata("proxy")
            )
            traces.append(proxy_trace)
            
            # Generate traces for connected services
            current_time = start_time + timedelta(seconds=proxy_duration)
            for conn_name in proxy_service.connections:
                conn_service = self.services[conn_name]
                conn_duration = self._generate_duration(conn_service.service_type, group)
                
                conn_trace = Trace(
                    trace_id=self._generate_trace_id(),
                    service_name=conn_service.name,
                    service_type=conn_service.service_type,
                    start_time=current_time,
                    end_time=current_time + timedelta(seconds=conn_duration),
                    status=self._generate_status(group),
                    parent_trace_id=trace_id,
                    metadata=self._generate_metadata(conn_service.service_type)
                )
                traces.append(conn_trace)
                
                # Recursively generate traces for connected services
                current_time += timedelta(seconds=conn_duration)
        
        return traces 