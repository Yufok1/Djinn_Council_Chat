#!/usr/bin/env python3
"""
Djinn Council - Multi-Agent Ollama Orchestration System
Based on the Djinn Council Technical Orchestration Audit Report

Implements:
- Phase 1: Invocation Recognition and Binding
- Phase 2: Council Assembly and Parallel Model Spawning  
- Phase 3: Deliberation Cycle
- Phase 4: Response Generation and Logging
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from pathlib import Path
import ollama

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DjinnRole:
    """Configuration for a single Djinn entity"""
    name: str
    role: str
    system_prompt: str
    priority_weight: float = 1.0
    model_name: str = "llama3.2:latest"

@dataclass
class CouncilResponse:
    """Response from a single Djinn"""
    djinn_name: str
    role: str
    response: str
    timestamp: datetime
    execution_time: float
    token_count: int = 0

@dataclass
class CouncilDeliberation:
    """Complete council deliberation results"""
    session_id: str
    user_input: str
    djinn_responses: List[CouncilResponse]
    consensus_result: str
    deliberation_mode: str
    total_execution_time: float
    timestamp: datetime

class DjinnCouncil:
    """
    Main Djinn Council orchestration system
    Implements multi-agent recursive model orchestration for advisory, arbitration, and parallel computation
    """
    
    def __init__(self, config_path: Optional[str] = None, log_path: Optional[str] = None):
        self.config_path = config_path or "djinn_council_config.json"
        self.log_path = log_path or "recursive_ledger.jsonl"
        
        # Core components from the specification
        self.djinn_roles: Dict[str, DjinnRole] = {}
        self.context_memory: List[str] = []
        self.violation_threshold = 0.8
        self.council_active = False
        
        # Initialize components
        self._load_djinn_manifest()
        self._initialize_logging()
        
        logger.info("🜂 Djinn Council initialized - Ready for invocation")
    
    def _load_djinn_manifest(self):
        """Load Djinn Manifest Config (DMC) - defines roles and behaviors"""
        default_roles = {
            "strategist": DjinnRole(
                name="Strategist",
                role="strategist", 
                system_prompt="You are the Strategist djinn. Focus on long-term planning, strategic thinking, and recursive stability analysis. Provide strategic insights and recommendations that consider both immediate and long-term implications.",
                priority_weight=1.2
            ),
            "analyst": DjinnRole(
                name="Analyst",
                role="analyst",
                system_prompt="You are the Analyst djinn. Provide detailed technical breakdowns, data analysis, and structural examination. Focus on precise, factual analysis with supporting evidence and technical accuracy.",
                priority_weight=1.1
            ),
            "arbiter": DjinnRole(
                name="Arbiter", 
                role="arbiter",
                system_prompt="You are the Arbiter djinn. Resolve conflicts, make balanced judgments, and provide neutral perspective. Focus on fairness, conflict resolution, and finding consensus among different viewpoints.",
                priority_weight=1.3
            ),
            "historian": DjinnRole(
                name="Historian",
                role="historian",
                system_prompt="You are the Historian djinn. Provide context from past patterns, precedents, and learned experiences. Focus on lessons from history and contextual knowledge that informs current decisions.",
                priority_weight=0.9
            ),
            "architect": DjinnRole(
                name="Architect",
                role="architect", 
                system_prompt="You are the Architect djinn. Focus on system design, structural planning, and implementation frameworks. Provide blueprints, architectural decisions, and systematic approaches to complex problems.",
                priority_weight=1.1
            )
        }
        
        # Try to load custom config, fall back to defaults
        if Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r') as f:
                    config_data = json.load(f)
                    # Convert config data to DjinnRole objects
                    for role_key, role_data in config_data.get('djinn_roles', {}).items():
                        self.djinn_roles[role_key] = DjinnRole(**role_data)
                logger.info(f"Loaded custom djinn configuration from {self.config_path}")
            except Exception as e:
                logger.warning(f"Failed to load config from {self.config_path}: {e}")
                self.djinn_roles = default_roles
        else:
            self.djinn_roles = default_roles
            self._save_default_config()
    
    def _save_default_config(self):
        """Save default configuration for future customization"""
        config_data = {
            "djinn_roles": {role_key: asdict(role) for role_key, role in self.djinn_roles.items()},
            "deliberation_modes": ["unanimous", "majority", "hybrid"],
            "violation_threshold": self.violation_threshold
        }
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config_data, f, indent=2)
            logger.info(f"Saved default configuration to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def _initialize_logging(self):
        """Initialize Recursive Ledger (RL) for audit and rollback"""
        self.ledger_path = Path(self.log_path)
        if not self.ledger_path.exists():
            self.ledger_path.touch()
            logger.info(f"Created recursive ledger at {self.log_path}")
    
    def _log_deliberation(self, deliberation: CouncilDeliberation):
        """Log complete deliberation to Recursive Ledger"""
        try:
            log_entry = {
                "timestamp": deliberation.timestamp.isoformat(),
                "session_id": deliberation.session_id,
                "user_input": deliberation.user_input,
                "djinn_responses": [asdict(response) for response in deliberation.djinn_responses],
                "consensus_result": deliberation.consensus_result,
                "deliberation_mode": deliberation.deliberation_mode,
                "total_execution_time": deliberation.total_execution_time
            }
            
            with open(self.ledger_path, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.error(f"Failed to log deliberation: {e}")
    
    def _run_single_djinn(self, djinn_role: DjinnRole, user_input: str, session_context: List[str]) -> CouncilResponse:
        """Execute a single djinn consultation"""
        start_time = time.time()
        
        try:
            # Prepare context-aware prompt
            context_prompt = ""
            if session_context:
                context_prompt = f"Context from previous interactions:\n{chr(10).join(session_context[-3:])}\n\n"
            
            full_input = f"{context_prompt}Current query: {user_input}"
            
            # Execute Ollama model
            response = ollama.chat(
                model=djinn_role.model_name,
                messages=[
                    {"role": "system", "content": djinn_role.system_prompt},
                    {"role": "user", "content": full_input}
                ]
            )
            
            execution_time = time.time() - start_time
            response_text = response['message']['content']
            
            return CouncilResponse(
                djinn_name=djinn_role.name,
                role=djinn_role.role,
                response=response_text,
                timestamp=datetime.now(),
                execution_time=execution_time,
                token_count=len(response_text.split())  # Rough token estimate
            )
            
        except Exception as e:
            logger.error(f"Error executing djinn {djinn_role.name}: {e}")
            execution_time = time.time() - start_time
            
            return CouncilResponse(
                djinn_name=djinn_role.name,
                role=djinn_role.role,
                response=f"[ERROR: {str(e)}]",
                timestamp=datetime.now(),
                execution_time=execution_time,
                token_count=0
            )
    
    def _aggregate_consensus(self, responses: List[CouncilResponse], mode: str = "majority") -> str:
        """Consensus Aggregator Engine (CAE) - synthesize djinn responses"""
        if not responses:
            return "[ERROR: No responses received from council]"
        
        if mode == "unanimous":
            # Check for identical responses (rare)
            unique_responses = set(r.response for r in responses if not r.response.startswith("[ERROR"))
            if len(unique_responses) == 1:
                return f"🜂 UNANIMOUS COUNCIL DECISION:\n{list(unique_responses)[0]}"
            else:
                return self._aggregate_consensus(responses, "majority")  # Fallback to majority
        
        elif mode == "majority":
            # Weight responses by priority and synthesize
            weighted_responses = []
            total_weight = 0
            
            for response in responses:
                if not response.response.startswith("[ERROR"):
                    djinn_role = self.djinn_roles.get(response.role)
                    weight = djinn_role.priority_weight if djinn_role else 1.0
                    weighted_responses.append((response, weight))
                    total_weight += weight
            
            if not weighted_responses:
                return "[ERROR: All djinn responses failed]"
            
            # Create consensus summary
            consensus = "🜂 DJINN COUNCIL DELIBERATION COMPLETE:\n\n"
            
            for response, weight in sorted(weighted_responses, key=lambda x: x[1], reverse=True):
                priority_indicator = "⭐" * int(weight)
                consensus += f"[{response.djinn_name} {priority_indicator}]:\n{response.response}\n\n"
            
            # Add synthesis if multiple responses
            if len(weighted_responses) > 1:
                consensus += "--- COUNCIL SYNTHESIS ---\n"
                consensus += "The council has deliberated. Consider the weighted perspectives above, with higher priority (⭐) responses carrying more authority in the final decision."
            
            return consensus
        
        elif mode == "hybrid":
            # Allow manual selection - return all responses for user choice
            result = "🜂 DJINN COUNCIL RESPONSES - SELECT PREFERRED APPROACH:\n\n"
            for i, response in enumerate(responses, 1):
                if not response.response.startswith("[ERROR"):
                    result += f"[Option {i} - {response.djinn_name}]:\n{response.response}\n\n"
            return result
        
        else:
            return self._aggregate_consensus(responses, "majority")  # Default fallback
    
    def invoke_council(self, user_input: str, deliberation_mode: str = "majority") -> CouncilDeliberation:
        """
        Phase 1-4: Complete Djinn Council invocation sequence
        
        Args:
            user_input: The query or problem statement
            deliberation_mode: "unanimous", "majority", or "hybrid"
            
        Returns:
            CouncilDeliberation: Complete results of the council session
        """
        start_time = time.time()
        session_id = f"council_{int(time.time())}"
        
        logger.info(f"🜂 INVOKING DJINN COUNCIL - Session: {session_id}")
        logger.info(f"Query: {user_input[:100]}...")
        
        # Phase 1: Invocation Recognition and Binding
        self.council_active = True
        
        # Phase 2: Council Assembly and Parallel Model Spawning
        djinn_responses = []
        
        with ThreadPoolExecutor(max_workers=len(self.djinn_roles)) as executor:
            # Submit all djinn consultations in parallel
            future_to_djinn = {
                executor.submit(self._run_single_djinn, djinn_role, user_input, self.context_memory): djinn_role
                for djinn_role in self.djinn_roles.values()
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_djinn):
                djinn_role = future_to_djinn[future]
                try:
                    response = future.result()
                    djinn_responses.append(response)
                    logger.info(f"✓ {djinn_role.name} consultation complete ({response.execution_time:.2f}s)")
                except Exception as e:
                    logger.error(f"✗ {djinn_role.name} consultation failed: {e}")
        
        # Phase 3: Deliberation Cycle - Consensus Aggregator Engine
        consensus_result = self._aggregate_consensus(djinn_responses, deliberation_mode)
        
        # Phase 4: Response Generation and Logging
        total_execution_time = time.time() - start_time
        
        deliberation = CouncilDeliberation(
            session_id=session_id,
            user_input=user_input,
            djinn_responses=djinn_responses,
            consensus_result=consensus_result,
            deliberation_mode=deliberation_mode,
            total_execution_time=total_execution_time,
            timestamp=datetime.now()
        )
        
        # Log to Recursive Ledger
        self._log_deliberation(deliberation)
        
        # Update context memory
        self.context_memory.append(f"Query: {user_input}")
        self.context_memory.append(f"Council Decision: {consensus_result[:200]}...")
        
        # Keep context memory manageable
        if len(self.context_memory) > 10:
            self.context_memory = self.context_memory[-6:]
        
        self.council_active = False
        logger.info(f"🜂 Council session complete ({total_execution_time:.2f}s)")
        
        return deliberation
    
    def get_council_status(self) -> Dict[str, Any]:
        """Return current council status and health metrics"""
        return {
            "council_active": self.council_active,
            "available_djinn": list(self.djinn_roles.keys()),
            "context_memory_size": len(self.context_memory),
            "ledger_entries": self._count_ledger_entries(),
            "violation_threshold": self.violation_threshold,
            "config_path": self.config_path,
            "log_path": str(self.ledger_path)
        }
    
    def _count_ledger_entries(self) -> int:
        """Count entries in recursive ledger"""
        try:
            with open(self.ledger_path, 'r') as f:
                return sum(1 for _ in f)
        except:
            return 0

def main():
    """CLI interface for Djinn Council"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Djinn Council - Multi-Agent Ollama Orchestration")
    parser.add_argument("query", nargs="*", help="Query for the council")
    parser.add_argument("--mode", choices=["unanimous", "majority", "hybrid"], 
                       default="majority", help="Deliberation mode")
    parser.add_argument("--config", help="Path to djinn config file")
    parser.add_argument("--status", action="store_true", help="Show council status")
    
    args = parser.parse_args()
    
    # Initialize council
    council = DjinnCouncil(config_path=args.config)
    
    if args.status:
        status = council.get_council_status()
        print("🜂 DJINN COUNCIL STATUS:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        return
    
    if not args.query:
        # Interactive mode
        print("🜂 Djinn Council Interactive Mode")
        print("Enter 'quit' to exit, 'status' for council status")
        print("Use 'invoke council <query>' or just type your query")
        
        while True:
            try:
                user_input = input("\n💫 Query: ").strip()
                
                if user_input.lower() in ['quit', 'exit']:
                    break
                elif user_input.lower() == 'status':
                    status = council.get_council_status()
                    for key, value in status.items():
                        print(f"  {key}: {value}")
                    continue
                elif not user_input:
                    continue
                
                # Remove "invoke council" prefix if present
                if user_input.lower().startswith("invoke council"):
                    user_input = user_input[13:].strip()
                
                # Invoke council
                deliberation = council.invoke_council(user_input, args.mode)
                print(f"\n{deliberation.consensus_result}")
                
            except KeyboardInterrupt:
                print("\n🜂 Council session terminated")
                break
            except Exception as e:
                print(f"Error: {e}")
    else:
        # Direct query mode
        query = " ".join(args.query)
        deliberation = council.invoke_council(query, args.mode)
        print(deliberation.consensus_result)

if __name__ == "__main__":
    main()