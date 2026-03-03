import asyncio
from fastmcp.client.transports import StreamableHttpTransport
from mcp import ClientSession
import logging

from contextlib import AsyncExitStack

logging.getLogger("mcp").setLevel(logging.WARNING)


class MCPHTTPCLIENT :
    def __init__(self, server_uri, root_dir):
        self.server_uri = server_uri
        self.root_dir = root_dir
        self._connected = False
        self.session = None
        self.exit_stack = AsyncExitStack
    
    async def connect(self):
        if self.connected:
            return 
        
        mcp_server_uri = f"{self.server_uri}/mcp"

        read, write,_ = self.exit_stack.enter_async_context(
            StreamableHttpTransport(mcp_server_uri)
        )

        self.session = self.exit_stack.enter_async_context(
            ClientSession(read_stream=read, write_stream=write)
        )

        self.session.initialize()
        self._connected = True

    # getting existing tools using session that created by mcp server / client
    async def list_tools(self):
        return await self.session.list_tools().tools
    
    # calling tool
    async def call_tool(self, tool_name:str, argument:dict):
        return self.session.call_tool(tool_name, argument)
    

    # list resources :
    async def list_resources(self):
        return await self.session.list_resource_templates().resourceTemplates
    
    # calling resources :
    async def read_resource(self,uri:str):
        return await self.sesssion.read_resource(uri)


    # list prompts :
    async  def list_prompts(self):
        return await self.session.list_prompt().prompts
    
    # get prompt :
    async def get_prompt(self, prompt_name, prompt_argument):
        return await self.session.get_prompt(prompt_name, prompt_argument)
    
    # clean up and closing the session 
    async def clean_up(self):
        await self.exit_stack.aclose()


