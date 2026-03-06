"""
Mulberry Phase 3 - AI Agent Module
5인 비서 군단 통합
"""

from app.agents.base import (
    BaseAgent,
    MessageBus,
    MessageType,
    AgentMessage,
    AgentCoordinator,
    get_message_bus,
    get_coordinator
)

from app.agents.sns_manager import SNSManagerAgent, get_sns_manager
from app.agents.sales_agent import SalesAgent, get_sales_agent
from app.agents.inventory_manager import InventoryManagerAgent, get_inventory_manager
from app.agents.crm_manager import CRMManagerAgent, get_crm_manager
from app.agents.strategy_advisor import StrategyAdvisorAgent, get_strategy_advisor

__all__ = [
    # Base
    "BaseAgent",
    "MessageBus",
    "MessageType",
    "AgentMessage",
    "AgentCoordinator",
    "get_message_bus",
    "get_coordinator",
    # Agents
    "SNSManagerAgent",
    "get_sns_manager",
    "SalesAgent",
    "get_sales_agent",
    "InventoryManagerAgent",
    "get_inventory_manager",
    "CRMManagerAgent",
    "get_crm_manager",
    "StrategyAdvisorAgent",
    "get_strategy_advisor",
]
