import json
import random

class GreetingManager:
	"""
	Fetches and builds greetings.
	"""
	def __init__(self):
		"""
		Initializes GreetingManager.

		Parameters:
			self (GreetingManager)
		"""
		self.join_greetings_filepath = "config/join_greetings.json"
		self.message_greetings_filepath = "config/message_greetings.json"
		self.join_greetings = self.__load_join_greetings()
		self.message_greetings = self.__load_message_greetings()

	def __load_join_greetings(self):
		"""
		Loads join greetings from join_greetings.json.

		Parameters:
			self (GreetingManager)
		"""
		try:
			with open(self.join_greetings_filepath, "r", encoding="utf-8") as f:
				return json.load(f)
		except Exception as e:
			print(f"[GreetingManager] Failed to load join greetings: {e}")
			return ["..."]

	def __load_message_greetings(self):
		"""
		Loads message greetings from message_greetings.json.

		Parameters:
			self (GreetingManager)
		"""
		try:
			with open(self.message_greetings_filepath, "r", encoding="utf-8") as f:
				return json.load(f)
		except Exception as e:
			print(f"[GreetingManager] Failed to load message greetings: {e}")
			return ["..."]

	def get_random_join_greeting(self):
		"""
		Gets a random join greeting.

		Parameters:
			self (GreetingManager)
		"""
		return random.choice(self.join_greetings)

	def get_random_message_greeting(self):
		"""
		Gets a random message greeting.

		Parameters:
			self (GreetingManager)
		"""
		return random.choice(self.message_greetings)