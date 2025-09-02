#!/usr/bin/env python3
"""
Generic Python Script Template Hello 
Author: Your Name
Description: A starter template for Python scripts.
"""

import argparse
import logging
import sys
import os
import json

def setup_logging(verbose: bool):
    """Configure logging."""
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def load_config(config_path: str) -> dict:
    """Load configuration from a JSON file if provided."""
    if config_path and os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    return {}

def main(args):
    """Main execution logic."""
    logging.info("Script started.")
    
    config = load_config(args.config)
    if config:
        logging.debug(f"Loaded config: {config}")
    
    # Example placeholder logic
    logging.info(f"Hello, {args.name}!")
    logging.info(f"Running in mode: {args.mode}")
    
    # You can add your main script logic here
    
    logging.info("Script finished successfully.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generic Python Script Template")
    parser.add_argument(
        "--name", "-n",
        type=str,
        default="World",
        help="Name to greet"
    )
    parser.add_argument(
        "--mode", "-m",
        type=str,
        choices=["dev", "test", "prod"],
        default="dev",
        help="Execution mode"
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default=None,
        help="Path to a JSON configuration file"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose (debug) logging"
    )
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    try:
        main(args)
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        sys.exit(1)
