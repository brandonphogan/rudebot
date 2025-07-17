import os

def get_data_file(file_name):
	base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	return os.path.join(base_dir, "data", file_name)