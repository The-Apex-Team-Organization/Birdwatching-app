from flask import Blueprint, render_template, request, jsonify
import asyncio
from Birdwatching.utils.mcp_client import MCPClient
import os
from dotenv import load_dotenv

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
load_dotenv(dotenv_path)

chatbot_bp = Blueprint("chatbot", __name__, template_folder="../templates")

mcp_client = MCPClient()
mcp_server_local_path = os.getenv("MCP_SERVER_LOCAL_PATH")

if not mcp_server_local_path:
    raise ValueError("MCP_SERVER_LOCAL_PATH is not set in .env")

async def ensure_connected():
    if not hasattr(mcp_client, "session") or mcp_client.session is None:
        await mcp_client.connect_to_server(mcp_server_local_path)

@chatbot_bp.route("/chatbot")
def chatbot_page():
    return render_template("aichatbot/aichatbot.html")

@chatbot_bp.route("/chatbot/query", methods=["POST"])
def chatbot_query():
    data = request.get_json()
    query = data.get("query")

    async def handle_query():
        await ensure_connected()
        messages = await mcp_client.process_query(query)
        return messages

    result = asyncio.run(handle_query())
    return jsonify({"messages": result})
