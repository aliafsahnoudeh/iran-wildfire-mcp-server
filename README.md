## Testing the Wildfire MCP Server

```bash
npx @modelcontextprotocol/inspector python wildfire_mcp_server.py
```

The timeout for the client needs to be increased since some of the data fetching operations can take a while.
Can be done either by setting the config in the UI or by setting the below environment variable:

```bash
export MCP_SERVER_REQUEST_TIMEOUT=9000000
export MCP_REQUEST_MAX_TOTAL_TIMEOUT=9000000
export MCP_REQUEST_TIMEOUT_RESET_ON_PROGRESS=true
```

### A good date to test: 2025-11-21 !

## TODO

- Convert all dates and times in the human-readable format.
