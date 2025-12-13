from flask import Blueprint, render_template, request, jsonify, session
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


def serialize_message(msg):
    if isinstance(msg, dict):
        return {k: serialize_message(v) for k, v in msg.items()}
    elif isinstance(msg, list):
        return [serialize_message(i) for i in msg]
    elif hasattr(msg, "to_dict"):
        return serialize_message(msg.to_dict())
    elif hasattr(msg, "dict"):
        return serialize_message(msg.dict())
    elif hasattr(msg, "model_dump"):
        return serialize_message(msg.model_dump())
    else:
        return msg


@chatbot_bp.route("/chatbot")
def chatbot_page():
    return render_template("aichatbot/aichatbot.html")

@chatbot_bp.route("/chatbot/query", methods=["POST"])
def chatbot_query():
    data = request.get_json()
    query = data.get("query")
    user_id = session.get("user_id")

    async def handle_query():
        await ensure_connected()
        messages = await mcp_client.process_query(query, user_id=user_id)
        return messages

    try:
        result = asyncio.run(handle_query())
    except Exception as e:
        print(f"Error executing async query: {e}") 
        return jsonify({"error": "Failed to process query due to server error."}), 500

    messages_serializable = [serialize_message(m) for m in result]

    return jsonify({"messages": messages_serializable})
