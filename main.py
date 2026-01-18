import argparse
from dotenv import load_dotenv
from src.agent import DailyPaperAgent

def main():
    parser = argparse.ArgumentParser(description="Daily AI Paper Agent")
    parser.add_argument("--config", default="config.yaml", help="Path to config file")
    
    args = parser.parse_args()
    
    # Load env vars
    load_dotenv()
    
    # Initialize and run agent
    agent = DailyPaperAgent(config_path=args.config)
    agent.wake_up()

if __name__ == "__main__":
    main()
