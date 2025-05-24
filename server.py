from flask import Flask, request, jsonify

app = Flask(__name__)

PROVIDER_ID = "devops-log-provider"

@app.route("/mcp/info", methods=["GET"])
def info():
    return jsonify({
        "provider_id": PROVIDER_ID,
        "description": "Serve last 100 lines of /var/log/syslog",
        "capabilities": ["text/log"]
    })

@app.route("/mcp/query", methods=["POST"])
def query():
    req = request.get_json()
    if req.get("provider") != PROVIDER_ID:
        return jsonify([])
    with open("/var/log/syslog") as f:
        lines = f.readlines()[-100:]
    return jsonify([{
        "query_id": req["query_id"],
        "kind": "text/log",
        "content": "".join(lines),
        "metadata": {"source": "/var/log/syslog"}
    }])

if __name__ == "__main__":
    app.run(port=9000)
