"""
History Service for conversation management and analytics
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import asyncio

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class HistoryService:
    """
    Conversation history service with multiple storage backends
    Supports Redis for development and Cosmos DB for production
    """
    
    def __init__(self):
        self._redis_client = None
        self._cosmos_client = None
        self._storage_backend = "redis" if settings.cosmos_db_emulator else "cosmos"
        
    async def __aenter__(self):
        """Initialize storage clients"""
        if self._storage_backend == "cosmos" and settings.cosmos_db_endpoint:
            await self._init_cosmos_client()
        else:
            await self._init_redis_client()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources"""
        if self._redis_client:
            await self._redis_client.close()
        if self._cosmos_client:
            await self._cosmos_client.close()
    
    async def _init_redis_client(self):
        """Initialize Redis client for development"""
        try:
            import aioredis
            self._redis_client = await aioredis.from_url(
                f"redis://:{settings.redis_password}@localhost:6379/0",
                decode_responses=True
            )
            logger.info("Redis client initialized for history service")
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {str(e)}")
            # Fallback to in-memory storage for development
            self._memory_store = {}
    
    async def _init_cosmos_client(self):
        """Initialize Cosmos DB client for production"""
        try:
            from azure.cosmos.aio import CosmosClient
            self._cosmos_client = CosmosClient(
                settings.cosmos_db_endpoint,
                credential=settings.cosmos_db_key
            )
            logger.info("Cosmos DB client initialized for history service")
        except Exception as e:
            logger.error(f"Failed to initialize Cosmos DB client: {str(e)}")
            # Fallback to Redis
            await self._init_redis_client()
    
    async def store_message(
        self,
        conversation_id: str,
        user_id: str,
        message: str,
        response: str,
        citations: List[Dict],
        metadata: Dict[str, Any]
    ):
        """Store a message and its response"""
        try:
            message_data = {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "message": message,
                "response": response,
                "citations": citations,
                "metadata": metadata,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "message"
            }
            
            if self._storage_backend == "cosmos" and self._cosmos_client:
                await self._store_in_cosmos(message_data)
            else:
                await self._store_in_redis(message_data)
                
        except Exception as e:
            logger.error(f"Failed to store message: {str(e)}")
            raise
    
    async def _store_in_cosmos(self, message_data: Dict):
        """Store message in Cosmos DB"""
        database = self._cosmos_client.get_database_client(settings.cosmos_db_database_name)
        container = database.get_container_client(settings.cosmos_db_container_name)
        
        await container.create_item(message_data)
    
    async def _store_in_redis(self, message_data: Dict):
        """Store message in Redis"""
        if self._redis_client:
            key = f"conversation:{message_data['conversation_id']}"
            await self._redis_client.lpush(key, json.dumps(message_data))
            await self._redis_client.expire(key, 86400)  # 24 hours TTL
        else:
            # Fallback to memory
            conv_id = message_data['conversation_id']
            if conv_id not in self._memory_store:
                self._memory_store[conv_id] = []
            self._memory_store[conv_id].append(message_data)
    
    async def get_conversation(self, conversation_id: str, user_id: str) -> Optional[Dict]:
        """Get conversation by ID"""
        try:
            if self._storage_backend == "cosmos" and self._cosmos_client:
                return await self._get_from_cosmos(conversation_id, user_id)
            else:
                return await self._get_from_redis(conversation_id, user_id)
        except Exception as e:
            logger.error(f"Failed to get conversation: {str(e)}")
            return None
    
    async def _get_from_cosmos(self, conversation_id: str, user_id: str) -> Optional[Dict]:
        """Get conversation from Cosmos DB"""
        database = self._cosmos_client.get_database_client(settings.cosmos_db_database_name)
        container = database.get_container_client(settings.cosmos_db_container_name)
        
        query = f"""
        SELECT * FROM c WHERE c.conversation_id = '{conversation_id}' 
        AND c.user_id = '{user_id}' ORDER BY c.timestamp
        """
        
        items = []
        async for item in container.query_items(query=query):
            items.append(item)
        
        if items:
            return {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "messages": items,
                "created_at": items[0]["timestamp"],
                "updated_at": items[-1]["timestamp"]
            }
        
        return None
    
    async def _get_from_redis(self, conversation_id: str, user_id: str) -> Optional[Dict]:
        """Get conversation from Redis"""
        if self._redis_client:
            key = f"conversation:{conversation_id}"
            messages_json = await self._redis_client.lrange(key, 0, -1)
            
            messages = []
            for msg_json in messages_json:
                msg = json.loads(msg_json)
                if msg["user_id"] == user_id:
                    messages.append(msg)
            
            if messages:
                return {
                    "conversation_id": conversation_id,
                    "user_id": user_id,
                    "messages": messages,
                    "created_at": messages[0]["timestamp"],
                    "updated_at": messages[-1]["timestamp"]
                }
        else:
            # Fallback to memory
            if conversation_id in self._memory_store:
                messages = [
                    msg for msg in self._memory_store[conversation_id]
                    if msg["user_id"] == user_id
                ]
                if messages:
                    return {
                        "conversation_id": conversation_id,
                        "user_id": user_id,
                        "messages": messages,
                        "created_at": messages[0]["timestamp"],
                        "updated_at": messages[-1]["timestamp"]
                    }
        
        return None
    
    async def list_user_conversations(
        self, 
        user_id: str, 
        limit: int = 10, 
        offset: int = 0
    ) -> List[Dict]:
        """List user's conversations"""
        try:
            if self._storage_backend == "cosmos" and self._cosmos_client:
                return await self._list_from_cosmos(user_id, limit, offset)
            else:
                return await self._list_from_redis(user_id, limit, offset)
        except Exception as e:
            logger.error(f"Failed to list conversations: {str(e)}")
            return []
    
    async def _list_from_cosmos(self, user_id: str, limit: int, offset: int) -> List[Dict]:
        """List conversations from Cosmos DB"""
        database = self._cosmos_client.get_database_client(settings.cosmos_db_database_name)
        container = database.get_container_client(settings.cosmos_db_container_name)
        
        query = f"""
        SELECT DISTINCT c.conversation_id, c.user_id, c.timestamp as created_at
        FROM c WHERE c.user_id = '{user_id}' 
        ORDER BY c.timestamp DESC OFFSET {offset} LIMIT {limit}
        """
        
        conversations = []
        async for item in container.query_items(query=query):
            conversations.append(item)
        
        return conversations
    
    async def _list_from_redis(self, user_id: str, limit: int, offset: int) -> List[Dict]:
        """List conversations from Redis"""
        conversations = []
        
        if self._redis_client:
            # Get all conversation keys
            keys = await self._redis_client.keys("conversation:*")
            
            for key in keys[offset:offset + limit]:
                messages_json = await self._redis_client.lrange(key, 0, -1)
                if messages_json:
                    first_msg = json.loads(messages_json[0])
                    if first_msg["user_id"] == user_id:
                        conversations.append({
                            "conversation_id": first_msg["conversation_id"],
                            "user_id": user_id,
                            "created_at": first_msg["timestamp"]
                        })
        else:
            # Fallback to memory
            for conv_id, messages in self._memory_store.items():
                user_messages = [
                    msg for msg in messages if msg["user_id"] == user_id
                ]
                if user_messages:
                    conversations.append({
                        "conversation_id": conv_id,
                        "user_id": user_id,
                        "created_at": user_messages[0]["timestamp"]
                    })
        
        # Sort by created_at descending
        conversations.sort(key=lambda x: x["created_at"], reverse=True)
        return conversations[:limit]
    
    async def delete_conversation(self, conversation_id: str, user_id: str) -> bool:
        """Delete a conversation"""
        try:
            if self._storage_backend == "cosmos" and self._cosmos_client:
                return await self._delete_from_cosmos(conversation_id, user_id)
            else:
                return await self._delete_from_redis(conversation_id, user_id)
        except Exception as e:
            logger.error(f"Failed to delete conversation: {str(e)}")
            return False
    
    async def _delete_from_cosmos(self, conversation_id: str, user_id: str) -> bool:
        """Delete conversation from Cosmos DB"""
        database = self._cosmos_client.get_database_client(settings.cosmos_db_database_name)
        container = database.get_container_client(settings.cosmos_db_container_name)
        
        query = f"""
        SELECT * FROM c WHERE c.conversation_id = '{conversation_id}' 
        AND c.user_id = '{user_id}'
        """
        
        deleted_count = 0
        async for item in container.query_items(query=query):
            await container.delete_item(item, partition_key=item["conversation_id"])
            deleted_count += 1
        
        return deleted_count > 0
    
    async def _delete_from_redis(self, conversation_id: str, user_id: str) -> bool:
        """Delete conversation from Redis"""
        if self._redis_client:
            key = f"conversation:{conversation_id}"
            await self._redis_client.delete(key)
            return True
        else:
            # Fallback to memory
            if conversation_id in self._memory_store:
                del self._memory_store[conversation_id]
                return True
        return False
    
    async def store_feedback(self, feedback_data: Dict):
        """Store user feedback"""
        try:
            feedback_data["timestamp"] = datetime.utcnow().isoformat()
            feedback_data["type"] = "feedback"
            
            if self._storage_backend == "cosmos" and self._cosmos_client:
                database = self._cosmos_client.get_database_client(settings.cosmos_db_database_name)
                container = database.get_container_client(settings.cosmos_db_container_name)
                await container.create_item(feedback_data)
            else:
                # Store feedback in Redis with separate key
                if self._redis_client:
                    key = f"feedback:{feedback_data['message_id']}"
                    await self._redis_client.setex(key, 86400, json.dumps(feedback_data))
            
            logger.info(f"Feedback stored: {feedback_data.get('message_id')}")
            
        except Exception as e:
            logger.error(f"Failed to store feedback: {str(e)}")
            raise
    
    async def get_analytics(self, user_id: str, days: int = 30) -> Dict:
        """Get user analytics"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            if self._storage_backend == "cosmos" and self._cosmos_client:
                return await self._get_analytics_from_cosmos(user_id, cutoff_date)
            else:
                return await self._get_analytics_from_redis(user_id, cutoff_date)
        except Exception as e:
            logger.error(f"Failed to get analytics: {str(e)}")
            return {}
    
    async def _get_analytics_from_cosmos(self, user_id: str, cutoff_date: datetime) -> Dict:
        """Get analytics from Cosmos DB"""
        database = self._cosmos_client.get_database_client(settings.cosmos_db_database_name)
        container = database.get_container_client(settings.cosmos_db_container_name)
        
        query = f"""
        SELECT c.metadata, c.timestamp FROM c 
        WHERE c.user_id = '{user_id}' 
        AND c.timestamp > '{cutoff_date.isoformat()}'
        AND c.type = 'message'
        """
        
        messages = []
        async for item in container.query_items(query=query):
            messages.append(item)
        
        return self._calculate_analytics(messages)
    
    async def _get_analytics_from_redis(self, user_id: str, cutoff_date: datetime) -> Dict:
        """Get analytics from Redis"""
        messages = []
        
        if self._redis_client:
            keys = await self._redis_client.keys("conversation:*")
            for key in keys:
                messages_json = await self._redis_client.lrange(key, 0, -1)
                for msg_json in messages_json:
                    msg = json.loads(msg_json)
                    if (msg["user_id"] == user_id and 
                        msg["type"] == "message" and
                        datetime.fromisoformat(msg["timestamp"]) > cutoff_date):
                        messages.append(msg)
        else:
            # Fallback to memory
            for conv_messages in self._memory_store.values():
                for msg in conv_messages:
                    if (msg["user_id"] == user_id and 
                        msg["type"] == "message" and
                        datetime.fromisoformat(msg["timestamp"]) > cutoff_date):
                        messages.append(msg)
        
        return self._calculate_analytics(messages)
    
    def _calculate_analytics(self, messages: List[Dict]) -> Dict:
        """Calculate analytics from messages"""
        if not messages:
            return {
                "total_messages": 0,
                "total_tokens": 0,
                "average_confidence": 0.0,
                "safety_violations": 0,
                "unique_conversations": 0
            }
        
        total_tokens = sum(
            msg.get("metadata", {}).get("token_usage", {}).get("total_tokens", 0)
            for msg in messages
        )
        
        confidence_scores = [
            msg.get("metadata", {}).get("confidence_score", 0.0)
            for msg in messages
        ]
        
        safety_violations = sum(
            1 for msg in messages
            if not msg.get("metadata", {}).get("safety_passed", True)
        )
        
        unique_conversations = len(set(msg["conversation_id"] for msg in messages))
        
        return {
            "total_messages": len(messages),
            "total_tokens": total_tokens,
            "average_confidence": sum(confidence_scores) / len(confidence_scores),
            "safety_violations": safety_violations,
            "unique_conversations": unique_conversations
        }
