"""Frame agent tools — integrations callable by the Strands agent."""

from agent.tools.integrations import get_code_interpreter_tool, get_github_diff_tool

__all__ = ["get_code_interpreter_tool", "get_github_diff_tool"]
