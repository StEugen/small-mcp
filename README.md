# small-mcp

Test mcp server and client for log analyze (last 100 lines in /var/log)

## Server
Exposes two endpoints:
/mcp/info - exposes available tools
```info
"provider_id": PROVIDER_ID,
"description": "Serve last 100 lines of /var/log/syslog",
"capabilities": ["text/log"]
```
/mcp/query - exposes queries
```payload
"query_id": query_id,
"provider": provider_id,
"kind": kind
```
