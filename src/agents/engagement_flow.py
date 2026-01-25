"""LangGraph workflow for engagement orchestration."""
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from src.agents.message_personalizer import MessagePersonalizer
from src.agents.offer_writer import OfferWriter
from src.services.messaging_service import MessagingService
from src.config import CandidateStage, MessageType, Channel

class AgentState(TypedDict):
    """State definition for engagement graph."""
    candidate_id: str
    job_id: str
    candidate_name: str
    role_title: str
    current_stage: str
    action: str  # e.g., "update_stage", "send_reminder"
    message_content: Optional[str]
    channel: str
    status: str

class EngagementGraph:
    """Workflow graph for candidate engagement."""
    
    def __init__(self):
        self.message_agent = MessagePersonalizer()
        self.messaging_service = MessagingService()
        self.workflow = self._build_graph()
        
    def _build_graph(self):
        """Build the LangGraph workflow."""
        workflow = StateGraph(AgentState)
        
        # Define nodes
        workflow.add_node("draft_message", self.draft_message)
        workflow.add_node("send_message", self.send_message)
        
        # Define edges
        workflow.set_entry_point("draft_message")
        workflow.add_edge("draft_message", "send_message")
        workflow.add_edge("send_message", END)
        
        return workflow.compile()
    
    async def draft_message(self, state: AgentState):
        """Node: Generate content using AI."""
        print(f"🤖 Drafting message for {state['candidate_name']} ({state['action']})")
        
        content = ""
        if state["action"] == "update_stage":
            content = self.message_agent.generate_stage_update_message(
                candidate_name=state["candidate_name"],
                role_title=state["role_title"],
                new_stage=CandidateStage(state["current_stage"])
            )
        
        return {"message_content": content}
    
    async def send_message(self, state: AgentState):
        """Node: Send the message via messaging service."""
        print(f"📨 Sending to {state['candidate_id']} via {state['channel']}")
        
        await self.messaging_service.send_message(
            candidate_id=state["candidate_id"],
            message=state["message_content"],
            channel=Channel(state["channel"]),
            message_type=MessageType.STAGE_UPDATE
        )
        
        return {"status": "sent"}
        
    async def run_stage_update(
        self,
        candidate_id: str,
        candidate_name: str,
        role_title: str,
        new_stage: CandidateStage,
        channel: str = "email"
    ):
        """Run the workflow for a stage update."""
        inputs = {
            "candidate_id": candidate_id,
            "job_id": "unknown", # TODO: fetch if needed
            "candidate_name": candidate_name,
            "role_title": role_title,
            "current_stage": new_stage.value,
            "action": "update_stage",
            "message_content": None,
            "channel": channel,
            "status": "started"
        }
        
        await self.workflow.ainvoke(inputs)
