
# agent.py — LangChain agent with retriever tool + DB tools + memory
from typing import List
from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import StructuredTool
from langchain.tools.retriever import create_retriever_tool
from langchain.memory import ConversationBufferMemory

from db_tools import find_order, search_faq

def get_retriever_tool(retriever):
    return create_retriever_tool(
        retriever,
        name="doc_retriever",
        description="Search uploaded documents for relevant context. Use before answering document questions."
    )

def get_db_tools():
    order_tool = StructuredTool.from_function(
        func=find_order,
        name="find_order",
        description="Lookup order status by numeric order_id. Use when the user asks about order status."
    )
    faq_tool = StructuredTool.from_function(
        func=search_faq,
        name="search_faq",
        description="Search FAQs for topics like return policy, refund, shipping, password reset."
    )
    return [order_tool, faq_tool]

def build_agent_executor(tools: List):
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.2)
    memory = ConversationBufferMemory(memory_key="history", return_messages=True)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a helpful customer-support and document QA agent. "
                       "Use tools when needed. If you cannot find the answer, say you don't know."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_openai_tools_agent(llm, tools, prompt)
    executor = AgentExecutor(agent=agent, tools=tools, memory=memory, verbose=False, handle_parsing_errors=True, return_intermediate_steps=True)
    return executor
