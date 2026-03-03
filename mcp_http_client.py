import asyncio
from fastmcp.client.transports import StreamableHttpTransport
from mcp import ClientSession
import logging

from contextlib import AsyncExitStack

logging.getLogger("mcp").setLevel(logging.WARNING)


class MCPHTTPCLIENT:
    def __init__(self, server_uri, root_dir):
        self.server_uri = server_uri
        self.root_dir = root_dir
        # aliases used by the Gradio app
        self.server_url = server_uri
        self.roots_dir = root_dir

        self._connected = False
        self.session: ClientSession | None = None
        self._exit_stack = AsyncExitStack()
        self._transport: StreamableHttpTransport | None = None

    @property
    def connected(self) -> bool:
        return self._connected
    
    async def connect(self):
        if self.connected:
            return
        
        mcp_server_uri = f"{self.server_uri.rstrip('/')}/mcp"
        self._transport = StreamableHttpTransport(mcp_server_uri)
        self.session = await self._exit_stack.enter_async_context(
            self._transport.connect_session()
        )
        await self.session.initialize()
        self._connected = True

    # getting existing tools using session that created by mcp server / client
    async def list_tools(self):
        if not self.session:
            raise RuntimeError("Not connected")
        return (await self.session.list_tools()).tools
    
    # calling tool
    async def call_tool(self, tool_name:str, argument:dict):
        if not self.session:
            raise RuntimeError("Not connected")
        return await self.session.call_tool(tool_name, argument)
    

    # list resources :
    async def list_resources(self):
        if not self.session:
            raise RuntimeError("Not connected")
        return (await self.session.list_resource_templates()).resourceTemplates
    
    # calling resources :
    async def read_resource(self,uri:str):
        if not self.session:
            raise RuntimeError("Not connected")
        return await self.session.read_resource(uri)


    # list prompts :
    async  def list_prompts(self):
        if not self.session:
            raise RuntimeError("Not connected")
        return (await self.session.list_prompts()).prompts
    
    # get prompt :
    async def get_prompt(self, prompt_name, prompt_argument):
        if not self.session:
            raise RuntimeError("Not connected")
        return await self.session.get_prompt(prompt_name, prompt_argument)
    
    # clean up and closing the session 
    async def clean_up(self):
        self._connected = False
        await self._exit_stack.aclose()


