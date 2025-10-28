"""
MongoDB Manager for Chat History Persistence
Handles user authentication and conversation storage
"""

from pymongo import MongoClient
from datetime import datetime
from typing import List, Dict, Optional
import os


class MongoDBManager:
    """Manages MongoDB operations for chat history"""

    def __init__(self, connection_string: str = None, database_name: str = "rag_chatbot"):
        """
        Initialize MongoDB connection

        Args:
            connection_string: MongoDB connection URI
            database_name: Database name to use
        """
        # Get connection string from environment or parameter
        self.connection_string = connection_string or os.getenv("MONGODB_URI")

        if not self.connection_string:
            raise ValueError(
                "MongoDB connection string not found. "
                "Set MONGODB_URI environment variable or pass connection_string parameter."
            )

        try:
            # Connect to MongoDB
            self.client = MongoClient(self.connection_string)
            self.db = self.client[database_name]

            # Collections
            self.users = self.db["users"]
            self.conversations = self.db["conversations"]

            # Create indexes for better performance
            self.conversations.create_index([("user_id", 1), ("timestamp", -1)])
            self.users.create_index("user_id", unique=True)

            print(f"✓ Connected to MongoDB database: {database_name}")

        except Exception as e:
            print(f"✗ MongoDB connection error: {e}")
            raise

    def create_user(self, user_id: str, email: str = None, name: str = None) -> Dict:
        """
        Create or update a user

        Args:
            user_id: Unique user identifier
            email: User email (optional)
            name: User display name (optional)

        Returns:
            User document
        """
        # Upsert (insert or update)
        self.users.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "user_id": user_id,
                    "email": email,
                    "name": name or user_id,
                    "last_active": datetime.utcnow()
                },
                "$setOnInsert": {"created_at": datetime.utcnow()}
            },
            upsert=True
        )

        user_data = {
            "user_id": user_id,
            "email": email,
            "name": name or user_id,
            "last_active": datetime.utcnow()
        }

        return user_data

    def get_user(self, user_id: str) -> Optional[Dict]:
        """
        Get user by user_id

        Args:
            user_id: User identifier

        Returns:
            User document or None
        """
        return self.users.find_one({"user_id": user_id})

    def save_message(
        self,
        user_id: str,
        role: str,
        content: str,
        sources: List[str] = None,
        metadata: Dict = None
    ) -> str:
        """
        Save a chat message to MongoDB

        Args:
            user_id: User identifier
            role: Message role ('user' or 'assistant')
            content: Message content
            sources: List of source documents (optional)
            metadata: Additional metadata (optional)

        Returns:
            Message ID
        """
        message = {
            "user_id": user_id,
            "role": role,
            "content": content,
            "sources": sources or [],
            "metadata": metadata or {},
            "timestamp": datetime.utcnow()
        }

        result = self.conversations.insert_one(message)

        # Update user's last active time
        self.users.update_one(
            {"user_id": user_id},
            {"$set": {"last_active": datetime.utcnow()}}
        )

        return str(result.inserted_id)

    def get_chat_history(
        self,
        user_id: str,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict]:
        """
        Retrieve chat history for a user

        Args:
            user_id: User identifier
            limit: Maximum number of messages to return
            skip: Number of messages to skip (for pagination)

        Returns:
            List of message documents
        """
        messages = self.conversations.find(
            {"user_id": user_id}
        ).sort("timestamp", 1).skip(skip).limit(limit)

        return list(messages)

    def get_recent_history(self, user_id: str, hours: int = 24) -> List[Dict]:
        """
        Get recent chat history within specified hours

        Args:
            user_id: User identifier
            hours: Number of hours to look back

        Returns:
            List of recent messages
        """
        from datetime import timedelta

        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        messages = self.conversations.find({
            "user_id": user_id,
            "timestamp": {"$gte": cutoff_time}
        }).sort("timestamp", 1)

        return list(messages)

    def clear_user_history(self, user_id: str) -> int:
        """
        Delete all chat history for a user

        Args:
            user_id: User identifier

        Returns:
            Number of deleted messages
        """
        result = self.conversations.delete_many({"user_id": user_id})
        return result.deleted_count

    def get_conversation_stats(self, user_id: str) -> Dict:
        """
        Get statistics about user's conversations

        Args:
            user_id: User identifier

        Returns:
            Dictionary with stats
        """
        total_messages = self.conversations.count_documents({"user_id": user_id})

        user_messages = self.conversations.count_documents({
            "user_id": user_id,
            "role": "user"
        })

        assistant_messages = self.conversations.count_documents({
            "user_id": user_id,
            "role": "assistant"
        })

        # Get first and last message timestamps
        first_message = self.conversations.find_one(
            {"user_id": user_id},
            sort=[("timestamp", 1)]
        )

        last_message = self.conversations.find_one(
            {"user_id": user_id},
            sort=[("timestamp", -1)]
        )

        return {
            "total_messages": total_messages,
            "user_messages": user_messages,
            "assistant_messages": assistant_messages,
            "first_message_at": first_message["timestamp"] if first_message else None,
            "last_message_at": last_message["timestamp"] if last_message else None
        }

    def export_conversation(self, user_id: str, format: str = "json") -> str:
        """
        Export user's conversation history

        Args:
            user_id: User identifier
            format: Export format ('json' or 'txt')

        Returns:
            Formatted conversation string
        """
        messages = self.get_chat_history(user_id, limit=1000)

        if format == "json":
            import json
            return json.dumps([
                {
                    "role": msg["role"],
                    "content": msg["content"],
                    "timestamp": msg["timestamp"].isoformat(),
                    "sources": msg.get("sources", [])
                }
                for msg in messages
            ], indent=2)

        elif format == "txt":
            lines = []
            for msg in messages:
                timestamp = msg["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
                role = "You" if msg["role"] == "user" else "Bot"
                lines.append(f"[{timestamp}] {role}: {msg['content']}\n")

            return "\n".join(lines)

        else:
            raise ValueError(f"Unsupported format: {format}")

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("✓ MongoDB connection closed")

    def __del__(self):
        """Cleanup on deletion"""
        self.close()
