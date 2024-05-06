import os

llm_config={"config_list": [
            {
                # "model": "gpt-4",
                "model": "cli-0-gpt35",
                "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
                "api_type": "azure",
                "base_url": os.environ.get("AZURE_OPENAI_API_BASE"),
                "api_version": "2024-02-15-preview",
            },
    ]}

from pprint import pprint
from typing import Annotated, Literal

Operator = Literal["+", "-", "*", "/"]


def calculator(a: int, b: int, operator: Annotated[Operator, "operator"]) -> int:
    if operator == "+":
        return a + b
    elif operator == "-":
        return a - b
    elif operator == "*":
        return a * b
    elif operator == "/":
        return int(a / b)
    else:
        raise ValueError("Invalid operator")
    
import os

from autogen import ConversableAgent

# Let's first define the assistant agent that suggests tool calls.
assistant = ConversableAgent(
    name="Assistant",
    system_message="You are a helpful AI assistant. "
    "You can help with simple calculations. "
    "Return 'TERMINATE' when the task is done.",
    llm_config=llm_config
)

# The user proxy agent is used for interacting with the assistant agent
# and executes tool calls.
user_proxy = ConversableAgent(
    name="User",
    llm_config=False,
    is_termination_msg=lambda msg: msg.get("content") is not None and "TERMINATE" in msg["content"],
    human_input_mode="NEVER",
)

# Register the tool signature with the assistant agent.
assistant.register_for_llm(name="calculator", description="A simple calculator")(calculator)
pprint(assistant.llm_config["tools"])

# Register the tool function with the user proxy agent.
user_proxy.register_for_execution(name="calculator")(calculator)

'''
from autogen import register_function

# Register the calculator function to the two agents.
register_function(
    calculator,
    caller=assistant,  # The assistant agent can suggest calls to the calculator.
    executor=user_proxy,  # The user proxy agent can execute the calculator calls.
    name="calculator",  # By default, the function name is used as the tool name.
    description="A simple calculator",  # A description of the tool.
)
'''

chat_result = user_proxy.initiate_chat(assistant, message="What is (44232 + 13312 / (232 - 32)) * 5?")