#!/usr/bin/env python3
"""
🜂 DJINN COUNCIL GUI - MYSTICAL MULTI-AGENT ORCHESTRATION NEXUS 🜂

A visually stunning interface for commanding legions of AI djinn in mystical council.
Features:
- Ethereal typewriter-flow response layout
- Live thinking visualization with actual AI thoughts
- Mystical role descriptions and consensus tooltips
- Dark arcane aesthetics with crystalline components
- Real-time orchestration visualization
- Advanced memory and configuration management
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import json
import time
import subprocess
import math
import random
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

# Import our advanced council
from advanced_djinn_council import (
    AdvancedDjinnCouncil, DjinnRole, ConsensusMode, SecurityLevel,
    CouncilState, DjinnResponse, ConsensusResult
)

class OllamaModelManager:
    """Manages Ollama model detection and validation"""
    
    def __init__(self):
        self.available_models = []
        self.refresh_models()
    
    def refresh_models(self):
        """Refresh list of available Ollama models"""
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                self.available_models = []
                for line in lines:
                    if line.strip():
                        model_name = line.split()[0]  # First column is model name
                        self.available_models.append(model_name)
            else:
                self.available_models = ['llama3.2:latest']  # Fallback
        except Exception as e:
            print(f"Failed to get Ollama models: {e}")
            self.available_models = ['llama3.2:latest']  # Fallback
    
    def is_model_available(self, model_name: str) -> bool:
        """Check if a specific model is available"""
        return model_name in self.available_models

# DJINN ROLE DESCRIPTIONS AND MYSTICAL PROPERTIES
DJINN_ROLE_DESCRIPTIONS = {
    'strategist': {
        'title': '🧙‍♂️ The Strategic Oracle',
        'description': 'Master of long-term vision and recursive stability. Sees patterns across time and space, analyzing the future implications of every decision with prophetic wisdom.',
        'specialty': 'Future-sight, Strategic Planning, Recursive Analysis',
        'symbol': '🔮',
        'color': '#4A90E2'
    },
    'analyst': {
        'title': '📊 The Data Sage',
        'description': 'Wielder of technical precision and analytical mastery. Breaks down the most complex problems into crystalline clarity with mathematical perfection.',
        'specialty': 'Technical Analysis, Data Processing, Structural Examination',
        'symbol': '⚗️',
        'color': '#7ED321'
    },
    'arbiter': {
        'title': '⚖️ The Grand Arbitrator',
        'description': 'Supreme judge of the council with ultimate authority. Resolves conflicts with divine wisdom and neutral perspective, their word carries the weight of cosmic law.',
        'specialty': 'Conflict Resolution, Balanced Judgment, Final Authority',
        'symbol': '👑',
        'color': '#F5A623'
    },
    'guardian': {
        'title': '🛡️ The Protective Sentinel',
        'description': 'Eternal watchman against chaos and vulnerability. Sees danger where others see opportunity, providing impenetrable shields of security and risk assessment.',
        'specialty': 'Risk Assessment, Security Analysis, Protective Measures',
        'symbol': '🔒',
        'color': '#D0021B'
    },
    'architect': {
        'title': '🏗️ The System Builder',
        'description': 'Creator of grand designs and systematic order. Constructs elegant frameworks from chaotic requirements, building bridges between concept and reality.',
        'specialty': 'System Design, Framework Architecture, Implementation Planning',
        'symbol': '🏛️',
        'color': '#9013FE'
    },
    'historian': {
        'title': '📚 The Memory Keeper',
        'description': 'Chronicler of all that was and wisdom of ages past. Draws upon infinite libraries of precedent and experience to illuminate the path forward.',
        'specialty': 'Historical Context, Pattern Recognition, Precedent Analysis',
        'symbol': '📜',
        'color': '#795548'
    }
}

# CONSENSUS MODE DESCRIPTIONS
CONSENSUS_MODE_DESCRIPTIONS = {
    'majority_vote': {
        'title': '🗳️ Democratic Majority',
        'description': 'The wisdom of the crowd prevails. Responses are grouped by similarity and the largest faction determines the outcome. Pure democratic decision-making.',
        'details': 'Groups similar responses and selects the most popular viewpoint. Best for clear-cut decisions where consensus is achievable.'
    },
    'confidence_scoring': {
        'title': '💯 Confidence Supremacy', 
        'description': 'Let the most confident djinn lead the way. The response with the highest self-reported confidence score becomes the final answer.',
        'details': 'Selects the response with maximum confidence score. Ideal when expertise levels vary significantly among djinn.'
    },
    'weighted_roles': {
        'title': '👑 Hierarchical Authority',
        'description': 'Respects the natural order and role importance. Each djinn\'s contribution is weighted by their role priority and confidence score.',
        'details': 'Combines responses using role-based weights and confidence scores. Balances hierarchy with individual confidence.'
    },
    'deliberative_loop': {
        'title': '🔄 Iterative Wisdom',
        'description': 'Multiple rounds of discussion until convergence. Djinn review each other\'s responses and refine their answers through deliberation.',
        'details': 'Runs multiple consensus rounds allowing djinn to see and respond to each other. Continues until convergence or max iterations.'
    },
    'hybrid': {
        'title': '🌟 Mystical Synthesis',
        'description': 'The ultimate fusion of all approaches. Intelligently combines multiple consensus methods to achieve the most balanced outcome.',
        'details': 'Applies multiple consensus algorithms and synthesizes results. The most sophisticated but computationally intensive approach.'
    }
}

class DjinnResponseWidget(tk.Frame):
    """🎭 Mystical widget for displaying individual djinn responses with ethereal aesthetics"""
    
    def __init__(self, parent, djinn_name: str, role: str, position: tuple = (0, 0)):
        super().__init__(parent, bg='#1a1a2e', relief='raised', bd=2)
        self.djinn_name = djinn_name
        self.role = role
        self.position = position
        self.current_model = None
        self.thinking_animation_active = False
        
        # Get role info
        self.role_info = DJINN_ROLE_DESCRIPTIONS.get(role, {
            'title': f'🔮 The {role.title()}',
            'symbol': '✨',
            'color': '#666666'
        })
        
        # Timer and status tracking
        self.start_time = None
        self.timer_job = None
        self.animation_job = None
        self.current_thinking_text = ""
        self.live_thinking_content = []
        
        # Thinking patterns - more mystical and role-specific
        self.thinking_patterns = self._get_role_thinking_patterns()
        self.current_thinking_index = 0
        
        # Visual state
        self.is_thinking = False
        self.pulse_state = 0
        
        # Create mystical widget layout
        self.setup_mystical_widget()
        
    def _get_role_thinking_patterns(self):
        """Get role-specific thinking patterns"""
        patterns = {
            'strategist': [
                "🔮 Peering into possible futures...",
                "⏳ Analyzing temporal implications...",
                "🌀 Mapping recursive consequences...",
                "🎯 Identifying strategic leverage points...",
                "🧭 Charting the optimal path forward...",
                "⚡ Synthesizing long-term vision..."
            ],
            'analyst': [
                "📊 Decomposing problem structure...",
                "🔬 Examining data patterns...",
                "⚗️ Distilling key insights...",
                "📐 Calculating statistical significance...",
                "🎯 Identifying critical variables...",
                "🧮 Performing analytical synthesis..."
            ],
            'arbiter': [
                "⚖️ Weighing all perspectives...",
                "👑 Considering cosmic justice...",
                "🔍 Examining conflicting viewpoints...",
                "💎 Seeking balanced judgment...",
                "🎭 Evaluating moral implications...",
                "⚡ Preparing final arbitration..."
            ],
            'guardian': [
                "🛡️ Scanning for vulnerabilities...",
                "🔒 Assessing security implications...",
                "⚠️ Identifying potential risks...",
                "🚨 Evaluating threat vectors...",
                "🔐 Fortifying protective measures...",
                "⚔️ Preparing defensive strategies..."
            ],
            'architect': [
                "🏗️ Designing system architecture...",
                "📐 Crafting structural blueprints...",
                "🔧 Engineering elegant solutions...",
                "🏛️ Building conceptual frameworks...",
                "⚙️ Optimizing component integration...",
                "🎨 Perfecting systematic beauty..."
            ],
            'historian': [
                "📚 Consulting ancient wisdom...",
                "📜 Reviewing historical precedents...",
                "🕰️ Tracing patterns through time...",
                "🔍 Uncovering relevant parallels...",
                "💭 Drawing from collective memory...",
                "✨ Illuminating with past insights..."
            ]
        }
        return patterns.get(self.role, [
            "🌟 Processing mystical insights...",
            "✨ Channeling cosmic wisdom...",
            "🔮 Divining optimal solutions..."
        ])
    
    def setup_mystical_widget(self):
        """🎨 Setup the mystical visual layout with ethereal aesthetics"""
        self.configure(width=350, height=400)
        
        # Mystical header with role symbol and glow effect
        header_frame = tk.Frame(self, bg='#0f0f23', relief='groove', bd=1)
        header_frame.pack(fill='x', padx=2, pady=(2, 0))
        
        # Djinn symbol and name with mystical styling
        symbol_name_frame = tk.Frame(header_frame, bg='#0f0f23')
        symbol_name_frame.pack(fill='x', padx=5, pady=3)
        
        self.symbol_label = tk.Label(symbol_name_frame, 
                                    text=self.role_info['symbol'], 
                                    font=('Arial', 16), 
                                    bg='#0f0f23', 
                                    fg=self.role_info['color'])
        self.symbol_label.pack(side='left')
        
        self.name_label = tk.Label(symbol_name_frame, 
                                  text=f"{self.djinn_name}", 
                                  font=('Arial', 11, 'bold'), 
                                  bg='#0f0f23', 
                                  fg='#e6e6fa')
        self.name_label.pack(side='left', padx=(8, 0))
        
        self.role_label = tk.Label(symbol_name_frame, 
                                  text=self.role_info['title'], 
                                  font=('Arial', 8), 
                                  bg='#0f0f23', 
                                  fg='#b0b0b0')
        self.role_label.pack(side='left', padx=(5, 0))
        
        # Status and timer with mystical indicators
        status_frame = tk.Frame(header_frame, bg='#0f0f23')
        status_frame.pack(fill='x', padx=5, pady=(0, 3))
        
        self.status_label = tk.Label(status_frame, 
                                    text="💤 Dormant", 
                                    font=('Arial', 9), 
                                    bg='#0f0f23', 
                                    fg='#888888')
        self.status_label.pack(side='left')
        
        self.timer_label = tk.Label(status_frame, 
                                   text="00:00", 
                                   font=('JetBrains Mono', 9, 'bold'), 
                                   bg='#0f0f23', 
                                   fg='#00ff88')
        self.timer_label.pack(side='right')
        
        # Mystical confidence crystal
        crystal_frame = tk.Frame(self, bg='#1a1a2e', height=30)
        crystal_frame.pack(fill='x', padx=5, pady=2)
        crystal_frame.pack_propagate(False)
        
        tk.Label(crystal_frame, text="🔮 Confidence:", 
                font=('Arial', 8), bg='#1a1a2e', fg='#cccccc').pack(side='left', pady=8)
        
        self.confidence_var = tk.DoubleVar()
        self.confidence_canvas = tk.Canvas(crystal_frame, width=120, height=15, 
                                          bg='#1a1a2e', highlightthickness=0)
        self.confidence_canvas.pack(side='left', padx=(8, 5), pady=8)
        
        self.confidence_label = tk.Label(crystal_frame, text="0.00", 
                                        font=('JetBrains Mono', 8), 
                                        bg='#1a1a2e', fg='#00ff88')
        self.confidence_label.pack(side='left', pady=8)
        
        # Mystical vote button
        self.vote_button = tk.Button(crystal_frame, text="⭐ Choose", 
                                    font=('Arial', 8, 'bold'),
                                    bg='#4A90E2', fg='white', 
                                    state='disabled',
                                    relief='raised', bd=2,
                                    command=self.vote_for_response)
        self.vote_button.pack(side='right', padx=5, pady=5)
        
        # Mystical response area with dark theme
        self.response_text = scrolledtext.ScrolledText(
            self, height=12, wrap='word',
            font=('JetBrains Mono', 9),
            bg='#0d1117', fg='#e6edf3',
            insertbackground='#00ff88',
            selectbackground='#264f78',
            relief='sunken', bd=2
        )
        self.response_text.pack(fill='both', expand=True, padx=5, pady=2)
        self.response_text.config(state='disabled')
        
        # Configure text tags for syntax highlighting
        self.response_text.tag_configure('thinking', foreground='#7c3aed', font=('JetBrains Mono', 9, 'italic'))
        self.response_text.tag_configure('djinn_name', foreground='#fbbf24', font=('JetBrains Mono', 9, 'bold'))
        self.response_text.tag_configure('timestamp', foreground='#6b7280', font=('JetBrains Mono', 8))
        self.response_text.tag_configure('confidence', foreground='#10b981', font=('JetBrains Mono', 8, 'bold'))
        self.response_text.tag_configure('model_info', foreground='#8b5cf6', font=('JetBrains Mono', 8))
        
        # Execution time with mystical styling
        self.time_label = tk.Label(self, text="", 
                                  font=('Arial', 8), 
                                  bg='#1a1a2e', fg='#888888')
        self.time_label.pack(pady=2)
        
        # Initialize confidence crystal
        self._draw_confidence_crystal(0.0)
    
    def _draw_confidence_crystal(self, confidence_level: float):
        """🔮 Draw mystical confidence crystal"""
        self.confidence_canvas.delete("all")
        width = 120
        height = 15
        
        # Background crystal structure
        self.confidence_canvas.create_rectangle(2, 2, width-2, height-2, 
                                               outline='#4a5568', fill='#1a202c')
        
        # Confidence fill with gradient effect
        fill_width = int((width - 4) * confidence_level)
        if fill_width > 0:
            # Create gradient colors based on confidence
            if confidence_level < 0.3:
                color = '#dc2626'  # Red for low confidence
            elif confidence_level < 0.7:
                color = '#f59e0b'  # Amber for medium confidence  
            else:
                color = '#10b981'  # Green for high confidence
                
            self.confidence_canvas.create_rectangle(3, 3, 3 + fill_width, height-3,
                                                   outline='', fill=color)
            
            # Add sparkle effects for high confidence
            if confidence_level > 0.8:
                for i in range(3):
                    x = random.randint(5, fill_width - 5)
                    y = random.randint(5, height - 5)
                    self.confidence_canvas.create_oval(x-1, y-1, x+1, y+1, 
                                                      fill='white', outline='')
    
    def set_thinking(self):
        """🎭 Set widget to mystical thinking state with live orchestration"""
        self.start_time = time.time()
        self.current_thinking_index = 0
        self.is_thinking = True
        self.thinking_animation_active = True
        self.live_thinking_content = []
        
        # Start mystical animations
        self._start_timer()
        self._start_thinking_animation()
        
        # Mystical thinking state
        self.status_label.config(text="🌀 Awakening...", fg='#7c3aed')
        self.confidence_var.set(0)
        self.confidence_label.config(text="0.00")
        self._draw_confidence_crystal(0.0)
        self.vote_button.config(state='disabled', bg='#374151')
        
        # Show mystical thinking initialization
        self.response_text.config(state='normal')
        self.response_text.delete(1.0, tk.END)
        
        thinking_header = f"""🌀 {self.role_info['title']} AWAKENS 🌀
{'=' * 50}
🔮 Channeling {self.role_info['specialty']}
✨ Model: {self.current_model or 'Unknown'}
🎭 Beginning mystical contemplation...

🧠 LIVE THINKING PROCESS:
{'─' * 50}
"""
        
        self.response_text.insert(tk.END, thinking_header, 'thinking')
        self.response_text.insert(tk.END, f"💭 {self.thinking_patterns[0]}\n", 'djinn_name')
        self.response_text.insert(tk.END, "\n⏳ Unlimited time granted for deep contemplation...\n", 'timestamp')
        self.response_text.config(state='disabled')
    
    def _start_timer(self):
        """Start the live timer and thinking updates"""
        self._update_timer_and_status()
    
    def _start_thinking_animation(self):
        """🎪 Start mystical thinking animation"""
        self._animate_thinking_symbols()
    
    def _animate_thinking_symbols(self):
        """✨ Animate the djinn symbol with pulsing effect"""
        if not self.thinking_animation_active:
            return
            
        # Pulse the djinn symbol
        self.pulse_state = (self.pulse_state + 1) % 60
        
        # Create pulsing effect with sine wave
        pulse_intensity = (math.sin(self.pulse_state * 0.2) + 1) / 2
        
        # Update symbol color based on pulse
        base_color = self.role_info['color']
        if pulse_intensity > 0.7:
            self.symbol_label.config(fg='#ffffff')  # Bright flash
        elif pulse_intensity > 0.4:
            self.symbol_label.config(fg=base_color)  # Normal color
        else:
            self.symbol_label.config(fg='#666666')  # Dimmed
        
        # Schedule next animation frame
        self.animation_job = self.after(100, self._animate_thinking_symbols)
    
    def _update_timer_and_status(self):
        """⏰ Update mystical timer display and thinking orchestration"""
        if self.start_time is None or not self.is_thinking:
            return
            
        # Calculate elapsed time with mystical precision
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        
        # Update timer with color coding
        if elapsed < 30:
            self.timer_label.config(text=time_str, fg='#10b981')
        elif elapsed < 120:
            self.timer_label.config(text=time_str, fg='#f59e0b')
        else:
            self.timer_label.config(text=time_str, fg='#ef4444')
        
        # Update mystical thinking status every 8 seconds
        if int(elapsed) % 8 == 0 and int(elapsed) > 0:
            self._update_mystical_thinking_status(elapsed)
        
        # Progressive status updates with mystical themes
        if elapsed > 45:  # After 45 seconds
            self.status_label.config(text="🔮 Deep Divination...", fg='#7c3aed')
        if elapsed > 120:  # After 2 minutes
            self.status_label.config(text="🌌 Cosmic Reasoning...", fg='#3b82f6')
        if elapsed > 300:  # After 5 minutes  
            self.status_label.config(text="💫 Transcendent Analysis...", fg='#10b981')
        
        # Schedule next mystical update
        self.timer_job = self.after(1000, self._update_timer_and_status)
    
    def _update_mystical_thinking_status(self, elapsed_time):
        """🔮 Update mystical thinking orchestration with live insights"""
        # Cycle through role-specific thinking patterns
        message_interval = 8
        message_index = (int(elapsed_time) // message_interval) % len(self.thinking_patterns)
        
        if message_index != self.current_thinking_index:
            self.current_thinking_index = message_index
            current_pattern = self.thinking_patterns[message_index]
            
            # Add thinking insight to live content
            timestamp = datetime.now().strftime('%H:%M:%S')
            thinking_entry = f"[{timestamp}] {current_pattern}"
            self.live_thinking_content.append(thinking_entry)
            
            # Update the mystical response display
            self.response_text.config(state='normal')
            
            # Add new thinking line
            self.response_text.insert(tk.END, f"\n{thinking_entry}", 'thinking')
            
            # Add mystical progress indicators
            depth_indicator = "✨" * (message_index + 1)
            elapsed_display = f"\n⏳ Contemplation depth: {int(elapsed_time)}s {depth_indicator}\n"
            
            # Special insights based on thinking time
            if int(elapsed_time) % 30 == 0 and elapsed_time > 30:
                mystical_insight = self._generate_mystical_insight(elapsed_time)
                self.response_text.insert(tk.END, f"\n🔮 MYSTICAL INSIGHT: {mystical_insight}\n", 'confidence')
            
            self.response_text.insert(tk.END, elapsed_display, 'timestamp')
            self.response_text.see(tk.END)
            self.response_text.config(state='disabled')
    
    def _generate_mystical_insight(self, elapsed_time):
        """🌟 Generate role-specific mystical insights during long thinking"""
        insights = {
            'strategist': [
                "Multiple timeline convergences detected",
                "Long-term stability patterns emerging", 
                "Strategic leverage points crystallizing",
                "Future-state probability matrices stabilizing"
            ],
            'analyst': [
                "Data correlation patterns strengthening",
                "Statistical significance thresholds reached",
                "Critical variable interactions identified",
                "Analytical framework coherence achieved"
            ],
            'arbiter': [
                "Moral weight calculations balancing",
                "Justice algorithms reaching equilibrium",
                "Ethical framework synthesis completing",
                "Wisdom-based decision tree optimizing"
            ],
            'guardian': [
                "Threat assessment matrices stabilizing",
                "Security perimeter analysis deepening",
                "Risk mitigation strategies crystallizing",
                "Protective protocol optimization active"
            ],
            'architect': [
                "System design blueprints crystallizing",
                "Architectural pattern recognition active",
                "Framework integration points solidifying",
                "Structural optimization algorithms running"
            ],
            'historian': [
                "Historical pattern matching intensifying",
                "Precedent correlation analysis deepening",
                "Temporal context synthesis strengthening",
                "Wisdom archive synchronization active"
            ]
        }
        
        role_insights = insights.get(self.role, ["Cosmic wisdom channels opening"])
        phase = int(elapsed_time // 30) % len(role_insights)
        return role_insights[phase]
    
    def _stop_timer(self):
        """⏹️ Stop the mystical timer and animations"""
        self.is_thinking = False
        self.thinking_animation_active = False
        
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None
            
        if self.animation_job:
            self.after_cancel(self.animation_job)
            self.animation_job = None
            
        # Reset symbol to normal state
        self.symbol_label.config(fg=self.role_info['color'])
    
    def _is_advanced_thinking_model(self) -> bool:
        """🧠 Check if current model supports advanced thinking patterns"""
        if not self.current_model:
            return False
        model_lower = self.current_model.lower()
        return any(pattern in model_lower for pattern in ['deepseek', 'o1', 'thinking', 'reasoning'])
    
    def set_model(self, model_name: str):
        """Set the current model for this djinn"""
        self.current_model = model_name
    
    def set_response(self, response: DjinnResponse):
        """Update widget with djinn response"""
        # Stop the live timer
        self._stop_timer()
        
        # Calculate final thinking time
        if self.start_time:
            total_thinking_time = time.time() - self.start_time
            minutes = int(total_thinking_time // 60)
            seconds = int(total_thinking_time % 60)
            final_time_str = f"{minutes:02d}:{seconds:02d}"
            self.timer_label.config(text=final_time_str, foreground='green')
        
        if response.response.startswith("[ERROR"):
            self.status_label.config(text="❌ Error", foreground='red')
            self.confidence_var.set(0)
            self.confidence_label.config(text="0.00")
        else:
            self.status_label.config(text="✅ Complete", foreground='green')
            self.confidence_var.set(response.confidence_score)
            self.confidence_label.config(text=f"{response.confidence_score:.2f}")
            self.vote_button.config(state='normal')
        
        # Update response text with final response
        self.response_text.config(state='normal')
        self.response_text.delete(1.0, tk.END)
        
        # Add thinking summary header
        if self.start_time:
            thinking_summary = f"🧠 Thinking completed in {response.execution_time:.1f}s\n"
            
            # Check if this is a deepseek model with thinking content
            if response.metadata and response.metadata.get("has_thinking", False):
                thinking_content = response.metadata.get("thinking_content", "")
                model_name = response.metadata.get("model_name", "")
                
                thinking_summary += f"🤖 Model: {model_name}\n"
                thinking_summary += f"🧠 Deep Thinking Process:\n"
                thinking_summary += "-" * 40 + "\n"
                thinking_summary += thinking_content[:500] + ("..." if len(thinking_content) > 500 else "")
                thinking_summary += "\n" + "-" * 40 + "\n\n"
                thinking_summary += f"💭 Final Response from {self.djinn_name}:\n"
            else:
                thinking_summary += f"💭 Final response from {self.djinn_name}:\n"
            
            thinking_summary += "=" * 50 + "\n\n"
            self.response_text.insert(tk.END, thinking_summary)
        
        # Add actual response
        self.response_text.insert(tk.END, response.response)
        self.response_text.config(state='disabled')
        
        # Update execution time with more detail
        if self.start_time:
            total_time = time.time() - self.start_time
            self.time_label.config(text=f"Thought for {total_time:.1f}s (Model exec: {response.execution_time:.1f}s)")
        else:
            self.time_label.config(text=f"Execution time: {response.execution_time:.2f}s")
        
        # Store response for voting
        self.current_response = response
    
    def vote_for_response(self):
        """Handle vote button click"""
        # This would trigger a callback to the main GUI
        if hasattr(self, 'vote_callback'):
            self.vote_callback(self.current_response)

class DjinnCouncilGUI:
    """🌌 MYSTICAL DJINN COUNCIL NEXUS - Supreme Orchestration Interface 🌌"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🌂 DJINN COUNCIL NEXUS - Mystical Multi-Agent Orchestration 🌂")
        self.root.geometry("1600x1000")
        
        # Apply dark mystical theme
        self.root.configure(bg='#0a0a0f')
        
        # Configure mystical styling
        style = ttk.Style()
        style.theme_use('clam')
        
        # Mystical color scheme
        style.configure('Mystical.TFrame', background='#1a1a2e')
        style.configure('Mystical.TLabel', background='#1a1a2e', foreground='#e6e6fa')
        style.configure('Mystical.TLabelFrame', background='#1a1a2e', foreground='#4A90E2')
        
        # Initialize mystical components
        self.model_manager = OllamaModelManager()
        self.council = None
        self.djinn_widgets = {}
        self.response_queue = queue.Queue()
        
        # Typewriter layout tracking
        self.djinn_positions = {}
        self.max_columns = 3  # 3 djinn per row in typewriter layout
        
        # User identification
        self.user_id = "gui_user"
        
        # Mystical configuration
        self.config_file = "djinn_gui_config.json"
        self.current_config = self.load_config()
        
        # Setup mystical GUI
        self.setup_mystical_gui()
        self.setup_council()
        
        # Start mystical response monitoring
        self.monitor_responses()
    
    def setup_mystical_gui(self):
        """🎨 Setup the mystical GUI layout with ethereal aesthetics"""
        # Create mystical main container
        main_container = tk.Frame(self.root, bg='#0a0a0f')
        main_container.pack(fill='both', expand=True, padx=8, pady=8)
        
        # Mystical header with cosmic title
        self.setup_cosmic_header(main_container)
        
        # Main mystical paned window
        main_pane = ttk.PanedWindow(main_container, orient='vertical', style='Mystical.TPanedwindow')
        main_pane.pack(fill='both', expand=True, pady=(5, 0))
        
        # Top realm - Configuration and mystical controls
        self.setup_mystical_config_frame(main_pane)
        
        # Middle realm - Consultation interface
        self.setup_mystical_chat_frame(main_pane)
        
        # Bottom realm - Djinn orchestration display (typewriter layout)
        self.setup_mystical_responses_frame(main_pane)
        
        # Mystical status nexus
        self.setup_mystical_status_bar(main_container)
    
    def setup_cosmic_header(self, parent):
        """🌌 Setup cosmic header with mystical title"""
        header_frame = tk.Frame(parent, bg='#0a0a0f', height=60)
        header_frame.pack(fill='x', pady=(0, 5))
        header_frame.pack_propagate(False)
        
        # Cosmic title with mystical symbols
        title_label = tk.Label(header_frame, 
                              text="🌌 🌂 DJINN COUNCIL NEXUS 🌂 🌌",
                              font=('Arial', 18, 'bold'),
                              bg='#0a0a0f', fg='#4A90E2')
        title_label.pack(pady=15)
        
        # Mystical subtitle
        subtitle_label = tk.Label(header_frame,
                                 text="Mystical Multi-Agent Orchestration • Command Legions of AI Djinn • Channel Cosmic Wisdom",
                                 font=('Arial', 10),
                                 bg='#0a0a0f', fg='#b0b0b0')
        subtitle_label.pack()
    
    def setup_config_frame(self, parent):
        """Setup configuration frame"""
        config_frame = ttk.LabelFrame(parent, text="🔧 Council Configuration", padding=10)
        parent.add(config_frame, weight=0)
        
        # Model assignment section
        models_frame = ttk.Frame(config_frame)
        models_frame.pack(fill='x', pady=5)
        
        ttk.Label(models_frame, text="Model Assignment:", font=('Arial', 10, 'bold')).pack(anchor='w')
        
        # Create model selection for each role
        self.model_vars = {}
        roles_frame = ttk.Frame(models_frame)
        roles_frame.pack(fill='x', pady=5)
        
        default_roles = ['strategist', 'analyst', 'arbiter', 'guardian', 'architect', 'historian']
        
        for i, role in enumerate(default_roles):
            row = i // 3
            col = i % 3
            
            role_frame = ttk.Frame(roles_frame)
            role_frame.grid(row=row, column=col, padx=10, pady=2, sticky='w')
            
            ttk.Label(role_frame, text=f"{role.title()}:", width=10).pack(side='left')
            
            self.model_vars[role] = tk.StringVar()
            model_combo = ttk.Combobox(role_frame, textvariable=self.model_vars[role],
                                      values=self.model_manager.available_models,
                                      width=20, state='readonly')
            model_combo.pack(side='left', padx=5)
            
            # Set default value
            if role in self.current_config.get('model_assignments', {}):
                self.model_vars[role].set(self.current_config['model_assignments'][role])
            else:
                self.model_vars[role].set(self.model_manager.available_models[0] if self.model_manager.available_models else 'llama3.2:latest')
        
        # Controls section
        controls_frame = ttk.Frame(config_frame)
        controls_frame.pack(fill='x', pady=10)
        
        # Consensus mode selection
        ttk.Label(controls_frame, text="Consensus Mode:").pack(side='left')
        self.consensus_var = tk.StringVar(value='weighted_roles')
        consensus_combo = ttk.Combobox(controls_frame, textvariable=self.consensus_var,
                                      values=[mode.value for mode in ConsensusMode],
                                      width=15, state='readonly')
        consensus_combo.pack(side='left', padx=5)
        
        # Buttons
        ttk.Button(controls_frame, text="🔄 Refresh Models", 
                  command=self.refresh_models).pack(side='right', padx=2)
        ttk.Button(controls_frame, text="💾 Save Config", 
                  command=self.save_config).pack(side='right', padx=2)
        ttk.Button(controls_frame, text="📁 Load Config", 
                  command=self.load_config_dialog).pack(side='right', padx=2)
        ttk.Button(controls_frame, text="🔧 Apply Changes", 
                  command=self.apply_config).pack(side='right', padx=2)
        ttk.Button(controls_frame, text="🧠 Memory Stats", 
                  command=self.show_memory_stats).pack(side='right', padx=2)
        ttk.Button(controls_frame, text="🗑️ Clear Memory", 
                  command=self.clear_memory_dialog).pack(side='right', padx=2)
    
    def setup_chat_frame(self, parent):
        """Setup chat interface frame"""
        chat_frame = ttk.LabelFrame(parent, text="💬 Council Consultation", padding=10)
        parent.add(chat_frame, weight=1)
        
        # Chat history
        self.chat_history = scrolledtext.ScrolledText(chat_frame, height=10, wrap='word',
                                                     font=('Consolas', 10))
        self.chat_history.pack(fill='both', expand=True, pady=(0, 10))
        
        # Input frame
        input_frame = ttk.Frame(chat_frame)
        input_frame.pack(fill='x')
        
        # Query input
        ttk.Label(input_frame, text="Your Query:").pack(anchor='w')
        query_input_frame = ttk.Frame(input_frame)
        query_input_frame.pack(fill='x', pady=5)
        
        self.query_text = scrolledtext.ScrolledText(query_input_frame, height=3, wrap='word',
                                                   font=('Arial', 10))
        self.query_text.pack(side='left', fill='both', expand=True)
        
        # Submit button
        button_frame = ttk.Frame(query_input_frame)
        button_frame.pack(side='right', padx=(10, 0), fill='y')
        
        self.submit_button = ttk.Button(button_frame, text="🜂\nInvoke\nCouncil", 
                                       command=self.invoke_council)
        self.submit_button.pack(fill='both', expand=True)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready to invoke council")
        progress_frame = ttk.Frame(input_frame)
        progress_frame.pack(fill='x', pady=5)
        
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.pack(side='left')
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(side='right', fill='x', expand=True, padx=(10, 0))
    
    def setup_responses_frame(self, parent):
        """Setup djinn responses frame"""
        responses_frame = ttk.LabelFrame(parent, text="🧠 Djinn Responses", padding=5)
        parent.add(responses_frame, weight=2)
        
        # Create notebook for different views
        self.responses_notebook = ttk.Notebook(responses_frame)
        self.responses_notebook.pack(fill='both', expand=True)
        
        # Individual responses tab
        individual_frame = ttk.Frame(self.responses_notebook)
        self.responses_notebook.add(individual_frame, text="Individual Responses")
        
        # Create scrollable frame for djinn widgets
        canvas = tk.Canvas(individual_frame)
        scrollbar = ttk.Scrollbar(individual_frame, orient="vertical", command=canvas.yview)
        self.djinn_responses_frame = ttk.Frame(canvas)
        
        self.djinn_responses_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.djinn_responses_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Consensus result tab
        consensus_frame = ttk.Frame(self.responses_notebook)
        self.responses_notebook.add(consensus_frame, text="Consensus Result")
        
        self.consensus_text = scrolledtext.ScrolledText(consensus_frame, wrap='word',
                                                       font=('Consolas', 11))
        self.consensus_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Metrics tab
        metrics_frame = ttk.Frame(self.responses_notebook)
        self.responses_notebook.add(metrics_frame, text="Session Metrics")
        
        self.metrics_text = scrolledtext.ScrolledText(metrics_frame, wrap='word',
                                                     font=('Consolas', 10))
        self.metrics_text.pack(fill='both', expand=True, padx=5, pady=5)
    
    def setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side='bottom', fill='x')
        
        self.status_var = tk.StringVar(value="Ready - Council initialized")
        self.status_label = ttk.Label(self.status_bar, textvariable=self.status_var)
        self.status_label.pack(side='left', padx=5)
        
        # Council state indicator
        self.state_var = tk.StringVar(value="IDLE")
        self.state_label = ttk.Label(self.status_bar, textvariable=self.state_var, 
                                    foreground='blue', font=('Arial', 8, 'bold'))
        self.state_label.pack(side='right', padx=5)
    
    def setup_council(self):
        """Initialize the council with current configuration"""
        try:
            if self.council:
                self.council.shutdown()
            
            # Create council with user ID for persistent memory
            self.council = AdvancedDjinnCouncil(user_id=self.user_id)
            
            # Apply current configuration
            self.apply_config()
            
            # Load any existing conversation history into chat display
            self.load_conversation_history()
            
            self.status_var.set("Council initialized successfully")
            
            # Create djinn response widgets
            self.create_djinn_widgets()
            
        except Exception as e:
            messagebox.showerror("Council Initialization Error", f"Failed to initialize council: {str(e)}")
            self.status_var.set(f"Error: {str(e)}")
    
    def create_djinn_widgets(self):
        """Create response widgets for each djinn"""
        # Clear existing widgets
        for widget in self.djinn_widgets.values():
            widget.destroy()
        self.djinn_widgets.clear()
        
        # Create new widgets
        if self.council and self.council.djinn_roles:
            for i, (role_key, djinn_role) in enumerate(self.council.djinn_roles.items()):
                widget = DjinnResponseWidget(self.djinn_responses_frame, 
                                           djinn_role.name, djinn_role.role)
                widget.pack(fill='x', padx=5, pady=5)
                widget.vote_callback = self.vote_for_djinn_response
                self.djinn_widgets[role_key] = widget
    
    def refresh_models(self):
        """Refresh available Ollama models"""
        self.model_manager.refresh_models()
        
        # Update all comboboxes
        for role in self.model_vars:
            combo_widget = None
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.PanedWindow):
                    for child in widget.winfo_children():
                        if isinstance(child, ttk.LabelFrame) and "Configuration" in child.cget("text"):
                            # Find and update combobox
                            for descendant in child.winfo_children():
                                if isinstance(descendant, ttk.Frame):
                                    for subchild in descendant.winfo_children():
                                        if isinstance(subchild, ttk.Frame):
                                            for combo in subchild.winfo_children():
                                                if isinstance(combo, ttk.Combobox) and combo.cget('textvariable') == str(self.model_vars[role]):
                                                    combo.configure(values=self.model_manager.available_models)
        
        self.status_var.set(f"Found {len(self.model_manager.available_models)} Ollama models")
    
    def apply_config(self):
        """Apply current configuration to the council"""
        if not self.council:
            return
        
        try:
            # Update djinn roles with selected models
            for role_key, model_var in self.model_vars.items():
                if role_key in self.council.djinn_roles:
                    selected_model = model_var.get()
                    if selected_model and self.model_manager.is_model_available(selected_model):
                        self.council.djinn_roles[role_key].model_name = selected_model
                        
                        # Update the widget with the model information
                        if role_key in self.djinn_widgets:
                            self.djinn_widgets[role_key].set_model(selected_model)
                    else:
                        messagebox.showwarning("Model Not Available", 
                                             f"Model '{selected_model}' not available for {role_key}")
            
            # Recreate workers with new model assignments
            self.council._initialize_workers()
            
            # Recreate widgets (this will set models again)
            self.create_djinn_widgets()
            
            self.status_var.set("Configuration applied successfully")
            
        except Exception as e:
            messagebox.showerror("Configuration Error", f"Failed to apply configuration: {str(e)}")
    
    def _start_mystical_progress(self):
        """🌟 Start mystical progress animation"""
        self.progress_active = True
        self.progress_canvas.delete("all")
        self._animate_mystical_progress()
    
    def _stop_mystical_progress(self):
        """⏹️ Stop mystical progress animation"""
        self.progress_active = False
        self.progress_canvas.delete("all")
    
    def _animate_mystical_progress(self):
        """✨ Animate mystical progress with cosmic effects"""
        if not self.progress_active:
            return
            
        self.progress_canvas.delete("all")
        width = self.progress_canvas.winfo_width()
        height = self.progress_canvas.winfo_height()
        
        if width > 1 and height > 1:
            # Create flowing mystical energy
            time_offset = time.time() * 3  # Speed multiplier
            
            for i in range(5):
                x = (time_offset * 50 + i * 40) % (width + 40) - 20
                y = height // 2 + math.sin(time_offset + i) * 3
                
                # Create mystical orbs
                self.progress_canvas.create_oval(x-3, y-3, x+3, y+3, 
                                               fill='#4A90E2', outline='#7c3aed', width=1)
                
                # Add sparkle trail
                trail_x = x - 15
                if trail_x > 0:
                    self.progress_canvas.create_oval(trail_x-1, y-1, trail_x+1, y+1,
                                                   fill='#bc8cff', outline='')
        
        # Schedule next animation frame
        self.root.after(50, self._animate_mystical_progress)
    
    def invoke_council(self):
        """Invoke the djinn council with the current query"""
        query = self.query_text.get(1.0, tk.END).strip()
        if not query:
            messagebox.showwarning("Empty Query", "Please enter a query for the council.")
            return
        
        if not self.council:
            messagebox.showerror("Council Error", "Council not initialized.")
            return
        
        # Disable submit button and start mystical progress
        self.submit_button.config(state='disabled', bg='#374151')
        self._start_mystical_progress()
        self.progress_var.set("🌌 Invoking mystical council... (Models have unlimited contemplation time) 🌌")
        
        # Set all djinn widgets to thinking state
        for widget in self.djinn_widgets.values():
            widget.set_thinking()
        
        # Add query to chat history
        self.add_to_chat_history(f"🤔 Your Query: {query}\n", 'user')
        
        # Start council invocation in separate thread
        threading.Thread(target=self._invoke_council_thread, args=(query,), daemon=True).start()
    
    def _invoke_council_thread(self, query: str):
        """Thread function for council invocation"""
        try:
            # Get consensus mode
            consensus_mode = ConsensusMode(self.consensus_var.get())
            
            # Invoke council (no timeout - let models think as long as needed)
            session = self.council.invoke_council(query, consensus_mode, timeout=None)
            
            # Queue results for main thread
            self.response_queue.put(('session_complete', session))
            
        except Exception as e:
            self.response_queue.put(('error', str(e)))
    
    def monitor_responses(self):
        """Monitor response queue and update GUI"""
        try:
            while True:
                try:
                    message_type, data = self.response_queue.get_nowait()
                    
                    if message_type == 'session_complete':
                        self.handle_session_complete(data)
                    elif message_type == 'error':
                        self.handle_council_error(data)
                        
                except queue.Empty:
                    break
                    
        except Exception as e:
            print(f"Error monitoring responses: {e}")
        
        # Schedule next check
        self.root.after(100, self.monitor_responses)
    
    def handle_session_complete(self, session):
        """Handle completed council session"""
        # Update djinn response widgets
        for response in session.djinn_responses:
            role_key = response.role
            if role_key in self.djinn_widgets:
                self.djinn_widgets[role_key].set_response(response)
        
        # Update consensus result
        if session.consensus_result:
            self.consensus_text.delete(1.0, tk.END)
            self.consensus_text.insert(tk.END, session.consensus_result.final_response)
            
            # Add to chat history
            self.add_to_chat_history(f"🜂 Council Decision:\n{session.consensus_result.final_response}\n\n", 'council')
        
        # Update metrics
        self.update_metrics_display(session)
        
        # Update mystical state and status
        self.state_var.set("IDLE")
        self._stop_mystical_progress()
        self.progress_var.set("✨ Mystical council invocation complete ✨")
        self.submit_button.config(state='normal', bg='#4A90E2')
        self.status_var.set(f"Session completed in {session.total_execution_time:.2f}s")
        
        # Switch to consensus result tab
        self.responses_notebook.select(1)
    
    def handle_council_error(self, error_msg: str):
        """💥 Handle mystical council invocation error"""
        self._stop_mystical_progress()
        self.progress_var.set("💥 Mystical error in the cosmic fabric 💥")
        self.submit_button.config(state='normal', bg='#4A90E2')
        self.status_var.set(f"Error: {error_msg}")
        self.state_var.set("ERROR")
        
        messagebox.showerror("Council Error", f"Council invocation failed: {error_msg}")
    
    def update_metrics_display(self, session):
        """Update metrics display"""
        metrics_text = f"""Session Metrics
================

Session ID: {session.session_id}
Total Execution Time: {session.total_execution_time:.2f}s
Consensus Mode: {session.consensus_result.consensus_mode.value}
Overall Confidence: {session.consensus_result.confidence_level:.2f}
Divergence Score: {session.consensus_result.divergence_score:.2f}
Recursion Depth: {session.recursion_depth}

Individual Response Times:
"""
        
        for response in session.djinn_responses:
            metrics_text += f"  {response.djinn_name}: {response.execution_time:.2f}s (confidence: {response.confidence_score:.2f})\n"
        
        if session.security_events:
            metrics_text += f"\nSecurity Events:\n"
            for event in session.security_events:
                metrics_text += f"  - {event}\n"
        
        metrics_text += f"\nState Transitions:\n"
        for state, timestamp in session.state_history:
            metrics_text += f"  {state.value}: {timestamp.strftime('%H:%M:%S.%f')[:-3]}\n"
        
        self.metrics_text.delete(1.0, tk.END)
        self.metrics_text.insert(tk.END, metrics_text)
    
    def add_to_chat_history(self, text: str, sender: str):
        """Add text to chat history with formatting"""
        self.chat_history.config(state='normal')
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_history.insert(tk.END, f"[{timestamp}] ")
        
        # Add text with color coding
        if sender == 'user':
            self.chat_history.insert(tk.END, text)
        elif sender == 'council':
            self.chat_history.insert(tk.END, text)
        
        self.chat_history.insert(tk.END, "\n" + "="*80 + "\n\n")
        self.chat_history.see(tk.END)
        self.chat_history.config(state='disabled')
    
    def vote_for_djinn_response(self, response: DjinnResponse):
        """Handle voting for a specific djinn response"""
        # Override consensus with voted response
        vote_text = f"👍 MANUAL OVERRIDE - Selected {response.djinn_name}'s Response:\n\n{response.response}"
        
        self.consensus_text.delete(1.0, tk.END)
        self.consensus_text.insert(tk.END, vote_text)
        
        self.add_to_chat_history(f"👍 You selected {response.djinn_name}'s response as the final decision.\n", 'user')
        
        # Switch to consensus tab
        self.responses_notebook.select(1)
    
    def load_config(self) -> Dict[str, Any]:
        """Load GUI configuration"""
        if Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Failed to load config: {e}")
        
        return {
            'model_assignments': {},
            'consensus_mode': 'weighted_roles',
            'window_geometry': '1400x900'
        }
    
    def save_config(self):
        """Save current GUI configuration"""
        config = {
            'model_assignments': {role: var.get() for role, var in self.model_vars.items()},
            'consensus_mode': self.consensus_var.get(),
            'window_geometry': self.root.geometry()
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            self.status_var.set("Configuration saved successfully")
            messagebox.showinfo("Config Saved", f"Configuration saved to {self.config_file}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save configuration: {str(e)}")
    
    def load_config_dialog(self):
        """Load configuration from file dialog"""
        file_path = filedialog.askopenfilename(
            title="Load Djinn Council Configuration",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    config = json.load(f)
                
                # Apply loaded configuration
                for role, model in config.get('model_assignments', {}).items():
                    if role in self.model_vars:
                        self.model_vars[role].set(model)
                
                if 'consensus_mode' in config:
                    self.consensus_var.set(config['consensus_mode'])
                
                self.current_config = config
                self.status_var.set(f"Configuration loaded from {Path(file_path).name}")
                messagebox.showinfo("Config Loaded", f"Configuration loaded successfully")
                
            except Exception as e:
                messagebox.showerror("Load Error", f"Failed to load configuration: {str(e)}")
    
    def load_conversation_history(self):
        """Load existing conversation history into the chat display"""
        if not self.council or not self.council.conversational_memory:
            return
        
        # Get recent conversation history
        recent_turns = self.council.conversational_memory.conversation_history[-10:]  # Last 10 turns
        
        if recent_turns:
            self.chat_history.config(state='normal')
            self.chat_history.insert(tk.END, "=== Previous Conversation History ===\n\n")
            
            for turn in recent_turns:
                # Format timestamp
                time_str = turn.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                self.chat_history.insert(tk.END, f"[{time_str}]\n")
                self.chat_history.insert(tk.END, f"🤔 Your Query: {turn.user_query}\n")
                self.chat_history.insert(tk.END, f"🜂 Council Decision: {turn.council_response}\n\n")
                self.chat_history.insert(tk.END, "-" * 80 + "\n\n")
            
            self.chat_history.insert(tk.END, "=== Current Session ===\n\n")
            self.chat_history.see(tk.END)
            self.chat_history.config(state='disabled')
    
    def show_memory_stats(self):
        """Show conversational memory statistics"""
        if not self.council:
            messagebox.showwarning("No Council", "Council not initialized.")
            return
        
        memory_stats = self.council.conversational_memory.get_memory_stats()
        
        stats_text = f"""🧠 Conversational Memory Statistics

📊 Basic Stats:
• Total conversation turns: {memory_stats['total_turns']}
• User since: {memory_stats['user_since'][:10]}
• Last interaction: {memory_stats['last_interaction'][:10]}
• Summary turn count: {memory_stats['summary_turn_count']}

🎯 User Profile:
• Preferred consensus: {memory_stats['preferred_consensus']}
• Common topics: {', '.join(memory_stats['common_topics'][:5])}

💭 Current Context:
• Main discussion topics: {', '.join(memory_stats['main_topics'][:5])}

📁 Memory Files:
• Conversation: {memory_stats['memory_files']['conversation']}
• Profile: {memory_stats['memory_files']['profile']}
• Summary: {memory_stats['memory_files']['summary']}

🔄 Memory Features:
• Persistent across sessions: ✅
• Shared across all models: ✅
• Intelligent summarization: ✅
• User preference learning: ✅
"""
        
        messagebox.showinfo("Memory Statistics", stats_text)
    
    def clear_memory_dialog(self):
        """Show dialog to clear conversational memory"""
        if not self.council:
            messagebox.showwarning("No Council", "Council not initialized.")
            return
        
        result = messagebox.askyesnocancel(
            "Clear Memory", 
            "What would you like to clear?\n\n"
            "• Yes: Clear conversation history but keep user profile\n"
            "• No: Clear everything including user profile\n"
            "• Cancel: Don't clear anything"
        )
        
        if result is True:  # Yes - keep profile
            self.council.conversational_memory.clear_memory(keep_profile=True)
            self.chat_history.config(state='normal')
            self.chat_history.delete(1.0, tk.END)
            self.chat_history.config(state='disabled')
            messagebox.showinfo("Memory Cleared", "Conversation history cleared. User profile kept.")
            
        elif result is False:  # No - clear everything
            self.council.conversational_memory.clear_memory(keep_profile=False)
            self.chat_history.config(state='normal')
            self.chat_history.delete(1.0, tk.END)
            self.chat_history.config(state='disabled')
            messagebox.showinfo("Memory Cleared", "All memory cleared including user profile.")
    
    def run(self):
        """Start the GUI application"""
        try:
            self.root.mainloop()
        finally:
            if self.council:
                self.council.shutdown()

def main():
    """Main entry point"""
    app = DjinnCouncilGUI()
    app.run()

if __name__ == "__main__":
    main()