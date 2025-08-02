#!/usr/bin/env python3
"""
Conversational Memory System for Djinn Council
Provides persistent, shared memory across all models and sessions
"""

import json
import time
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from dataclasses import dataclass, asdict, field

@dataclass
class ConversationTurn:
    """A single turn in the conversation"""
    timestamp: datetime
    user_query: str
    council_response: str
    individual_responses: Dict[str, str]  # djinn_name -> response
    consensus_mode: str
    confidence_scores: Dict[str, float]  # djinn_name -> confidence
    session_id: str
    turn_id: str

@dataclass
class UserProfile:
    """User preferences and characteristics learned over time"""
    preferred_consensus_mode: str = "weighted_roles"
    interaction_style: str = "balanced"  # technical, casual, formal, balanced
    common_topics: List[str] = field(default_factory=list)
    model_preferences: Dict[str, str] = field(default_factory=dict)  # role -> preferred_model
    response_length_preference: str = "detailed"  # brief, detailed, comprehensive
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)

@dataclass
class ConversationSummary:
    """Summary of conversation topics and key points"""
    main_topics: List[str]
    key_decisions: List[str]
    unresolved_questions: List[str]
    important_context: List[str]
    last_updated: datetime
    turn_count: int

class ConversationalMemory:
    """
    Advanced conversational memory system with persistence and intelligent context management
    """
    
    def __init__(self, memory_dir: str = "djinn_memory", user_id: str = "default_user"):
        self.memory_dir = Path(memory_dir)
        self.user_id = user_id
        self.memory_dir.mkdir(exist_ok=True)
        
        # Memory components
        self.conversation_history: List[ConversationTurn] = []
        self.user_profile: UserProfile = UserProfile()
        self.conversation_summary: ConversationSummary = ConversationSummary(
            main_topics=[], key_decisions=[], unresolved_questions=[],
            important_context=[], last_updated=datetime.now(), turn_count=0
        )
        
        # Configuration
        self.max_context_turns = 20  # How many recent turns to include in full context
        self.max_summary_topics = 10
        self.auto_summarize_threshold = 50  # Turns before auto-summarization
        
        # File paths
        self.conversation_file = self.memory_dir / f"{user_id}_conversation.jsonl"
        self.profile_file = self.memory_dir / f"{user_id}_profile.json"
        self.summary_file = self.memory_dir / f"{user_id}_summary.json"
        
        # Load existing memory
        self._load_memory()
    
    def _load_memory(self):
        """Load existing memory from disk"""
        # Load conversation history
        if self.conversation_file.exists():
            try:
                with open(self.conversation_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            turn = ConversationTurn(
                                timestamp=datetime.fromisoformat(data['timestamp']),
                                user_query=data['user_query'],
                                council_response=data['council_response'],
                                individual_responses=data['individual_responses'],
                                consensus_mode=data['consensus_mode'],
                                confidence_scores=data['confidence_scores'],
                                session_id=data['session_id'],
                                turn_id=data['turn_id']
                            )
                            self.conversation_history.append(turn)
                print(f"Loaded {len(self.conversation_history)} conversation turns")
            except Exception as e:
                print(f"Error loading conversation history: {e}")
        
        # Load user profile
        if self.profile_file.exists():
            try:
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_profile = UserProfile(
                        preferred_consensus_mode=data.get('preferred_consensus_mode', 'weighted_roles'),
                        interaction_style=data.get('interaction_style', 'balanced'),
                        common_topics=data.get('common_topics', []),
                        model_preferences=data.get('model_preferences', {}),
                        response_length_preference=data.get('response_length_preference', 'detailed'),
                        created_at=datetime.fromisoformat(data['created_at']),
                        last_updated=datetime.fromisoformat(data['last_updated'])
                    )
                print(f"Loaded user profile (created: {self.user_profile.created_at.strftime('%Y-%m-%d')})")
            except Exception as e:
                print(f"Error loading user profile: {e}")
        
        # Load conversation summary
        if self.summary_file.exists():
            try:
                with open(self.summary_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.conversation_summary = ConversationSummary(
                        main_topics=data['main_topics'],
                        key_decisions=data['key_decisions'],
                        unresolved_questions=data['unresolved_questions'],
                        important_context=data['important_context'],
                        last_updated=datetime.fromisoformat(data['last_updated']),
                        turn_count=data['turn_count']
                    )
                print(f"Loaded conversation summary ({self.conversation_summary.turn_count} turns)")
            except Exception as e:
                print(f"Error loading conversation summary: {e}")
    
    def add_conversation_turn(self, user_query: str, council_response: str, 
                           individual_responses: Dict[str, str], consensus_mode: str,
                           confidence_scores: Dict[str, float], session_id: str) -> str:
        """Add a new conversation turn to memory"""
        
        # Generate unique turn ID
        turn_id = hashlib.md5(f"{session_id}_{user_query}_{time.time()}".encode()).hexdigest()[:8]
        
        # Create conversation turn
        turn = ConversationTurn(
            timestamp=datetime.now(),
            user_query=user_query,
            council_response=council_response,
            individual_responses=individual_responses,
            consensus_mode=consensus_mode,
            confidence_scores=confidence_scores,
            session_id=session_id,
            turn_id=turn_id
        )
        
        # Add to memory
        self.conversation_history.append(turn)
        
        # Update user profile based on this interaction
        self._update_user_profile(turn)
        
        # Update conversation summary
        self._update_conversation_summary(turn)
        
        # Persist to disk
        self._save_conversation_turn(turn)
        self._save_user_profile()
        self._save_conversation_summary()
        
        # Check if we need to summarize old conversations
        if len(self.conversation_history) > self.auto_summarize_threshold:
            self._auto_summarize_old_conversations()
        
        return turn_id
    
    def get_context_for_models(self, include_recent_turns: int = None) -> str:
        """
        Generate context string that all models will receive
        This creates a comprehensive context that any model can understand
        """
        if include_recent_turns is None:
            include_recent_turns = self.max_context_turns
        
        context_parts = []
        
        # User profile context
        context_parts.append("=== USER CONTEXT ===")
        context_parts.append(f"User interaction style: {self.user_profile.interaction_style}")
        context_parts.append(f"Preferred response length: {self.user_profile.response_length_preference}")
        
        if self.user_profile.common_topics:
            context_parts.append(f"User's common topics: {', '.join(self.user_profile.common_topics[:5])}")
        
        # Conversation summary context
        if self.conversation_summary.main_topics:
            context_parts.append(f"\n=== CONVERSATION THEMES ===")
            context_parts.append(f"Main topics discussed: {', '.join(self.conversation_summary.main_topics)}")
        
        if self.conversation_summary.key_decisions:
            context_parts.append(f"Previous key decisions: {'; '.join(self.conversation_summary.key_decisions[-3:])}")
        
        if self.conversation_summary.unresolved_questions:
            context_parts.append(f"Unresolved questions: {'; '.join(self.conversation_summary.unresolved_questions[-3:])}")
        
        # Recent conversation history
        recent_turns = self.conversation_history[-include_recent_turns:] if self.conversation_history else []
        
        if recent_turns:
            context_parts.append(f"\n=== RECENT CONVERSATION ({len(recent_turns)} turns) ===")
            
            for i, turn in enumerate(recent_turns, 1):
                # Format timestamp
                time_ago = self._format_time_ago(turn.timestamp)
                
                context_parts.append(f"\n[Turn {i} - {time_ago}]")
                context_parts.append(f"User: {turn.user_query}")
                context_parts.append(f"Council Decision: {turn.council_response[:300]}{'...' if len(turn.council_response) > 300 else ''}")
                
                # Include key individual insights if they were significantly different
                if len(turn.individual_responses) > 1:
                    diverse_responses = self._get_diverse_responses(turn.individual_responses)
                    if diverse_responses:
                        context_parts.append("Key perspectives:")
                        for djinn, response in diverse_responses.items():
                            context_parts.append(f"  {djinn}: {response[:150]}{'...' if len(response) > 150 else ''}")
        
        # Current context summary
        context_parts.append(f"\n=== CURRENT SESSION CONTEXT ===")
        context_parts.append(f"Total conversation history: {len(self.conversation_history)} turns")
        context_parts.append(f"User since: {self.user_profile.created_at.strftime('%Y-%m-%d')}")
        context_parts.append("You have access to this full conversation context. Reference previous discussions naturally.")
        
        return "\n".join(context_parts)
    
    def _format_time_ago(self, timestamp: datetime) -> str:
        """Format how long ago something happened"""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days > 0:
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "just now"
    
    def _get_diverse_responses(self, individual_responses: Dict[str, str]) -> Dict[str, str]:
        """Get responses that differ significantly from each other"""
        if len(individual_responses) <= 2:
            return individual_responses
        
        # Simple diversity check - responses that start very differently
        diverse = {}
        seen_starts = set()
        
        for djinn, response in individual_responses.items():
            start = response[:100].lower()
            if not any(start.startswith(seen[:50]) for seen in seen_starts):
                diverse[djinn] = response
                seen_starts.add(start)
                if len(diverse) >= 3:  # Limit to 3 diverse responses
                    break
        
        return diverse
    
    def _update_user_profile(self, turn: ConversationTurn):
        """Update user profile based on new interaction"""
        self.user_profile.last_updated = datetime.now()
        
        # Track consensus mode preferences
        if hasattr(self, '_consensus_mode_counts'):
            self._consensus_mode_counts = getattr(self, '_consensus_mode_counts', {})
        else:
            self._consensus_mode_counts = {}
        
        self._consensus_mode_counts[turn.consensus_mode] = self._consensus_mode_counts.get(turn.consensus_mode, 0) + 1
        
        # Update preferred consensus mode if we have enough data
        if sum(self._consensus_mode_counts.values()) >= 5:
            self.user_profile.preferred_consensus_mode = max(self._consensus_mode_counts, key=self._consensus_mode_counts.get)
        
        # Extract topics from user query (simple keyword extraction)
        query_words = set(turn.user_query.lower().split())
        topic_keywords = query_words.intersection({
            'code', 'programming', 'api', 'database', 'security', 'design', 'architecture',
            'strategy', 'business', 'analysis', 'data', 'ai', 'machine', 'learning',
            'web', 'mobile', 'cloud', 'devops', 'testing', 'deployment'
        })
        
        for topic in topic_keywords:
            if topic not in self.user_profile.common_topics:
                self.user_profile.common_topics.append(topic)
        
        # Keep only top topics
        if len(self.user_profile.common_topics) > 20:
            self.user_profile.common_topics = self.user_profile.common_topics[-15:]
    
    def _update_conversation_summary(self, turn: ConversationTurn):
        """Update conversation summary with new turn"""
        self.conversation_summary.turn_count += 1
        self.conversation_summary.last_updated = datetime.now()
        
        # Extract key topics (simple approach)
        query_topics = self._extract_topics(turn.user_query)
        response_topics = self._extract_topics(turn.council_response)
        
        all_topics = query_topics + response_topics
        for topic in all_topics:
            if topic not in self.conversation_summary.main_topics:
                self.conversation_summary.main_topics.append(topic)
        
        # Keep top topics only
        if len(self.conversation_summary.main_topics) > self.max_summary_topics:
            self.conversation_summary.main_topics = self.conversation_summary.main_topics[-self.max_summary_topics:]
        
        # Look for decisions and questions
        if any(word in turn.council_response.lower() for word in ['recommend', 'suggest', 'should', 'decision']):
            decision = turn.council_response[:200] + "..." if len(turn.council_response) > 200 else turn.council_response
            self.conversation_summary.key_decisions.append(decision)
            if len(self.conversation_summary.key_decisions) > 10:
                self.conversation_summary.key_decisions = self.conversation_summary.key_decisions[-5:]
        
        if turn.user_query.strip().endswith('?'):
            if turn.user_query not in [q.split('?')[0] + '?' for q in self.conversation_summary.unresolved_questions]:
                self.conversation_summary.unresolved_questions.append(turn.user_query)
            if len(self.conversation_summary.unresolved_questions) > 10:
                self.conversation_summary.unresolved_questions = self.conversation_summary.unresolved_questions[-5:]
    
    def _extract_topics(self, text: str) -> List[str]:
        """Simple topic extraction from text"""
        technical_terms = {
            'api', 'database', 'security', 'authentication', 'authorization', 'encryption',
            'microservices', 'architecture', 'design', 'patterns', 'algorithms', 'data',
            'machine learning', 'ai', 'neural networks', 'cloud', 'docker', 'kubernetes',
            'testing', 'deployment', 'ci/cd', 'devops', 'monitoring', 'performance',
            'scalability', 'load balancing', 'caching', 'optimization'
        }
        
        text_lower = text.lower()
        found_topics = []
        
        for term in technical_terms:
            if term in text_lower:
                found_topics.append(term)
        
        return found_topics[:5]  # Limit to 5 topics per text
    
    def _save_conversation_turn(self, turn: ConversationTurn):
        """Save a single conversation turn to disk"""
        try:
            with open(self.conversation_file, 'a', encoding='utf-8') as f:
                turn_data = {
                    'timestamp': turn.timestamp.isoformat(),
                    'user_query': turn.user_query,
                    'council_response': turn.council_response,
                    'individual_responses': turn.individual_responses,
                    'consensus_mode': turn.consensus_mode,
                    'confidence_scores': turn.confidence_scores,
                    'session_id': turn.session_id,
                    'turn_id': turn.turn_id
                }
                f.write(json.dumps(turn_data) + '\n')
        except Exception as e:
            print(f"Error saving conversation turn: {e}")
    
    def _save_user_profile(self):
        """Save user profile to disk"""
        try:
            profile_data = {
                'preferred_consensus_mode': self.user_profile.preferred_consensus_mode,
                'interaction_style': self.user_profile.interaction_style,
                'common_topics': self.user_profile.common_topics,
                'model_preferences': self.user_profile.model_preferences,
                'response_length_preference': self.user_profile.response_length_preference,
                'created_at': self.user_profile.created_at.isoformat(),
                'last_updated': self.user_profile.last_updated.isoformat()
            }
            
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile_data, f, indent=2)
        except Exception as e:
            print(f"Error saving user profile: {e}")
    
    def _save_conversation_summary(self):
        """Save conversation summary to disk"""
        try:
            summary_data = {
                'main_topics': self.conversation_summary.main_topics,
                'key_decisions': self.conversation_summary.key_decisions,
                'unresolved_questions': self.conversation_summary.unresolved_questions,
                'important_context': self.conversation_summary.important_context,
                'last_updated': self.conversation_summary.last_updated.isoformat(),
                'turn_count': self.conversation_summary.turn_count
            }
            
            with open(self.summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary_data, f, indent=2)
        except Exception as e:
            print(f"Error saving conversation summary: {e}")
    
    def _auto_summarize_old_conversations(self):
        """Automatically summarize old conversations to save memory"""
        # Keep recent turns and summarize older ones
        if len(self.conversation_history) > self.auto_summarize_threshold:
            # Move old conversations to summary
            old_turns = self.conversation_history[:-self.max_context_turns]
            recent_turns = self.conversation_history[-self.max_context_turns:]
            
            # Add key information from old turns to important context
            for turn in old_turns[-10:]:  # Last 10 old turns
                if len(turn.council_response) > 200:  # Significant responses
                    context_item = f"{turn.timestamp.strftime('%Y-%m-%d')}: {turn.user_query} -> {turn.council_response[:150]}..."
                    if context_item not in self.conversation_summary.important_context:
                        self.conversation_summary.important_context.append(context_item)
            
            # Keep only important context (limit size)
            if len(self.conversation_summary.important_context) > 20:
                self.conversation_summary.important_context = self.conversation_summary.important_context[-15:]
            
            # Keep only recent turns in active memory
            self.conversation_history = recent_turns
            print(f"Auto-summarized old conversations, keeping {len(recent_turns)} recent turns")
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the memory system"""
        return {
            'total_turns': len(self.conversation_history),
            'user_since': self.user_profile.created_at.isoformat(),
            'last_interaction': self.user_profile.last_updated.isoformat(),
            'common_topics': self.user_profile.common_topics[:10],
            'preferred_consensus': self.user_profile.preferred_consensus_mode,
            'main_topics': self.conversation_summary.main_topics,
            'summary_turn_count': self.conversation_summary.turn_count,
            'memory_files': {
                'conversation': str(self.conversation_file),
                'profile': str(self.profile_file),
                'summary': str(self.summary_file)
            }
        }
    
    def clear_memory(self, keep_profile: bool = True):
        """Clear conversation memory (optionally keeping user profile)"""
        self.conversation_history = []
        self.conversation_summary = ConversationSummary(
            main_topics=[], key_decisions=[], unresolved_questions=[],
            important_context=[], last_updated=datetime.now(), turn_count=0
        )
        
        if not keep_profile:
            self.user_profile = UserProfile()
        
        # Remove files
        if self.conversation_file.exists():
            self.conversation_file.unlink()
        if self.summary_file.exists():
            self.summary_file.unlink()
        if not keep_profile and self.profile_file.exists():
            self.profile_file.unlink()
        
        print(f"Memory cleared ({'profile kept' if keep_profile else 'all data cleared'})")

def test_memory_system():
    """Test the conversational memory system"""
    memory = ConversationalMemory(user_id="test_user")
    
    # Test adding conversations
    memory.add_conversation_turn(
        user_query="How should I design a secure API?",
        council_response="The council recommends using OAuth 2.0 with JWT tokens...",
        individual_responses={
            "strategist": "Long-term security strategy should include...",
            "analyst": "Technical analysis shows that...",
            "guardian": "Security vulnerabilities to consider..."
        },
        consensus_mode="weighted_roles",
        confidence_scores={"strategist": 0.9, "analyst": 0.8, "guardian": 0.95},
        session_id="test_session_1"
    )
    
    # Test context generation
    context = memory.get_context_for_models()
    print("Generated context:")
    print(context)
    
    # Test memory stats
    stats = memory.get_memory_stats()
    print("\nMemory stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    test_memory_system()