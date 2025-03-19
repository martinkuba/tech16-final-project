#!/usr/bin/env python3
import requests
import argparse
import json
import os
import sys

class ChatbotClient:
    def __init__(self, server_url="http://localhost:8181"):
        self.server_url = server_url
        self.chat_endpoint = f"{server_url}/chat"
        self.history = []

    def send_message(self, prompt, request_type="all-notes", context=""):
        """Send a message to the chatbot server and get a response."""
        payload = {
            "prompt": prompt,
            "type": request_type,
            "context": context
        }

        try:
            response = requests.post(self.chat_endpoint, json=payload)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error communicating with server: {e}")
            return None

    def print_response(self, response):
        """Pretty print the chatbot response."""
        if not response:
            return

        print("\n" + "="*80)
        print("CHATBOT RESPONSE:")
        print("-"*80)
        print(response.get('response', 'No response received'))
        
        # Print sources if available
        sources = response.get('sources', [])
        if sources:
            print("\nSOURCES:")
            print("-"*80)
            for i, source in enumerate(sources, 1):
                print(f"{i}. {source}")
        print("="*80 + "\n")

    def save_history(self, prompt, response):
        """Save the conversation history."""
        self.history.append({
            "prompt": prompt,
            "response": response
        })

def main():
    parser = argparse.ArgumentParser(description="CLI Chatbot Client")
    parser.add_argument("-s", "--server", default="http://localhost:8181",
                        help="Server URL (default: http://localhost:8181)")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="Run in interactive mode")
    parser.add_argument("prompt", nargs="?", help="Prompt to send to the chatbot")
    
    args = parser.parse_args()
    client = ChatbotClient(args.server)

    if args.interactive:
        print("Chatbot CLI Client")
        print("Type 'exit', 'quit', or use Ctrl+D to exit")
        print("="*80)
        
        try:
            while True:
                try:
                    prompt = input("\nYou: ")
                    if prompt.lower() in ('exit', 'quit'):
                        break
                        
                    if prompt.strip():
                        response = client.send_message(prompt)
                        client.print_response(response)
                        client.save_history(prompt, response)
                except EOFError:
                    break
        except KeyboardInterrupt:
            pass
        
        print("\nExiting chatbot client. Goodbye!")
    
    elif args.prompt:
        response = client.send_message(args.prompt)
        client.print_response(response)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 