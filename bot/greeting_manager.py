import json
import random

class GreetingManager:
	def __init__(self):
		self.join_greetings_filepath = "config/join_greetings.json"
		self.message_greetings_filepath = "config/message_greetings.json"
		self.join_greetings = self._load_join_greetings()
		self.message_greetings = self._load_message_greetings()

	def _load_join_greetings(self):
		try:
			with open(self.join_greetings_filepath, "r", encoding="utf-8") as f:
				return json.load(f)
		except Exception as e:
			print(f"[GreetingManager] Failed to load join greetings: {e}")
			return ["..."]

	def _load_message_greetings(self):
		try:
			with open(self.message_greetings_filepath, "r", encoding="utf-8") as f:
				return json.load(f)
		except Exception as e:
			print(f"[GreetingManager] Failed to load message greetings: {e}")
			return ["..."]

	def get_random_join_greeting(self):
		return random.choice(self.join_greetings)

	def get_random_message_greeting(self):
		return random.choice(self.message_greetings)