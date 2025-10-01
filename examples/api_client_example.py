#!/usr/bin/env python
"""
Example client for the NeuroGym API.

This script demonstrates how to interact with the NeuroGym web service
running on Raspberry Pi or any other host.
"""

import requests
import time
from typing import Optional


class NeuroGymClient:
    """Client for interacting with NeuroGym API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Initialize the client.

        Args:
            base_url: Base URL of the NeuroGym API service
        """
        self.base_url = base_url
        self.session_id: Optional[str] = None

    def check_health(self) -> bool:
        """Check if the service is healthy."""
        try:
            response = requests.get(f"{self.base_url}/health")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def list_tasks(self) -> list:
        """Get list of available tasks."""
        response = requests.get(f"{self.base_url}/tasks")
        response.raise_for_status()
        return response.json()["tasks"]

    def create_environment(self, task_name: str, **kwargs) -> dict:
        """
        Create a new environment.

        Args:
            task_name: Name of the task
            **kwargs: Additional parameters for the environment

        Returns:
            Environment information including session_id
        """
        response = requests.post(
            f"{self.base_url}/environments",
            json={"task_name": task_name, "kwargs": kwargs},
        )
        response.raise_for_status()
        data = response.json()
        self.session_id = data["session_id"]
        return data

    def reset(self) -> dict:
        """Reset the environment."""
        if not self.session_id:
            raise ValueError("No active environment session")

        response = requests.post(
            f"{self.base_url}/environments/{self.session_id}/reset"
        )
        response.raise_for_status()
        return response.json()

    def step(self, action: int) -> dict:
        """
        Take a step in the environment.

        Args:
            action: Action to take

        Returns:
            Step result with observation, reward, terminated, truncated, and info
        """
        if not self.session_id:
            raise ValueError("No active environment session")

        response = requests.post(
            f"{self.base_url}/environments/{self.session_id}/step",
            json={"session_id": self.session_id, "action": action},
        )
        response.raise_for_status()
        return response.json()

    def close(self):
        """Close and delete the environment."""
        if self.session_id:
            response = requests.delete(
                f"{self.base_url}/environments/{self.session_id}"
            )
            response.raise_for_status()
            self.session_id = None

    def list_active_sessions(self) -> list:
        """List all active environment sessions."""
        response = requests.get(f"{self.base_url}/environments")
        response.raise_for_status()
        return response.json()["sessions"]


def main():
    """Example usage of the NeuroGym API client."""
    # Initialize client
    client = NeuroGymClient("http://localhost:8000")

    # Check if service is running
    print("Checking service health...")
    if not client.check_health():
        print("ERROR: Service is not healthy or not running!")
        print("Please start the service with: docker compose up -d")
        return

    print("✓ Service is healthy\n")

    # List available tasks
    print("Available tasks:")
    tasks = client.list_tasks()
    print(f"Found {len(tasks)} tasks")
    print("Sample tasks:", tasks[:5])
    print()

    # Create an environment
    print("Creating environment: PerceptualDecisionMaking-v0")
    env_info = client.create_environment(
        "PerceptualDecisionMaking-v0", dt=100, timing={"fixation": 100, "stimulus": 2000}
    )
    print(f"✓ Environment created with session_id: {env_info['session_id']}")
    print(f"  Observation space: {env_info['observation_space']}")
    print(f"  Action space: {env_info['action_space']}")
    print()

    # Run a simple episode
    print("Running episode...")
    reset_result = client.reset()
    print(f"✓ Environment reset")
    print(f"  Initial observation shape: {len(reset_result['observation'])}")

    total_reward = 0
    steps = 0
    max_steps = 50

    try:
        while steps < max_steps:
            # Random action (in a real scenario, use a policy)
            import random

            action = random.randint(0, env_info["action_space"].get("n", 2) - 1)

            # Take step
            result = client.step(action)
            total_reward += result["reward"]
            steps += 1

            if result["terminated"] or result["truncated"]:
                print(f"✓ Episode finished after {steps} steps")
                break

            # Print progress every 10 steps
            if steps % 10 == 0:
                print(f"  Step {steps}: reward={result['reward']:.2f}")

    except KeyboardInterrupt:
        print("\nInterrupted by user")

    print(f"\nEpisode summary:")
    print(f"  Total steps: {steps}")
    print(f"  Total reward: {total_reward:.2f}")
    print(f"  Average reward: {total_reward/steps:.2f}")

    # Cleanup
    print("\nClosing environment...")
    client.close()
    print("✓ Environment closed")

    # Show active sessions
    print("\nActive sessions:")
    sessions = client.list_active_sessions()
    print(f"  {len(sessions)} active session(s)")


if __name__ == "__main__":
    main()
