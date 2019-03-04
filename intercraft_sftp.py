import dotenv
import sys

from src.server import Server

def main():

	# Load the environment
	dotenv.load_dotenv()

	# Create the server
	server = Server()

	# Execute the server
	return server.run()


if __name__ == "__main__":
	sys.exit(main())
