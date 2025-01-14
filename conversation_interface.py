import logging
# from langchain.prompts import ChatPromptTemplate, SystemMessage, HumanMessage

logger = logging.getLogger(__name__)


class ConversationInterface:
    """
    A skeleton class to demonstrate system-user style interactions.
    You can incorporate LangChain or your LLM library of choice here.
    """

    def __init__(self, system_prompt: str):
        self.system_prompt = system_prompt

    def ask_for_cv_details(self, cv_text: str) -> str:
        """
        Mock method to show how you'd pass user content to a system prompt.
        """
        # In a real scenario, you would do something like:
        # system_msg = SystemMessage(content=self.system_prompt)
        # user_msg = HumanMessage(content=f"Please analyze the following CV text: {cv_text}")
        # Then create a ChatPromptTemplate or pass to your LLM for analysis.

        logger.debug("Asking system to analyze CV text via conversation interface...")
        # For now, just return a mock analysis
        return f"System analyzed the following text:\n{cv_text[:200]}..."
