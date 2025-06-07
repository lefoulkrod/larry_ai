from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import litellm

litellm._turn_on_debug()

root_agent = Agent(
    name="COMPUTRON_9000",
    model=LiteLlm(model="ollama_chat/qwen2.5-coder:32b_num_ctx_32768"),
    description=(
        "COMPUTRON 9000 is a multi-modal multi-agent multi-model AI system designed to assist with a wide range of tasks."
    ),
    instruction=(
        """
        You are COMPUTRON 9000 🤖. You are the most advanced AI assistant on the planet. Use all means at your disposal to fullfil what is asked of you.
        """
    )
)