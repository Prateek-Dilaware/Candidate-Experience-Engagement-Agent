"""LangGraph workflow for engagement orchestration (refactored, safe)."""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from src.agents.message_personalizer import MessagePersonalizer
from src.services.messaging_service import MessagingService
from src.config.constants import CandidateStage, MessageType, Channel
from src.db import get_supabase


class AgentState(TypedDict):
    """State definition for engagement graph."""
    candidate_id: str
    job_id: str
    candidate_name: str
    role_title: str
    current_stage: str
    action: str
    message_content: Optional[str]
    channel: str
    status: str


class EngagementGraph:
    """Workflow graph for candidate engagement."""

    def __init__(self):
        self.message_agent = MessagePersonalizer()
        self.messaging_service = MessagingService()
        self.workflow = self._build_graph()
        self.supabase = get_supabase()

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("draft_message", self.draft_message)
        workflow.add_node("send_message", self.send_message)

        workflow.set_entry_point("draft_message")
        workflow.add_edge("draft_message", "send_message")
        workflow.add_edge("send_message", END)

        return workflow.compile()

    async def draft_message(self, state: AgentState):
        """Generate content using AI (channel-aware)."""
        print(f"🤖 Drafting message for {state['candidate_name']} ({state['action']})")

        content = ""

        if state["action"] == "update_stage":
            content = self.message_agent.generate_stage_update_message(
                candidate_name=state["candidate_name"],
                role_title=state["role_title"],
                new_stage=CandidateStage(state["current_stage"]),
                channel=Channel(state["channel"])
            )

        return {"message_content": content}

    async def send_message(self, state: AgentState):
        """Send the message via MessagingService."""
        print(f"📨 Sending to {state['candidate_id']} via {state['channel']}")

        await self.messaging_service.send_message(
            candidate_id=state["candidate_id"],
            job_id=state["job_id"],
            stage=CandidateStage(state["current_stage"]),
            message=state["message_content"],
            preferred_channel=state["channel"],
            message_type=MessageType.STAGE_UPDATE
        )

        return {"status": "sent"}

    async def run_stage_update(
        self,
        candidate_id: str,
        job_id: str,
        new_stage: CandidateStage,
        channel: Channel = Channel.EMAIL
    ):
        """Run the workflow for a stage update."""

        # Fetch candidate name
        profile_resp = (
            self.supabase
            .table("candidate_profiles")
            .select("full_name")
            .eq("candidate_id", candidate_id)
            .execute()
        )
        candidate_name = profile_resp.data[0]["full_name"] if profile_resp.data else "Candidate"

        # Fetch job title
        job_resp = (
            self.supabase
            .table("jobs")
            .select("title")
            .eq("job_id", job_id)
            .execute()
        )
        role_title = job_resp.data[0]["title"] if job_resp.data else "Software Engineer"

        inputs = {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "candidate_name": candidate_name,
            "role_title": role_title,
            "current_stage": new_stage.value,
            "action": "update_stage",
            "message_content": None,
            "channel": channel.value,
            "status": "started"
        }

        await self.workflow.ainvoke(inputs)
