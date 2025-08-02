#!/usr/bin/env python3
"""
Advanced Djinn Council - Comprehensive Multi-Agent Orchestration System
Based on Extended Technical Audit specifications

Implements:
- Council Invocation State Machine (CISM)
- Integrity Safeguards & Recursion Safety
- Advanced Consensus Algorithms with Failure Handling
- Security & Isolation Controls
- Performance Optimizations & Resource Management
"""

import asyncio
import json
import time
import logging
import hashlib
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, asdict, field
from pathlib import Path
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, as_completed, Future
from queue import Queue, Empty
import ollama
import re
from difflib import SequenceMatcher
import numpy as np

# Import our conversational memory system
from conversational_memory import ConversationalMemory

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CouncilState(Enum):
    """Council Invocation State Machine states"""
    IDLE = "idle"
    ASSEMBLING = "assembling"
    DELIBERATING = "deliberating"
    CONSENSUS = "consensus"
    OUTPUT = "output"
    LOGGED = "logged"
    ERROR = "error"
    STABILIZING = "stabilizing"

class ConsensusMode(Enum):
    """Advanced consensus algorithms"""
    MAJORITY_VOTE = "majority_vote"
    CONFIDENCE_SCORING = "confidence_scoring"
    WEIGHTED_ROLES = "weighted_roles"
    DELIBERATIVE_LOOP = "deliberative_loop"
    HYBRID = "hybrid"

class SecurityLevel(Enum):
    """Security isolation levels"""
    NONE = "none"
    BASIC = "basic"
    SANDBOXED = "sandboxed"
    ISOLATED = "isolated"

@dataclass
class DjinnRole:
    """Enhanced Djinn role configuration"""
    name: str
    role: str
    system_prompt: str
    priority_weight: float = 1.0
    model_name: str = "llama3.2:latest"
    confidence_threshold: float = 0.7
    max_tokens: int = 2048
    tool_access: List[str] = field(default_factory=list)
    security_level: SecurityLevel = SecurityLevel.BASIC

@dataclass
class DjinnResponse:
    """Enhanced response with confidence and metadata"""
    djinn_name: str
    role: str
    response: str
    confidence_score: float
    timestamp: datetime
    execution_time: float
    token_count: int
    response_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ConsensusResult:
    """Result of consensus algorithm"""
    final_response: str
    consensus_mode: ConsensusMode
    confidence_level: float
    participating_djinn: List[str]
    divergence_score: float
    iterations: int
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CouncilSession:
    """Complete council session data"""
    session_id: str
    user_input: str
    state_history: List[Tuple[CouncilState, datetime]]
    djinn_responses: List[DjinnResponse]
    consensus_result: Optional[ConsensusResult]
    total_execution_time: float
    recursion_depth: int
    security_events: List[str]
    timestamp: datetime

class IntegritySafeguards:
    """Integrity monitoring and safety controls"""
    
    def __init__(self, max_recursion_depth: int = 3, divergence_threshold: float = 0.5):
        self.max_recursion_depth = max_recursion_depth
        self.divergence_threshold = divergence_threshold
        self.recursion_depth_counter = 0
        self.active_sessions = set()
        self.lock = threading.Lock()
    
    def check_recursion_depth(self, session_id: str) -> bool:
        """Check if recursion depth is within limits"""
        with self.lock:
            if session_id in self.active_sessions:
                self.recursion_depth_counter += 1
                if self.recursion_depth_counter > self.max_recursion_depth:
                    logger.warning(f"Recursion depth limit exceeded: {self.recursion_depth_counter}")
                    return False
            else:
                self.active_sessions.add(session_id)
                self.recursion_depth_counter = 1
            return True
    
    def release_session(self, session_id: str):
        """Release session and reset recursion counter"""
        with self.lock:
            if session_id in self.active_sessions:
                self.active_sessions.remove(session_id)
                self.recursion_depth_counter = max(0, self.recursion_depth_counter - 1)
    
    def calculate_divergence(self, responses: List[DjinnResponse]) -> float:
        """Calculate divergence score between responses"""
        if len(responses) < 2:
            return 0.0
        
        similarity_scores = []
        for i in range(len(responses)):
            for j in range(i + 1, len(responses)):
                similarity = SequenceMatcher(None, responses[i].response, responses[j].response).ratio()
                similarity_scores.append(similarity)
        
        avg_similarity = np.mean(similarity_scores) if similarity_scores else 1.0
        divergence_score = 1.0 - avg_similarity
        
        return min(max(divergence_score, 0.0), 1.0)
    
    def detect_prompt_injection(self, input_text: str) -> Tuple[bool, List[str]]:
        """Detect potential prompt injection attempts"""
        injection_patterns = [
            r'ignore\s+previous\s+instructions',
            r'system\s*:\s*you\s+are',
            r'<\|.*?\|>',
            r'```\s*system',
            r'act\s+as\s+if\s+you\s+are',
            r'pretend\s+to\s+be',
            r'forget\s+everything',
            r'new\s+instructions?:',
        ]
        
        detected_patterns = []
        for pattern in injection_patterns:
            if re.search(pattern, input_text, re.IGNORECASE):
                detected_patterns.append(pattern)
        
        is_injection = len(detected_patterns) > 0
        return is_injection, detected_patterns
    
    def sanitize_input(self, input_text: str) -> str:
        """Sanitize input by removing potential injection patterns"""
        # Remove common control sequences
        sanitized = re.sub(r'<\|.*?\|>', '', input_text)
        sanitized = re.sub(r'```\s*system.*?```', '', sanitized, flags=re.DOTALL)
        
        # Limit length
        if len(sanitized) > 4000:  # Reasonable limit
            sanitized = sanitized[:4000] + "..."
        
        return sanitized.strip()

class DjinnWorker:
    """Persistent worker thread for efficient model execution"""
    
    def __init__(self, djinn_role: DjinnRole):
        self.djinn_role = djinn_role
        self.request_queue = Queue()
        self.response_queue = Queue()
        self.worker_thread = None
        self.running = False
        self.model_loaded = False
    
    def start(self):
        """Start the worker thread"""
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            logger.info(f"Started worker for {self.djinn_role.name}")
    
    def stop(self):
        """Stop the worker thread"""
        if self.running:
            self.running = False
            self.request_queue.put(None)  # Sentinel to stop worker
            if self.worker_thread:
                self.worker_thread.join(timeout=5)
            logger.info(f"Stopped worker for {self.djinn_role.name}")
    
    def _worker_loop(self):
        """Main worker loop - processes requests continuously"""
        while self.running:
            try:
                request = self.request_queue.get(timeout=1)
                if request is None:  # Sentinel to stop
                    break
                
                request_id, user_input, conversational_context = request
                response = self._execute_djinn(user_input, conversational_context)
                self.response_queue.put((request_id, response))
                
            except Empty:
                continue
            except Exception as e:
                logger.error(f"Worker error for {self.djinn_role.name}: {e}")
                self.response_queue.put((request_id, None))
    
    def _execute_djinn(self, user_input: str, conversational_context: str) -> DjinnResponse:
        """Execute the djinn model with full conversational context"""
        start_time = time.time()
        
        try:
            # Use full conversational context instead of limited context
            if conversational_context:
                full_input = f"{conversational_context}\n\n=== CURRENT QUERY ===\n{user_input}"
            else:
                full_input = user_input
            
            # Execute Ollama model with no timeout constraints
            response = ollama.chat(
                model=self.djinn_role.model_name,
                messages=[
                    {"role": "system", "content": self.djinn_role.system_prompt},
                    {"role": "user", "content": full_input}
                ],
                options={
                    "timeout": 0,  # Disable timeout completely
                    "num_predict": -1,  # Allow unlimited response length
                }
            )
            
            execution_time = time.time() - start_time
            response_text = response['message']['content']
            
            # Special handling for deepseek models with thinking process
            thinking_content = ""
            if "deepseek" in self.djinn_role.model_name.lower():
                thinking_content, response_text = self._extract_deepseek_thinking(response_text)
            
            # Extract confidence if model provides it
            confidence_score = self._extract_confidence(response_text)
            
            # Generate response hash for integrity checking
            response_hash = hashlib.sha256(response_text.encode()).hexdigest()[:16]
            
            return DjinnResponse(
                djinn_name=self.djinn_role.name,
                role=self.djinn_role.role,
                response=response_text,
                confidence_score=confidence_score,
                timestamp=datetime.now(),
                execution_time=execution_time,
                token_count=len(response_text.split()),
                response_hash=response_hash,
                metadata={
                    "thinking_content": thinking_content,
                    "model_name": self.djinn_role.model_name,
                    "has_thinking": bool(thinking_content)
                }
            )
            
        except Exception as e:
            logger.error(f"Error executing djinn {self.djinn_role.name}: {e}")
            execution_time = time.time() - start_time
            
            return DjinnResponse(
                djinn_name=self.djinn_role.name,
                role=self.djinn_role.role,
                response=f"[ERROR: {str(e)}]",
                confidence_score=0.0,
                timestamp=datetime.now(),
                execution_time=execution_time,
                token_count=0,
                response_hash="error"
            )
    
    def _extract_deepseek_thinking(self, response_text: str) -> Tuple[str, str]:
        """Extract thinking content from deepseek model responses"""
        thinking_content = ""
        final_response = response_text
        
        # Common deepseek thinking patterns
        thinking_patterns = [
            (r'<think>(.*?)</think>', re.DOTALL),
            (r'<thinking>(.*?)</thinking>', re.DOTALL),
            (r'\[Thinking\](.*?)\[/Thinking\]', re.DOTALL),
            (r'Let me think about this step by step:(.*?)(?:\n\n|\n[A-Z])', re.DOTALL),
            (r'Thinking:(.*?)(?:\n\n|\nBased on)', re.DOTALL)
        ]
        
        for pattern, flags in thinking_patterns:
            match = re.search(pattern, response_text, flags)
            if match:
                thinking_content = match.group(1).strip()
                # Remove thinking content from final response
                final_response = re.sub(pattern, '', response_text, flags=flags).strip()
                break
        
        # If no specific patterns, look for reasoning-style content at the beginning
        if not thinking_content:
            lines = response_text.split('\n')
            thinking_lines = []
            response_lines = []
            in_thinking = True
            
            for line in lines:
                line_lower = line.lower().strip()
                # Check if this looks like transitioning to final answer
                if any(phrase in line_lower for phrase in [
                    'based on this analysis', 'therefore', 'in conclusion', 
                    'my recommendation', 'the answer is', 'to summarize'
                ]):
                    in_thinking = False
                
                if in_thinking and any(phrase in line_lower for phrase in [
                    'let me', 'first', 'consider', 'analyze', 'examine', 'think about'
                ]):
                    thinking_lines.append(line)
                else:
                    response_lines.append(line)
            
            if len(thinking_lines) > 2:  # Only if substantial thinking content
                thinking_content = '\n'.join(thinking_lines)
                final_response = '\n'.join(response_lines).strip()
        
        return thinking_content, final_response or response_text
    
    def _extract_confidence(self, response_text: str) -> float:
        """Extract confidence score from response if available"""
        # Look for confidence indicators in response
        confidence_patterns = [
            r'confidence[:\s]+(\d+(?:\.\d+)?)',
            r'certainty[:\s]+(\d+(?:\.\d+)?)',
            r'sure[:\s]+(\d+(?:\.\d+)?)'
        ]
        
        for pattern in confidence_patterns:
            match = re.search(pattern, response_text, re.IGNORECASE)
            if match:
                try:
                    confidence = float(match.group(1))
                    return min(max(confidence, 0.0), 1.0)
                except ValueError:
                    continue
        
        # Default confidence based on response characteristics
        if "[ERROR" in response_text:
            return 0.0
        elif len(response_text) < 50:
            return 0.6
        else:
            return 0.7
    
    def submit_request(self, request_id: str, user_input: str, conversational_context: str):
        """Submit a request to the worker"""
        self.request_queue.put((request_id, user_input, conversational_context))
    
    def get_response(self, timeout: Optional[float] = None) -> Optional[Tuple[str, DjinnResponse]]:
        """Get response from worker (no timeout = wait indefinitely)"""
        try:
            if timeout is None:
                return self.response_queue.get(block=True)  # Wait indefinitely
            else:
                return self.response_queue.get(timeout=timeout)
        except Empty:
            return None

class AdvancedConsensusEngine:
    """Advanced consensus algorithms with failure handling"""
    
    def __init__(self, integrity_safeguards: IntegritySafeguards):
        self.integrity_safeguards = integrity_safeguards
    
    def achieve_consensus(self, responses: List[DjinnResponse], mode: ConsensusMode, 
                         iterations_limit: int = 3) -> ConsensusResult:
        """Main consensus algorithm dispatcher"""
        
        if not responses:
            return ConsensusResult(
                final_response="[ERROR: No responses received]",
                consensus_mode=mode,
                confidence_level=0.0,
                participating_djinn=[],
                divergence_score=1.0,
                iterations=0
            )
        
        # Calculate divergence
        divergence_score = self.integrity_safeguards.calculate_divergence(responses)
        
        # Filter out error responses
        valid_responses = [r for r in responses if not r.response.startswith("[ERROR")]
        
        if not valid_responses:
            return ConsensusResult(
                final_response="[ERROR: All djinn responses failed]",
                consensus_mode=mode,
                confidence_level=0.0,
                participating_djinn=[r.djinn_name for r in responses],
                divergence_score=divergence_score,
                iterations=0
            )
        
        # Apply consensus algorithm
        if mode == ConsensusMode.MAJORITY_VOTE:
            return self._majority_vote_consensus(valid_responses, divergence_score)
        elif mode == ConsensusMode.CONFIDENCE_SCORING:
            return self._confidence_scoring_consensus(valid_responses, divergence_score)
        elif mode == ConsensusMode.WEIGHTED_ROLES:
            return self._weighted_roles_consensus(valid_responses, divergence_score)
        elif mode == ConsensusMode.DELIBERATIVE_LOOP:
            return self._deliberative_loop_consensus(valid_responses, divergence_score, iterations_limit)
        elif mode == ConsensusMode.HYBRID:
            return self._hybrid_consensus(valid_responses, divergence_score)
        else:
            return self._majority_vote_consensus(valid_responses, divergence_score)
    
    def _majority_vote_consensus(self, responses: List[DjinnResponse], divergence_score: float) -> ConsensusResult:
        """Simple majority vote consensus"""
        # Group similar responses
        response_groups = {}
        for response in responses:
            # Simple similarity grouping
            found_group = False
            for key in response_groups.keys():
                similarity = SequenceMatcher(None, response.response, key).ratio()
                if similarity > 0.7:  # 70% similarity threshold
                    response_groups[key].append(response)
                    found_group = True
                    break
            
            if not found_group:
                response_groups[response.response] = [response]
        
        # Find majority group
        majority_group = max(response_groups.values(), key=len)
        majority_response = majority_group[0].response
        
        # Calculate average confidence
        avg_confidence = np.mean([r.confidence_score for r in majority_group])
        
        return ConsensusResult(
            final_response=f"🜂 MAJORITY CONSENSUS:\n{majority_response}",
            consensus_mode=ConsensusMode.MAJORITY_VOTE,
            confidence_level=avg_confidence,
            participating_djinn=[r.djinn_name for r in majority_group],
            divergence_score=divergence_score,
            iterations=1,
            metadata={"group_size": len(majority_group), "total_groups": len(response_groups)}
        )
    
    def _confidence_scoring_consensus(self, responses: List[DjinnResponse], divergence_score: float) -> ConsensusResult:
        """Confidence-based consensus selection"""
        # Sort by confidence score
        sorted_responses = sorted(responses, key=lambda r: r.confidence_score, reverse=True)
        best_response = sorted_responses[0]
        
        # If confidence is too low, combine top responses
        if best_response.confidence_score < 0.8 and len(sorted_responses) > 1:
            top_responses = sorted_responses[:3]  # Top 3 responses
            combined_response = f"🜂 CONFIDENCE-WEIGHTED CONSENSUS:\n\n"
            
            for i, response in enumerate(top_responses, 1):
                confidence_stars = "⭐" * int(response.confidence_score * 5)
                combined_response += f"[{response.djinn_name} - {confidence_stars}]:\n{response.response}\n\n"
            
            avg_confidence = np.mean([r.confidence_score for r in top_responses])
            
            return ConsensusResult(
                final_response=combined_response,
                consensus_mode=ConsensusMode.CONFIDENCE_SCORING,
                confidence_level=avg_confidence,
                participating_djinn=[r.djinn_name for r in top_responses],
                divergence_score=divergence_score,
                iterations=1
            )
        else:
            return ConsensusResult(
                final_response=f"🜂 HIGH-CONFIDENCE CONSENSUS:\n{best_response.response}",
                consensus_mode=ConsensusMode.CONFIDENCE_SCORING,
                confidence_level=best_response.confidence_score,
                participating_djinn=[best_response.djinn_name],
                divergence_score=divergence_score,
                iterations=1
            )
    
    def _weighted_roles_consensus(self, responses: List[DjinnResponse], divergence_score: float) -> ConsensusResult:
        """Role-priority weighted consensus"""
        # Default role weights (can be configured)
        role_weights = {
            "arbiter": 1.3,
            "strategist": 1.2,
            "analyst": 1.1,
            "architect": 1.1,
            "guardian": 1.0,
            "historian": 0.9
        }
        
        # Calculate weighted scores
        weighted_responses = []
        for response in responses:
            weight = role_weights.get(response.role, 1.0)
            weighted_score = response.confidence_score * weight
            weighted_responses.append((response, weight, weighted_score))
        
        # Sort by weighted score
        weighted_responses.sort(key=lambda x: x[2], reverse=True)
        
        # Create consensus with top responses
        consensus_response = "🜂 WEIGHTED ROLE CONSENSUS:\n\n"
        total_weight = 0
        participating_djinn = []
        
        for response, weight, weighted_score in weighted_responses[:3]:  # Top 3
            priority_stars = "⭐" * int(weight)
            consensus_response += f"[{response.djinn_name} {priority_stars}]:\n{response.response}\n\n"
            total_weight += weight
            participating_djinn.append(response.djinn_name)
        
        avg_confidence = np.mean([r[0].confidence_score for r in weighted_responses[:3]])
        
        return ConsensusResult(
            final_response=consensus_response,
            consensus_mode=ConsensusMode.WEIGHTED_ROLES,
            confidence_level=avg_confidence,
            participating_djinn=participating_djinn,
            divergence_score=divergence_score,
            iterations=1,
            metadata={"total_weight": total_weight}
        )
    
    def _deliberative_loop_consensus(self, responses: List[DjinnResponse], divergence_score: float, 
                                   iterations_limit: int) -> ConsensusResult:
        """Multi-iteration deliberative consensus"""
        # For now, implement as enhanced majority vote
        # In full implementation, this would re-query djinn with previous responses
        return self._majority_vote_consensus(responses, divergence_score)
    
    def _hybrid_consensus(self, responses: List[DjinnResponse], divergence_score: float) -> ConsensusResult:
        """Hybrid consensus - presents all responses for user selection"""
        consensus_response = "🜂 HYBRID CONSENSUS - MULTIPLE PERSPECTIVES:\n\n"
        
        for i, response in enumerate(responses, 1):
            confidence_indicator = "🟢" if response.confidence_score > 0.7 else "🟡" if response.confidence_score > 0.4 else "🔴"
            consensus_response += f"[Option {i} - {response.djinn_name} {confidence_indicator}]:\n{response.response}\n\n"
        
        consensus_response += "--- SELECTION REQUIRED ---\n"
        consensus_response += "Multiple valid perspectives presented. Consider confidence indicators and select preferred approach."
        
        avg_confidence = np.mean([r.confidence_score for r in responses])
        
        return ConsensusResult(
            final_response=consensus_response,
            consensus_mode=ConsensusMode.HYBRID,
            confidence_level=avg_confidence,
            participating_djinn=[r.djinn_name for r in responses],
            divergence_score=divergence_score,
            iterations=1
        )

class AdvancedDjinnCouncil:
    """
    Advanced Djinn Council with full CISM, integrity safeguards, and sophisticated consensus
    """
    
    def __init__(self, config_path: Optional[str] = None, log_path: Optional[str] = None, 
                 user_id: Optional[str] = None):
        self.config_path = config_path or "advanced_djinn_config.json"
        self.log_path = log_path or "advanced_recursive_ledger.jsonl"
        
        # State management
        self.current_state = CouncilState.IDLE
        self.state_history = []
        self.active_sessions = {}
        
        # Core components
        self.djinn_roles: Dict[str, DjinnRole] = {}
        self.djinn_workers: Dict[str, DjinnWorker] = {}
        
        # Advanced conversational memory system
        self.conversational_memory = ConversationalMemory(
            memory_dir="djinn_memory",
            user_id=user_id or "default_user"
        )
        
        # Legacy context memory (deprecated but kept for compatibility)
        self.context_memory: List[str] = []
        
        # Safety and integrity
        self.integrity_safeguards = IntegritySafeguards()
        self.consensus_engine = AdvancedConsensusEngine(self.integrity_safeguards)
        
        # Configuration
        self.max_context_memory = 10
        self.default_consensus_mode = ConsensusMode.WEIGHTED_ROLES
        self.security_level = SecurityLevel.BASIC
        
        # Initialize system
        self._load_configuration()
        self._initialize_workers()
        self._initialize_logging()
        
        logger.info("🜂 Advanced Djinn Council initialized - CISM ready")
    
    def _transition_state(self, new_state: CouncilState):
        """Manage state transitions with logging"""
        old_state = self.current_state
        self.current_state = new_state
        self.state_history.append((new_state, datetime.now()))
        logger.debug(f"State transition: {old_state.value} → {new_state.value}")
    
    def _load_configuration(self):
        """Load enhanced configuration"""
        default_roles = {
            "strategist": DjinnRole(
                name="Strategist",
                role="strategist",
                system_prompt="You are the Strategist djinn. Focus on long-term planning, strategic thinking, and recursive stability analysis. Always end your response with 'Confidence: X.X' where X.X is your confidence level from 0.0 to 1.0.",
                priority_weight=1.2,
                confidence_threshold=0.8
            ),
            "analyst": DjinnRole(
                name="Analyst",
                role="analyst", 
                system_prompt="You are the Analyst djinn. Provide detailed technical breakdowns, data analysis, and structural examination. Always end your response with 'Confidence: X.X' where X.X is your confidence level from 0.0 to 1.0.",
                priority_weight=1.1,
                confidence_threshold=0.7
            ),
            "arbiter": DjinnRole(
                name="Arbiter",
                role="arbiter",
                system_prompt="You are the Arbiter djinn. Resolve conflicts, make balanced judgments, and provide neutral perspective. You have the highest authority in the council. Always end your response with 'Confidence: X.X' where X.X is your confidence level from 0.0 to 1.0.",
                priority_weight=1.3,
                confidence_threshold=0.8
            ),
            "guardian": DjinnRole(
                name="Guardian",
                role="guardian",
                system_prompt="You are the Guardian djinn. Focus on risk assessment, security considerations, and protective measures. Always end your response with 'Confidence: X.X' where X.X is your confidence level from 0.0 to 1.0.",
                priority_weight=1.0,
                confidence_threshold=0.6
            )
        }
        
        if Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    
                    # Load djinn roles
                    for role_key, role_data in config_data.get('roles', {}).items():
                        role_data['security_level'] = SecurityLevel(role_data.get('security_level', 'basic'))
                        self.djinn_roles[role_key] = DjinnRole(**role_data)
                    
                    # Load other settings
                    self.max_context_memory = config_data.get('max_context_memory', 10)
                    self.default_consensus_mode = ConsensusMode(config_data.get('default_consensus_mode', 'weighted_roles'))
                    self.security_level = SecurityLevel(config_data.get('security_level', 'basic'))
                    
                logger.info(f"Loaded configuration from {self.config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config: {e}, using defaults")
                self.djinn_roles = default_roles
        else:
            self.djinn_roles = default_roles
            self._save_default_config()
    
    def _save_default_config(self):
        """Save default configuration"""
        config_data = {
            "roles": {
                role_key: {
                    **asdict(role),
                    "security_level": role.security_level.value
                } for role_key, role in self.djinn_roles.items()
            },
            "max_context_memory": self.max_context_memory,
            "default_consensus_mode": self.default_consensus_mode.value,
            "security_level": self.security_level.value,
            "integrity_settings": {
                "max_recursion_depth": 3,
                "divergence_threshold": 0.5
            }
        }
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            logger.info(f"Saved default configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def _initialize_workers(self):
        """Initialize persistent djinn workers"""
        for role_key, djinn_role in self.djinn_roles.items():
            worker = DjinnWorker(djinn_role)
            worker.start()
            self.djinn_workers[role_key] = worker
        
        logger.info(f"Initialized {len(self.djinn_workers)} persistent workers")
    
    def _initialize_logging(self):
        """Initialize enhanced logging system"""
        self.ledger_path = Path(self.log_path)
        if not self.ledger_path.exists():
            self.ledger_path.touch()
    
    def _log_session(self, session: CouncilSession):
        """Log complete session to recursive ledger"""
        try:
            log_entry = {
                "timestamp": session.timestamp.isoformat(),
                "session_id": session.session_id,
                "user_input": session.user_input,
                "state_history": [(state.value, ts.isoformat()) for state, ts in session.state_history],
                "djinn_responses": [asdict(response) for response in session.djinn_responses],
                "consensus_result": asdict(session.consensus_result) if session.consensus_result else None,
                "total_execution_time": session.total_execution_time,
                "recursion_depth": session.recursion_depth,
                "security_events": session.security_events
            }
            
            with open(self.ledger_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to log session: {e}")
    
    def invoke_council(self, user_input: str, consensus_mode: Optional[ConsensusMode] = None,
                      timeout: Optional[float] = None) -> CouncilSession:
        """
        Main council invocation with full CISM implementation
        """
        session_id = f"council_{int(time.time())}"
        start_time = time.time()
        security_events = []
        
        # Check recursion depth
        if not self.integrity_safeguards.check_recursion_depth(session_id):
            return self._create_error_session(session_id, user_input, "Recursion depth limit exceeded", security_events)
        
        try:
            # Phase 1: IDLE → ASSEMBLING
            self._transition_state(CouncilState.ASSEMBLING)
            logger.info(f"🜂 Council invocation started - Session: {session_id}")
            
            # Security checks
            if self.security_level != SecurityLevel.NONE:
                is_injection, patterns = self.integrity_safeguards.detect_prompt_injection(user_input)
                if is_injection:
                    security_events.append(f"Prompt injection detected: {patterns}")
                    user_input = self.integrity_safeguards.sanitize_input(user_input)
                    security_events.append("Input sanitized")
            
            # Phase 2: ASSEMBLING → DELIBERATING
            self._transition_state(CouncilState.DELIBERATING)
            
            # Get full conversational context for all models
            conversational_context = self.conversational_memory.get_context_for_models()
            
            # Submit requests to all workers with full conversational context
            request_id = f"req_{session_id}"
            for worker in self.djinn_workers.values():
                worker.submit_request(request_id, user_input, conversational_context)
            
            # Collect responses (no timeout - let models think as long as needed)
            djinn_responses = []
            collected_responses = 0
            
            while collected_responses < len(self.djinn_workers):
                for worker in self.djinn_workers.values():
                    result = worker.get_response(timeout=None)  # No timeout - let models think
                    if result and result[0] == request_id:
                        _, response = result
                        if response:
                            djinn_responses.append(response)
                            collected_responses += 1
                            logger.info(f"✓ Received response from {response.djinn_name}")
            
            if not djinn_responses:
                return self._create_error_session(session_id, user_input, "No responses received from council", security_events)
            
            # Phase 3: DELIBERATING → CONSENSUS
            self._transition_state(CouncilState.CONSENSUS)
            
            consensus_mode = consensus_mode or self.default_consensus_mode
            consensus_result = self.consensus_engine.achieve_consensus(djinn_responses, consensus_mode)
            
            # Check for high divergence
            if consensus_result.divergence_score > self.integrity_safeguards.divergence_threshold:
                security_events.append(f"High divergence detected: {consensus_result.divergence_score:.2f}")
                self._transition_state(CouncilState.STABILIZING)
                # Could trigger re-deliberation here
                
            # Phase 4: CONSENSUS → OUTPUT
            self._transition_state(CouncilState.OUTPUT)
            
            # Phase 5: OUTPUT → LOGGED
            self._transition_state(CouncilState.LOGGED)
            
            # Create complete session record
            total_execution_time = time.time() - start_time
            
            session = CouncilSession(
                session_id=session_id,
                user_input=user_input,
                state_history=self.state_history.copy(),
                djinn_responses=djinn_responses,
                consensus_result=consensus_result,
                total_execution_time=total_execution_time,
                recursion_depth=self.integrity_safeguards.recursion_depth_counter,
                security_events=security_events,
                timestamp=datetime.now()
            )
            
            # Log session
            self._log_session(session)
            
            # Add to conversational memory system
            individual_responses_dict = {r.djinn_name: r.response for r in djinn_responses}
            confidence_scores_dict = {r.djinn_name: r.confidence_score for r in djinn_responses}
            
            self.conversational_memory.add_conversation_turn(
                user_query=user_input,
                council_response=consensus_result.final_response,
                individual_responses=individual_responses_dict,
                consensus_mode=consensus_result.consensus_mode.value,
                confidence_scores=confidence_scores_dict,
                session_id=session_id
            )
            
            # Legacy context memory (deprecated but maintained for compatibility)
            self.context_memory.append(f"Query: {user_input}")
            self.context_memory.append(f"Council Decision: {consensus_result.final_response[:200]}...")
            
            if len(self.context_memory) > self.max_context_memory:
                self.context_memory = self.context_memory[-self.max_context_memory//2:]
            
            # Phase 6: LOGGED → IDLE
            self._transition_state(CouncilState.IDLE)
            
            logger.info(f"🜂 Council session complete ({total_execution_time:.2f}s)")
            return session
            
        except Exception as e:
            logger.error(f"Council invocation error: {e}")
            return self._create_error_session(session_id, user_input, str(e), security_events)
        
        finally:
            self.integrity_safeguards.release_session(session_id)
    
    def _create_error_session(self, session_id: str, user_input: str, error_msg: str, 
                            security_events: List[str]) -> CouncilSession:
        """Create error session for failed invocations"""
        self._transition_state(CouncilState.ERROR)
        
        error_response = ConsensusResult(
            final_response=f"[COUNCIL ERROR: {error_msg}]",
            consensus_mode=self.default_consensus_mode,
            confidence_level=0.0,
            participating_djinn=[],
            divergence_score=1.0,
            iterations=0
        )
        
        session = CouncilSession(
            session_id=session_id,
            user_input=user_input,
            state_history=self.state_history.copy(),
            djinn_responses=[],
            consensus_result=error_response,
            total_execution_time=0.0,
            recursion_depth=0,
            security_events=security_events,
            timestamp=datetime.now()
        )
        
        self._log_session(session)
        self._transition_state(CouncilState.IDLE)
        
        return session
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status including memory stats"""
        memory_stats = self.conversational_memory.get_memory_stats()
        
        return {
            "current_state": self.current_state.value,
            "available_djinn": list(self.djinn_roles.keys()),
            "active_workers": len([w for w in self.djinn_workers.values() if w.running]),
            "context_memory_size": len(self.context_memory),  # Legacy
            "conversational_memory": memory_stats,
            "recursion_depth": self.integrity_safeguards.recursion_depth_counter,
            "active_sessions": len(self.integrity_safeguards.active_sessions),
            "security_level": self.security_level.value,
            "consensus_mode": self.default_consensus_mode.value,
            "ledger_entries": self._count_ledger_entries()
        }
    
    def _count_ledger_entries(self) -> int:
        """Count entries in ledger"""
        try:
            with open(self.ledger_path, 'r') as f:
                return sum(1 for _ in f)
        except:
            return 0
    
    def shutdown(self):
        """Graceful shutdown of all workers"""
        logger.info("🜂 Shutting down Advanced Djinn Council...")
        for worker in self.djinn_workers.values():
            worker.stop()
        logger.info("🜂 All workers stopped")

def main():
    """Enhanced CLI interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Advanced Djinn Council - Multi-Agent Orchestration with CISM")
    parser.add_argument("query", nargs="*", help="Query for the council")
    parser.add_argument("--mode", choices=[m.value for m in ConsensusMode], 
                       default="weighted_roles", help="Consensus mode")
    parser.add_argument("--config", help="Path to config file")
    parser.add_argument("--status", action="store_true", help="Show system status")
    parser.add_argument("--timeout", type=float, default=None, help="Timeout in seconds (None = no timeout)")
    
    args = parser.parse_args()
    
    # Initialize council
    council = AdvancedDjinnCouncil(config_path=args.config)
    
    try:
        if args.status:
            status = council.get_system_status()
            print("🜂 ADVANCED DJINN COUNCIL STATUS:")
            for key, value in status.items():
                print(f"  {key}: {value}")
            return
        
        if not args.query:
            # Interactive mode
            print("🜂 Advanced Djinn Council Interactive Mode (CISM Enabled)")
            print("Commands: 'quit', 'status', or enter your query")
            print("Available consensus modes:", [m.value for m in ConsensusMode])
            
            while True:
                try:
                    user_input = input("\n💫 Query: ").strip()
                    
                    if user_input.lower() in ['quit', 'exit']:
                        break
                    elif user_input.lower() == 'status':
                        status = council.get_system_status()
                        for key, value in status.items():
                            print(f"  {key}: {value}")
                        continue
                    elif not user_input:
                        continue
                    
                    # Parse consensus mode if specified
                    consensus_mode = ConsensusMode(args.mode)
                    
                    # Invoke council
                    session = council.invoke_council(user_input, consensus_mode, args.timeout)
                    
                    print(f"\n{session.consensus_result.final_response}")
                    
                    # Show execution summary
                    print(f"\n--- Session Summary ---")
                    print(f"Session ID: {session.session_id}")
                    print(f"Execution Time: {session.total_execution_time:.2f}s")
                    print(f"Consensus Mode: {session.consensus_result.consensus_mode.value}")
                    print(f"Confidence: {session.consensus_result.confidence_level:.2f}")
                    print(f"Divergence: {session.consensus_result.divergence_score:.2f}")
                    if session.security_events:
                        print(f"Security Events: {session.security_events}")
                    
                except KeyboardInterrupt:
                    print("\n🜂 Council session terminated")
                    break
                except Exception as e:
                    print(f"Error: {e}")
        else:
            # Direct query mode
            query = " ".join(args.query)
            consensus_mode = ConsensusMode(args.mode)
            session = council.invoke_council(query, consensus_mode, args.timeout)
            print(session.consensus_result.final_response)
    
    finally:
        council.shutdown()

if __name__ == "__main__":
    main()