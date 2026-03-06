"""
Custom Exceptions for Advanced Skill System
Mulberry Project - CTO Koda
PM 제안 반영: 예외 처리 강화
"""

class SkillSystemException(Exception):
    """Base exception for skill system"""
    pass


# NFT Marketplace Exceptions
class InsufficientBalanceError(SkillSystemException):
    """구매자 잔액 부족"""
    def __init__(self, required: float, available: float):
        self.required = required
        self.available = available
        super().__init__(
            f"잔액 부족: 필요 {required:,.0f}원, 보유 {available:,.0f}원"
        )


class NFTSoldError(SkillSystemException):
    """이미 판매된 NFT"""
    def __init__(self, nft_id: str):
        self.nft_id = nft_id
        super().__init__(f"NFT {nft_id}는 이미 판매되었습니다")


class NFTNotFoundError(SkillSystemException):
    """NFT를 찾을 수 없음"""
    def __init__(self, nft_id: str):
        self.nft_id = nft_id
        super().__init__(f"NFT {nft_id}를 찾을 수 없습니다")


class InvalidPriceError(SkillSystemException):
    """잘못된 가격"""
    def __init__(self, price: float):
        self.price = price
        super().__init__(f"잘못된 가격: {price}")


# Skill Transfer Exceptions
class IncompatibleSkillError(SkillSystemException):
    """전이 불가능한 스킬"""
    def __init__(self, source: str, target: str):
        self.source = source
        self.target = target
        super().__init__(
            f"스킬 전이 불가: {source} → {target}"
        )


class InsufficientSkillLevelError(SkillSystemException):
    """스킬 레벨 부족"""
    def __init__(self, required: int, current: int):
        self.required = required
        self.current = current
        super().__init__(
            f"스킬 레벨 부족: 필요 Lv{required}, 현재 Lv{current}"
        )


# Collaboration Exceptions
class CollaborationNotFoundError(SkillSystemException):
    """협업 프로젝트를 찾을 수 없음"""
    def __init__(self, collab_id: str):
        self.collab_id = collab_id
        super().__init__(f"협업 {collab_id}를 찾을 수 없습니다")


class AgentNotInCollaborationError(SkillSystemException):
    """협업에 참여하지 않은 Agent"""
    def __init__(self, agent_id: str, collab_id: str):
        self.agent_id = agent_id
        self.collab_id = collab_id
        super().__init__(
            f"Agent {agent_id}는 협업 {collab_id}에 참여하지 않았습니다"
        )


# Competition Exceptions
class ChallengeNotFoundError(SkillSystemException):
    """챌린지를 찾을 수 없음"""
    def __init__(self, challenge_id: str):
        self.challenge_id = challenge_id
        super().__init__(f"챌린지 {challenge_id}를 찾을 수 없습니다")


class ChallengeClosedError(SkillSystemException):
    """참가 마감된 챌린지"""
    def __init__(self, challenge_id: str):
        self.challenge_id = challenge_id
        super().__init__(f"챌린지 {challenge_id}는 참가 마감되었습니다")


# Concurrent Access Exceptions
class ConcurrentModificationError(SkillSystemException):
    """동시 수정 충돌"""
    def __init__(self, entity_type: str, entity_id: str):
        self.entity_type = entity_type
        self.entity_id = entity_id
        super().__init__(
            f"{entity_type} {entity_id}가 다른 프로세스에 의해 수정되었습니다. 재시도하세요."
        )


class LockAcquisitionError(SkillSystemException):
    """락 획득 실패"""
    def __init__(self, resource: str, timeout: int):
        self.resource = resource
        self.timeout = timeout
        super().__init__(
            f"리소스 {resource}에 대한 락을 {timeout}초 내에 획득하지 못했습니다"
        )
