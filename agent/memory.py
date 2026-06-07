class ConversationMemory:
    def __init__(self, max_turns: int = 10):
        self.max_turns = max_turns
        self.history = []

    def add_turn(self, question: str, answer: str):
        """Add a conversation turn to memory."""
        self.history.append({
            "question": question,
            "answer": answer
        })
        # Keep only last max_turns
        if len(self.history) > self.max_turns:
            self.history = self.history[-self.max_turns:]

    def get_context(self) -> str:
        """Get conversation history as context string."""
        if not self.history:
            return ""
        
        context = "Previous conversation:\n"
        for turn in self.history:
            context += f"Q: {turn['question']}\n"
            context += f"A: {turn['answer'][:200]}...\n\n"
        return context

    def clear(self):
        """Clear conversation history."""
        self.history = []

    def is_empty(self):
        return len(self.history) == 0