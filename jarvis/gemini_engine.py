import google.generativeai as genai

class GeminiEngine:
    def __init__(self, api_key):
        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-2.5-flash")
        except Exception as e:
            raise RuntimeError(f"Failed to connect Gemini API: {e}")

    def generate(self, prompt):
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Gemini API Error: {e}"
    def stream(self, prompt):
         try:
           response = self.model.generate_content(prompt, stream=True)
           for chunk in response:
            yield chunk.text
         except Exception as e:
           yield f"Gemini API Error: {e}"
