from typing import Optional
from contextlib import AsyncExitStack
import traceback
from Birdwatching.utils.logger import logger
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from datetime import datetime
import json
import os
from dotenv import load_dotenv
from anthropic import Anthropic
from anthropic.types import Message

dotenv_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.env"))
load_dotenv(dotenv_path)


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.llm = Anthropic()
        self.tools = []
        self.messages = []
        self.logger = logger

    async def call_tool(self, tool_name: str, tool_args: dict):
        try:
            result = await self.session.call_tool(tool_name, tool_args)
            return result
        except Exception as e:
            self.logger.error(f"Failed to call tool: {str(e)}")
            raise Exception(f"Failed to call tool: {str(e)}")

    async def connect_to_server(self, server_script_path: str):
        try:
            is_python = server_script_path.endswith(".py")
            is_js = server_script_path.endswith(".js")
            if not (is_python or is_js):
                raise ValueError("Server script must be a .py or .js file")

            self.logger.info(
                f"Attempting to connect to server using script: {server_script_path}"
            )
            command = "python" if is_python else "node"
            server_params = StdioServerParameters(
                command=command, args=[server_script_path], env=None
            )

            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            self.stdio, self.write = stdio_transport
            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )

            await self.session.initialize()
            mcp_tools = await self.get_mcp_tools()
            self.tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                }
                for tool in mcp_tools
            ]
            self.logger.info(
                f"Successfully connected to server. Available tools: {[tool['name'] for tool in self.tools]}"
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to server: {str(e)}")
            self.logger.debug(f"Connection error details: {traceback.format_exc()}")
            raise Exception(f"Failed to connect to server: {str(e)}")

    async def get_mcp_tools(self):
        try:
            self.logger.info("Requesting MCP tools from the server.")
            response = await self.session.list_tools()
            tools = response.tools
            return tools
        except Exception as e:
            self.logger.error(f"Failed to get MCP tools: {str(e)}")
            self.logger.debug(f"Error details: {traceback.format_exc()}")
            raise Exception(f"Failed to get tools: {str(e)}")

    async def call_llm(self) -> Message:
        try:
            return self.llm.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1000,
                system = "You are a Birdwatching assistant. Answer general questions without using tools. Use tools only when the user's query explicitly requires information contained in the database. Use can use tools only if the user asks for specific data related to birdwatching posts or documentation. Generally, avoid using tools for casual conversation or unrelated queries.",
                messages=self.messages,
                tools=self.tools,
            )
        except Exception as e:
            self.logger.error(f"Failed to call LLM: {str(e)}")
            raise Exception(f"Failed to call LLM: {str(e)}")

    async def process_query(self, query: str, user_id: Optional[int] = None):
        try:
            self.logger.info(
                f"Processing new query: {query[:100]}..."
            )
            query_with_id = query
            if user_id is not None:
                query_with_id = f"user's id {user_id}. {query}"

            user_message = {"role": "user", "content": query_with_id}
            self.messages.append(user_message)
            await self.log_conversation(self.messages)
            messages = [user_message]

            while True:
                self.logger.debug("Calling Claude API")
                response = await self.call_llm()

                if response.content[0].type == "text" and len(response.content) == 1:
                    assistant_message = {
                        "role": "assistant",
                        "content": response.content[0].text,
                    }
                    self.messages.append(assistant_message)
                    await self.log_conversation(self.messages)
                    messages.append(assistant_message)
                    break

                assistant_message = {
                    "role": "assistant",
                    "content": response.to_dict()["content"],
                }
                self.messages.append(assistant_message)
                await self.log_conversation(self.messages)
                messages.append(assistant_message)

                for content in response.content:
                    if content.type == "text":
                        text_message = {"role": "assistant", "content": content.text}
                        await self.log_conversation(self.messages)
                        messages.append(text_message)
                    elif content.type == "tool_use":
                        tool_name = content.name
                        tool_args = content.input
                        tool_use_id = content.id

                        self.logger.info(
                            f"Executing tool: {tool_name} with args: {tool_args}"
                        )
                        try:
                            result = await self.session.call_tool(tool_name, tool_args)
                            self.logger.info(f"Tool result: {result}")
                            tool_result_message = {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "tool_result",
                                        "tool_use_id": tool_use_id,
                                        "content": result.content,
                                    }
                                ],
                            }
                            self.messages.append(tool_result_message)
                            await self.log_conversation(self.messages)
                            messages.append(tool_result_message)
                        except Exception as e:
                            error_msg = f"Tool execution failed: {str(e)}"
                            self.logger.error(error_msg)
                            raise Exception(error_msg)

            return messages

        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            self.logger.debug(
                f"Query processing error details: {traceback.format_exc()}"
            )
            raise

    async def log_conversation(self, conversation: list):
        os.makedirs("conversations", exist_ok=True)

        serializable_conversation = []
        for message in conversation:
            try:
                serializable_message = {
                    "role": message["role"],
                    "content": []
                }
                
                if isinstance(message["content"], str):
                    serializable_message["content"] = message["content"]                  
                elif isinstance(message["content"], list):
                    for content_item in message["content"]:
                        if hasattr(content_item, 'to_dict'):
                            serializable_message["content"].append(content_item.to_dict())
                        elif hasattr(content_item, 'dict'):
                            serializable_message["content"].append(content_item.dict())
                        elif hasattr(content_item, 'model_dump'):
                            serializable_message["content"].append(content_item.model_dump())
                        else:
                            serializable_message["content"].append(content_item)
                
                serializable_conversation.append(serializable_message)
            except Exception as e:
                self.logger.error(f"Error processing message: {str(e)}")
                self.logger.debug(f"Message content: {message}")
                raise

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filepath = os.path.join("conversations", f"conversation_{timestamp}.json")
        
        try:
            with open(filepath, "w") as f:
                json.dump(serializable_conversation, f, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Error writing conversation to file: {str(e)}")
            self.logger.debug(f"Serializable conversation: {serializable_conversation}")
            raise

    async def cleanup(self):
        try:
            self.logger.info("Cleaning up resources")
            await self.exit_stack.aclose()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
