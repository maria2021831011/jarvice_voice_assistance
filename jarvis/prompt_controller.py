class PromptController:
    def __init__(self, role):
        self.role = role

    def build_prompt(self, user_input, memory):
        system = f"""
You are JARVIS, a personal AI assistant.
Role: {self.role}

Tutor → Explain clearly
Coder → Write clean code
Mentor → Career guidance
"""

        chat = ""
        for m in memory.get_history():
            chat += f"{m['role']}: {m['message']}\n"

        return f"{system}\n{chat}\nUser: {user_input}\nJARVIS:"
