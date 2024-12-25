import json
import os


# class Singleton(type):
# 	_instances= {}
# 	def __new__(cls, *args, **kwargs):
# 		if cls not in cls._instances:
# 			cls._instances[cls]= super(Singleton, cls).__new__(*args, **kwargs)
# 		return cls._instances[cls]

class GuildConfig():

	config_dir = 'config'

	def __init__(self, guild_id: int):
		self.config = {}
		self.guild_id = guild_id
		self.config_path = f"{self.config_dir}/{self.guild_id}.json"
		self.load_config()

	def dir_exists(self):
		if os.path.exists(self.config_dir):
			return
		os.mkdir(self.config_dir)

	def exists(self):
		return os.path.exists(self.config_path)

	def create_config(self):
		self.dir_exists()
		with open(self.config_path, "w") as f:
			json.dump({
				"cleanup" : True
			}, f)

	def load_config(self):
		if self.exists() is False:
			self.create_config()
		with open(self.config_path, "r") as f:
			self.config = json.load(f)

	def save_config(self):
		with open(self.config_path, "w") as f:
			json.dump(self.config, f)

	def get(self, key):
		return self.config.get(key, None)

	def set(self, key, value):
		self.config[key] = value
		self.save_config()

	def delete(self, key):
		del self.config[key]
		self.save_config()

