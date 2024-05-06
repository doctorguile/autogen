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
import os

from autogen import ConversableAgent

student_agent = ConversableAgent(
    name="Student_Agent",
    system_message="You are a student willing to learn.",
    llm_config=llm_config
)
teacher_agent = ConversableAgent(
    name="Teacher_Agent",
    system_message="You are a math teacher.",
    llm_config=llm_config
)

chat_result = student_agent.initiate_chat(
    teacher_agent,
    message="What is triangle inequality?",
    summary_method="reflection_with_llm",
    max_turns=1,
)

print(chat_result.summary)