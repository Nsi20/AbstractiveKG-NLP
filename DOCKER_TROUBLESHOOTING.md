# Docker Network Troubleshooting Guide

## Issue Diagnosis

**Problem**: Cannot pull Neo4j image from Docker Hub
```
Error: failed to authorize: failed to fetch oauth token: dial tcp: lookup auth.docker.io: no such host
```

**Root Cause**: Network connectivity to Docker registry is blocked
- ✅ DNS resolution works (found 8 IP addresses for auth.docker.io)
- ❌ Network connectivity blocked (100% packet loss on ping)
- **Likely cause**: Firewall, proxy, or network restrictions

## Solutions (Try in Order)

### Solution 1: Configure Docker DNS Settings

Docker Desktop may be using incorrect DNS servers. Let's configure it to use reliable public DNS.

**Steps:**
1. Open **Docker Desktop**
2. Click the **Settings** icon (gear icon)
3. Go to **Docker Engine** tab
4. Add DNS configuration to the JSON:

```json
{
  "dns": ["8.8.8.8", "8.8.4.4", "1.1.1.1"]
}
```

5. Click **Apply & Restart**
6. Wait for Docker to restart
7. Try pulling the image again:
```bash
docker pull neo4j:latest
```

### Solution 2: Check Windows Firewall

Your firewall might be blocking Docker's network access.

**Steps:**
1. Open **Windows Security** → **Firewall & network protection**
2. Click **Allow an app through firewall**
3. Find **Docker Desktop** in the list
4. Ensure both **Private** and **Public** are checked
5. If not listed, click **Change settings** → **Allow another app**
6. Browse to: `C:\Program Files\Docker\Docker\Docker Desktop.exe`
7. Add and enable for both networks

### Solution 3: Configure Proxy (If Behind Corporate Network)

If you're on a corporate network with a proxy:

**Steps:**
1. Open **Docker Desktop** → **Settings**
2. Go to **Resources** → **Proxies**
3. Enable **Manual proxy configuration**
4. Enter your proxy details:
   - HTTP Proxy: `http://your-proxy:port`
   - HTTPS Proxy: `http://your-proxy:port`
5. Click **Apply & Restart**

### Solution 4: Use Alternative Registry Mirror

Use a Docker registry mirror that might be accessible:

**Steps:**
1. Open **Docker Desktop** → **Settings** → **Docker Engine**
2. Add registry mirrors:

```json
{
  "registry-mirrors": [
    "https://mirror.gcr.io"
  ],
  "dns": ["8.8.8.8", "8.8.4.4"]
}
```

3. Click **Apply & Restart**
4. Try pulling again

### Solution 5: Download Neo4j Image Manually (Workaround)

If network issues persist, use a pre-downloaded image:

**Option A: Use Docker Save/Load**
1. On a machine with internet access:
```bash
docker pull neo4j:latest
docker save neo4j:latest -o neo4j-latest.tar
```
2. Transfer `neo4j-latest.tar` to your machine
3. Load the image:
```bash
docker load -i neo4j-latest.tar
```

**Option B: Use Alternative Neo4j Installation**
Instead of Docker, install Neo4j directly:
1. Download from: https://neo4j.com/download/
2. Install Neo4j Desktop or Community Edition
3. Update `.env` to use the local installation

### Solution 6: Use Alternative Graph Database

If Neo4j remains inaccessible, use NetworkX for development:

**Create `src/graph_db_networkx.py`:**
```python
import networkx as nx
import matplotlib.pyplot as plt

class NetworkXConnector:
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def add_entity(self, name, label):
        self.graph.add_node(name, label=label)
    
    def add_relation(self, head, relation, tail):
        self.graph.add_edge(head, tail, relation=relation)
    
    def populate_kg(self, kg_data):
        for ent in kg_data.get("entities", []):
            self.add_entity(ent["text"], ent["label"])
        for rel in kg_data.get("relations", []):
            self.add_relation(rel["head"], rel["type"], rel["tail"])
    
    def visualize(self, output_file="knowledge_graph.png"):
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.graph)
        nx.draw(self.graph, pos, with_labels=True, 
                node_color='lightblue', node_size=3000,
                font_size=10, font_weight='bold',
                arrows=True, arrowsize=20)
        edge_labels = nx.get_edge_attributes(self.graph, 'relation')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels)
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Graph saved to {output_file}")
    
    def close(self):
        pass
```

**Update `pipeline.py`:**
```python
# Replace:
from src.graph_db import Neo4jConnector
# With:
from src.graph_db_networkx import NetworkXConnector as Neo4jConnector
```

## Quick Test Commands

After trying any solution, test with:

```bash
# Test DNS
nslookup auth.docker.io

# Test Docker connectivity
docker run hello-world

# Test Neo4j pull
docker pull neo4j:latest

# If successful, start Neo4j
docker-compose up -d

# Check status
docker-compose ps
```

## Verification

Once Neo4j is running:

```bash
# Check container
docker ps

# Access Neo4j Browser
# Open: http://localhost:7474
# Login: neo4j / password123

# Run demo
python demo.py
```

## Common Issues

### "Docker daemon not running"
```bash
# Start Docker Desktop manually
# Or restart Docker service
```

### "Port 7474 or 7687 already in use"
```bash
# Find and stop conflicting process
netstat -ano | findstr :7474
netstat -ano | findstr :7687
```

### "Permission denied"
```bash
# Run PowerShell/CMD as Administrator
```

## Need More Help?

If issues persist:
1. Check Docker Desktop logs: Settings → Troubleshoot → View logs
2. Check Windows Event Viewer for network errors
3. Contact your network administrator if on corporate network
4. Use NetworkX alternative (Solution 6) for development
