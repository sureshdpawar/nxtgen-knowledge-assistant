from enum import Enum


class UserRole(str, Enum):
    SUPERADMIN = "SUPERADMIN"
    ADMIN = "ADMIN"
    USER = "USER"


class TenantStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    SUSPENDED = "SUSPENDED"


class TenantPlan(str, Enum):
    FREE = "FREE"
    PRO = "PRO"
    ENTERPRISE = "ENTERPRISE"


class DocumentStatus(str, Enum):
    UPLOADED = "UPLOADED"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


class ConversationStatus(str, Enum):
    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    
class KnowledgeBaseStatus(str, Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class KnowledgeBaseVisibility(str, Enum):
    PRIVATE = "PRIVATE"
    SHARED = "SHARED"
    
class KnowledgeSourceType(str, Enum):
    UPLOAD = "UPLOAD"
    WEBSITE = "WEBSITE"
    SHAREPOINT = "SHAREPOINT"
    CONFLUENCE = "CONFLUENCE"
    GITHUB = "GITHUB"
    GOOGLE_DRIVE = "GOOGLE_DRIVE"
    ONEDRIVE = "ONEDRIVE"
    S3 = "S3"


class KnowledgeSourceStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    ERROR = "ERROR"    
    
class DocumentStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"
    
class LLMProvider(Enum):
    OPENAI = "OPENAI"
    AZURE_OPENAI = "AZURE_OPENAI"
    ANTHROPIC = "ANTHROPIC"
    GOOGLE = "GOOGLE"
    VLLM = "VLLM"
    OLLAMA = "OLLAMA"
    
class KnowledgeBaseAccessLevel(str, Enum):
    READ = "READ"
    MANAGE = "MANAGE"    
    
class AgentStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    
class AgentRunStatus(str, Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class AgentRunStepType(str, Enum):
    LLM = "LLM"
    TOOL = "TOOL"


class AgentRunStepStatus(str, Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"    