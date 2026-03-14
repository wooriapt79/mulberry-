"""
Mulberry WiFi Sensing MVP
-------------------------
Consolidated runnable MVP — merges Colab advances + local bug fixes.

Reviewed & fixed by Nguyen Trang (2026-03-14):
  - identify_person: best-match logic (was: first-match bug)
  - compare_patterns: length mismatch warning added
  - CSIAnalyzer/CSICollector: frame logic unified (seconds * 5, max 50)
  - MHCMotionDetector: thresholds updated (fall=0.85, abnormal=0.60)
  - is_speech_present: VAD threshold 0.20 → 0.40 (stub false-positive fix)
  - MHCMultiModalModel.predict: count-based averaging (was: /2 always)
  - MHCApiError: custom exception for API failures
  - MHCClient: env-var API key, Bearer auth, retry + exponential backoff
  - preprocess_person_identified_data: SHA-256 biometric hashing (K-PIPA)
  - preprocess_motion_event_data: ISO-8601 event payload builder
  - MHCMultiModalSensor / WhoFiIdentifier: mhc_client dependency injection
  - logging module replaces all bare print()
  - __all__ export list added

Run:
    python mulberry_wifi_sensing_mvp.py

Production dependencies (commented — not needed for MVP stub):
    pip install numpy scipy pyaudio librosa soundfile torch requests
"""

from __future__ import annotations

import datetime
import hashlib
import json
import logging
import os
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# ── optional: requests (needed for real MHCClient HTTP calls) ──────────────
try:
    import requests as _requests
    _REQUESTS_AVAILABLE = True
except ImportError:
    _requests = None
    _REQUESTS_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

__all__ = [
    # exceptions
    "MHCApiError",
    # data classes
    "DetectionResult",
    "EventStorage",
    # helpers
    "get_current_iso_timestamp",
    "preprocess_motion_event_data",
    "preprocess_person_identified_data",
    # hardware stubs
    "CSIReader",
    "CSIAnalyzer",
    "CSICollector",
    "LEDIndicator",
    # motion detection
    "MHCMotionDetector",
    "MHCMotionModel",
    "MHCMultiModalModel",
    "load_mhc_model",
    # API client
    "MHCClient",
    # sensors / modules
    "WiFiSensingModule",
    "WiFiSensingPrivacy",
    "MHCMultiModalSensor",
    # identification & fall detection
    "WhoFiIdentifier",
    "WiFiFallDetector",
]


# ══════════════════════════════════════════════════════════════════════════════
# 1. EXCEPTIONS
# ══════════════════════════════════════════════════════════════════════════════

class MHCApiError(Exception):
    """mHC API 호출 중 발생한 오류를 나타내는 사용자 정의 예외."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        original_exception: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.original_exception = original_exception


# ══════════════════════════════════════════════════════════════════════════════
# 2. DATA CLASSES
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class DetectionResult:
    label: str
    confidence: float


@dataclass
class EventStorage:
    """인메모리 이벤트 저장소 (배포 시 DB/메시지큐로 교체)."""
    events: List[dict] = field(default_factory=list)

    def add(self, payload: dict) -> None:
        self.events.append(payload)
        logger.debug(f"[EventStorage] stored event type={payload.get('eventType')}")

    def get_all(self) -> List[dict]:
        return list(self.events)

    def clear(self) -> None:
        self.events.clear()


# ══════════════════════════════════════════════════════════════════════════════
# 3. HELPER FUNCTIONS
# ══════════════════════════════════════════════════════════════════════════════

def get_current_iso_timestamp() -> str:
    """현재 시각을 ISO 8601 UTC 문자열로 반환."""
    return datetime.datetime.now(datetime.timezone.utc).isoformat() + "Z"


def preprocess_motion_event_data(
    result: DetectionResult,
    person_id: Optional[str] = None,
    location: str = "unknown",
    duration: Optional[int] = None,
) -> dict:
    """낙상 감지 / 비정상 움직임 이벤트를 위한 JSON 페이로드 생성."""
    event_type_map = {
        "fall_detected": "FallDetectionAlert",
        "abnormal_movement": "AbnormalMovementRecord",
        "normal": "NormalMovementRecord",
    }
    payload: dict = {
        "eventType": event_type_map.get(result.label, "UnknownEvent"),
        "timestamp": get_current_iso_timestamp(),
        "confidence": result.confidence,
        "location": location,
    }
    if person_id:
        payload["personId"] = person_id
    if duration is not None:
        payload["durationSeconds"] = duration
    return payload


def preprocess_person_identified_data(
    person_id: str,
    signature: List[float],
    device_name: str = "WiFi_Sensor_Module",
) -> dict:
    """개인 식별 이벤트를 위한 JSON 페이로드 생성.

    [SECURITY] biometricSignature는 SHA-256 해싱 후 전송 (K-PIPA 준수).
    원본 서명은 페이로드에 포함되지 않습니다.
    """
    signature_str = json.dumps(signature, sort_keys=True)
    hashed_signature = hashlib.sha256(signature_str.encode("utf-8")).hexdigest()
    return {
        "eventType": "PersonIdentificationEvent",
        "timestamp": get_current_iso_timestamp(),
        "personId": person_id,
        "deviceName": device_name,
        "hashedBiometricSignature": hashed_signature,
        # "biometricSignature": signature  ← 원본 전송 금지
    }


# ══════════════════════════════════════════════════════════════════════════════
# 4. HARDWARE STUBS
# ══════════════════════════════════════════════════════════════════════════════

class CSIReader:
    """하드웨어 CSI 수집기 stub (wlan0 인터페이스).
    배포 시 nexmon-csi 기반 실제 CSI 추출 코드로 교체.
    """

    def __init__(self, interface: str = "wlan0") -> None:
        self.interface = interface

    def read_csi(self) -> List[float]:
        """64-subcarrier CSI 프레임 1개 반환."""
        return [random.random() for _ in range(64)]


class CSIAnalyzer:
    """장시간 CSI 수집 분석기 (WhoFi용).
    [FIX] CSICollector와 프레임 계산 방식 통일: seconds * 5, max 50.
    """

    def collect_for_duration(self, seconds: int) -> List[List[float]]:
        frames = max(1, min(seconds * 5, 50))
        return [[random.random() for _ in range(64)] for _ in range(frames)]


class CSICollector:
    """단기 CSI 수집기 (낙상 감지용)."""

    def collect(self, duration: int = 3) -> List[List[float]]:
        frames = max(1, duration * 5)
        return [[random.random() for _ in range(64)] for _ in range(frames)]


class LEDIndicator:
    def blink_green(self) -> None:
        logger.info("[LED] blinking green")

    def off(self) -> None:
        logger.info("[LED] off")


# ══════════════════════════════════════════════════════════════════════════════
# 5. MOTION DETECTION MODELS
# ══════════════════════════════════════════════════════════════════════════════

class MHCMotionDetector:
    """단일 CSI 프레임 기반 간이 동작 감지.

    [FIX] 임계값 갱신 (Colab Cell 1 기준):
        normal:             avg <= 0.60
        abnormal_movement:  0.60 < avg <= 0.85
        fall_detected:      avg > 0.85
    """

    def __init__(
        self,
        fall_threshold: float = 0.85,
        abnormal_threshold: float = 0.60,
    ) -> None:
        self.fall_threshold = fall_threshold
        self.abnormal_threshold = abnormal_threshold

    def analyze(self, csi_data: List[float]) -> str:
        avg = sum(csi_data) / len(csi_data) if csi_data else 0.0
        if avg > self.fall_threshold:
            return "fall_detected"
        if avg > self.abnormal_threshold:
            return "abnormal_movement"
        return "normal"


class MHCMotionModel:
    """진폭 데이터 기반 동작 분류 모델 stub."""

    def predict(self, amplitude_data: List[float]) -> DetectionResult:
        avg = sum(amplitude_data) / len(amplitude_data) if amplitude_data else 0.0
        if avg > 0.85:
            return DetectionResult(label="fall_detected", confidence=0.97)
        if avg > 0.68:
            return DetectionResult(label="abnormal_movement", confidence=0.83)
        return DetectionResult(label="normal", confidence=0.60)


class MHCMultiModalModel:
    """오디오 + CSI 멀티모달 분류 모델 stub.

    [FIX] count 기반 평균 계산 (단일 모달리티 시 /2 오류 방지).
    """

    def predict(self, aligned_data: Dict[str, List[float]]) -> str:
        audio = aligned_data.get("audio", [])
        csi = aligned_data.get("csi", [])
        signal = 0.0
        count = 0
        if audio:
            signal += sum(audio) / len(audio)
            count += 1
        if csi:
            signal += sum(csi) / len(csi)
            count += 1
        if count:
            signal /= count
        if signal > 0.82:
            return "fall_detected"
        if signal > 0.66:
            return "abnormal_movement"
        return "normal"


def load_mhc_model() -> MHCMultiModalModel:
    return MHCMultiModalModel()


# ══════════════════════════════════════════════════════════════════════════════
# 6. mHC API CLIENT
# ══════════════════════════════════════════════════════════════════════════════

class MHCClient:
    """mHC 시스템 API 클라이언트.

    Features:
    - API Key는 환경 변수에서 로드 (보안)
    - Bearer Token 인증
    - 지수 백오프 재시도 (max_retries=3, 5xx 오류 시)
    - MVP 모드: requests 미설치 시 stub 응답 반환
    """

    def __init__(
        self,
        base_url: str = "https://api.mhcsystem.com/v1",
        api_key_env_var: str = "MHC_API_KEY",
        api_key: Optional[str] = None,
        mock_mode: bool = False,
    ) -> None:
        self.base_url = base_url
        self._mock_mode = mock_mode
        # api_key 직접 전달 > 환경변수 > 기본 mock 값
        self.api_key = api_key or os.getenv(api_key_env_var, "mock_api_key")
        if self.api_key == "mock_api_key":
            logger.warning(
                f"[MHCClient] API key not set. "
                f"Set '{api_key_env_var}' env var for production."
            )
        logger.info(
            f"[MHCClient] initialized base_url={self.base_url}"
            f"{' (mock_mode)' if mock_mode else ''}"
        )

    def _send_request(
        self,
        endpoint: str,
        payload: dict,
        max_retries: int = 3,
        backoff_factor: float = 1.0,
    ) -> dict:
        """HTTP POST with retry + exponential backoff.
        MVP stub: requests 미설치 또는 mock_mode=True 시 stub 응답 반환.
        """
        if self._mock_mode or not _REQUESTS_AVAILABLE:
            logger.info(
                f"[MHCClient][STUB] POST {endpoint} "
                f"payload_type={payload.get('eventType')} → mock OK"
            )
            return {"status": "ok_stub", "eventType": payload.get("eventType")}

        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        for attempt in range(max_retries):
            logger.info(
                f"[MHCClient] attempt {attempt + 1}/{max_retries} → {url}"
            )
            try:
                response = _requests.post(
                    url, headers=headers, json=payload, timeout=10
                )
                response.raise_for_status()
                return response.json()

            except _requests.exceptions.HTTPError as exc:
                status_code = (
                    exc.response.status_code if exc.response is not None else None
                )
                logger.error(f"[MHCClient] HTTP {status_code} for {url}: {exc}")
                if status_code in (500, 502, 503, 504) and attempt < max_retries - 1:
                    sleep_time = backoff_factor * (2 ** attempt)
                    logger.info(f"[MHCClient] retry in {sleep_time:.1f}s …")
                    time.sleep(sleep_time)
                else:
                    raise MHCApiError(
                        f"HTTP error {status_code}", status_code, exc
                    )

            except _requests.exceptions.RequestException as exc:
                logger.error(f"[MHCClient] network error: {exc}")
                if attempt < max_retries - 1:
                    sleep_time = backoff_factor * (2 ** attempt)
                    logger.info(f"[MHCClient] retry in {sleep_time:.1f}s …")
                    time.sleep(sleep_time)
                else:
                    raise MHCApiError(
                        "Network error after retries", original_exception=exc
                    )

            except Exception as exc:
                logger.error(f"[MHCClient] unexpected error: {exc}")
                raise MHCApiError(
                    "Unexpected error", original_exception=exc
                )

        raise MHCApiError(f"Failed after {max_retries} attempts")

    def send_fall_detection_alert(self, payload: dict) -> dict:
        return self._send_request("/events/fall-detection", payload)

    def send_abnormal_movement_log(self, payload: dict) -> dict:
        return self._send_request("/events/abnormal-movement", payload)

    def send_person_identification_info(self, payload: dict) -> dict:
        return self._send_request("/users/identification", payload)


# ══════════════════════════════════════════════════════════════════════════════
# 7. PRIVACY / CONSENT MODULE
# ══════════════════════════════════════════════════════════════════════════════

class WiFiSensingPrivacy:
    def __init__(self) -> None:
        self.user_consent = False
        self.collection_active = False
        self.led = LEDIndicator()

    def tts_speak(self, message: str) -> None:
        logger.info(f"[TTS] {message}")

    def request_consent(self) -> None:
        self.tts_speak("움직임 감지 기능을 켤까요? 언제든지 끌 수 있어요.")
        self.user_consent = True
        logger.info("[Privacy] user_consent=True")

    def toggle_collection(self, voice_command: str) -> None:
        if "움직임 감지 켜줘" in voice_command:
            self.collection_active = True
            self.led.blink_green()
            logger.info("[Privacy] collection_active=True")
        elif "움직임 감지 꺼줘" in voice_command:
            self.collection_active = False
            self.led.off()
            logger.info("[Privacy] collection_active=False")


# ══════════════════════════════════════════════════════════════════════════════
# 8. WIFI SENSING MODULE (기본 단일 모달리티)
# ══════════════════════════════════════════════════════════════════════════════

class WiFiSensingModule:
    def __init__(self, interface: str = "wlan0") -> None:
        self.csi_extractor = CSIReader(interface)
        self.motion_detector = MHCMotionDetector()

    def alert_emergency(self) -> None:
        logger.warning("[EMERGENCY] Fall detected. Alert triggered.")

    def run_once(self) -> str:
        csi_data = self.csi_extractor.read_csi()
        motion_status = self.motion_detector.analyze(csi_data)
        logger.info(f"[WiFiSensingModule] motion_status={motion_status}")
        if motion_status == "fall_detected":
            self.alert_emergency()
        return motion_status

    def run(self, iterations: int = 5, sleep_sec: float = 0.2) -> None:
        for _ in range(iterations):
            self.run_once()
            time.sleep(sleep_sec)


# ══════════════════════════════════════════════════════════════════════════════
# 9. MULTIMODAL SENSOR (오디오 + CSI)
# ══════════════════════════════════════════════════════════════════════════════

class MHCMultiModalSensor:
    """오디오 + CSI 멀티모달 센서.

    Args:
        mhc_client: MHCClient 인스턴스 (선택적). 제공 시 이벤트 자동 전송.
    """

    def __init__(self, mhc_client: Optional[MHCClient] = None) -> None:
        self.mhc_model = load_mhc_model()
        self.mhc_client = mhc_client
        self.event_storage = EventStorage()

    def tts_speak(self, message: str) -> None:
        logger.info(f"[TTS] {message}")

    def trigger_emergency(self) -> None:
        logger.warning("[EMERGENCY] Multimodal emergency trigger")

    def is_speech_present(self, audio_stream: List[float]) -> bool:
        """오디오 스트림에 음성 존재 여부 판단.

        [FIX] 임계값 0.20 → 0.40:
            stub 랜덤 데이터 평균 ~0.5에서 0.20 기준은 항상 True → 오탐 다수 발생.
            배포 시 실제 VAD(Voice Activity Detection) 모델로 교체 필요.
        """
        return bool(audio_stream) and (
            sum(audio_stream) / len(audio_stream)
        ) > 0.40

    def align_modalities(
        self,
        audio_stream: List[float],
        csi_stream: List[float],
    ) -> Dict[str, List[float]]:
        return {"audio": audio_stream, "csi": csi_stream}

    def analyze(
        self,
        audio_stream: List[float],
        csi_stream: List[float],
        person_id: Optional[str] = None,
        location: str = "unknown",
    ) -> str:
        aligned_data = self.align_modalities(audio_stream, csi_stream)
        situation = self.mhc_model.predict(aligned_data)

        if situation == "fall_detected":
            if self.is_speech_present(audio_stream):
                self.trigger_emergency()
            if self.mhc_client:
                payload = preprocess_motion_event_data(
                    DetectionResult("fall_detected", 0.97),
                    person_id=person_id,
                    location=location,
                )
                payload["alertTriggered"] = True
                try:
                    self.mhc_client.send_fall_detection_alert(payload)
                    self.event_storage.add(payload)
                except MHCApiError as exc:
                    logger.error(f"[MHCMultiModalSensor] API send failed: {exc}")

        elif situation == "abnormal_movement":
            self.tts_speak("괜찮으세요?")
            if self.mhc_client:
                payload = preprocess_motion_event_data(
                    DetectionResult("abnormal_movement", 0.83),
                    person_id=person_id,
                    location=location,
                )
                try:
                    self.mhc_client.send_abnormal_movement_log(payload)
                    self.event_storage.add(payload)
                except MHCApiError as exc:
                    logger.error(f"[MHCMultiModalSensor] API send failed: {exc}")

        logger.info(f"[MHCMultiModalSensor] situation={situation}")
        return situation


# ══════════════════════════════════════════════════════════════════════════════
# 10. WHOFI IDENTIFIER — WiFi CSI 기반 개인 식별
# ══════════════════════════════════════════════════════════════════════════════

class WhoFiIdentifier:
    """WiFi CSI 기반 개인 식별 모듈.

    Args:
        mhc_client: MHCClient 인스턴스 (선택적). 제공 시 식별 이벤트 자동 전송.
    """

    def __init__(self, mhc_client: Optional[MHCClient] = None) -> None:
        self.csi_analyzer = CSIAnalyzer()
        self.body_signature_db: Dict[str, List[float]] = {}
        self.mhc_client = mhc_client
        self.event_storage = EventStorage()

    def extract_biometric_features(
        self, csi_patterns: List[List[float]]
    ) -> List[float]:
        if not csi_patterns:
            return [0.0] * 64
        cols = len(csi_patterns[0])
        return [
            sum(frame[i] for frame in csi_patterns) / len(csi_patterns)
            for i in range(cols)
        ]

    def compare_patterns(
        self,
        realtime_csi: List[float],
        signature: List[float],
    ) -> float:
        """두 CSI 패턴 유사도 반환 (0.0 ~ 1.0).

        [FIX] 길이 불일치 시 경고 로그 추가.
        """
        if not realtime_csi or not signature:
            return 0.0
        if len(realtime_csi) != len(signature):
            logger.warning(
                f"[WhoFi] compare_patterns 길이 불일치 "
                f"(realtime={len(realtime_csi)}, signature={len(signature)}) "
                f"→ 0.0 반환"
            )
            return 0.0
        distance = (
            sum(abs(a - b) for a, b in zip(realtime_csi, signature))
            / len(signature)
        )
        return max(0.0, 1.0 - distance)

    def enroll_person(self, person_id: str, seconds: int = 5) -> None:
        csi_patterns = self.csi_analyzer.collect_for_duration(seconds)
        signature = self.extract_biometric_features(csi_patterns)
        self.body_signature_db[person_id] = signature
        logger.info(f"[WhoFi] enrolled person_id={person_id}")

        if self.mhc_client:
            payload = preprocess_person_identified_data(
                person_id=person_id,
                signature=signature,
                device_name="WiFi_Sensor_Module",
            )
            try:
                self.mhc_client.send_person_identification_info(payload)
                self.event_storage.add(payload)
            except MHCApiError as exc:
                logger.error(f"[WhoFi] API send failed: {exc}")

    def identify_person(
        self,
        realtime_csi: List[float],
        threshold: float = 0.95,
    ) -> str:
        """등록된 사람 중 가장 유사도 높은 사람 반환.

        [FIX] best-match 로직:
            이전: threshold 초과 첫 번째 매칭 즉시 반환 → 다중 등록자 오인식
            수정: 전체 스캔 후 최고 유사도 매칭 반환
        """
        best_match: str = "unknown"
        best_similarity: float = 0.0

        for person_id, signature in self.body_signature_db.items():
            similarity = self.compare_patterns(realtime_csi, signature)
            logger.info(f"[WhoFi] compare {person_id}: similarity={similarity:.3f}")
            if similarity > threshold and similarity > best_similarity:
                best_similarity = similarity
                best_match = person_id

        if best_match != "unknown":
            logger.info(
                f"[WhoFi] identified={best_match} "
                f"(best_similarity={best_similarity:.3f})"
            )
        return best_match


# ══════════════════════════════════════════════════════════════════════════════
# 11. WIFI FALL DETECTOR
# ══════════════════════════════════════════════════════════════════════════════

class WiFiFallDetector:
    def __init__(self) -> None:
        self.csi_collector = CSICollector()
        self.motion_analyzer = MHCMotionModel()

    def trigger_emergency(self) -> None:
        logger.warning("[EMERGENCY] WiFi fall detector triggered")

    def extract_amplitude(self, csi_stream: List[List[float]]) -> List[float]:
        return [sum(frame) / len(frame) for frame in csi_stream if frame]

    def detect_fall(self) -> DetectionResult:
        csi_stream = self.csi_collector.collect(duration=3)
        amplitude_data = self.extract_amplitude(csi_stream)
        result = self.motion_analyzer.predict(amplitude_data)
        logger.info(
            f"[WiFiFallDetector] result={result.label}, "
            f"confidence={result.confidence:.2f}"
        )
        if result.label == "fall_detected" and result.confidence > 0.95:
            self.trigger_emergency()
        return result


# ══════════════════════════════════════════════════════════════════════════════
# 12. DEMO
# ══════════════════════════════════════════════════════════════════════════════

def demo() -> None:
    print("\n=== 1. Privacy Control ===")
    privacy = WiFiSensingPrivacy()
    privacy.request_consent()
    privacy.toggle_collection("움직임 감지 켜줘")

    print("\n=== 2. WiFi Sensing Module ===")
    sensing = WiFiSensingModule()
    sensing.run(iterations=3, sleep_sec=0.05)

    print("\n=== 3. Multimodal Sensor (with MHCClient stub) ===")
    mhc_client = MHCClient(api_key="demo_key", mock_mode=True)
    multimodal = MHCMultiModalSensor(mhc_client=mhc_client)
    audio_stream = [random.random() for _ in range(32)]
    csi_stream = [random.random() for _ in range(64)]
    multimodal.analyze(audio_stream, csi_stream, person_id="senior_01", location="living_room")

    print("\n=== 4. WhoFi Identifier (best-match + SHA-256) ===")
    identifier = WhoFiIdentifier(mhc_client=mhc_client)
    identifier.enroll_person("senior_01")
    sample = identifier.body_signature_db["senior_01"][:]
    identified = identifier.identify_person(sample, threshold=0.80)
    print(f"[WhoFi] identified={identified}")

    print("\n=== 5. Fall Detector ===")
    fall_detector = WiFiFallDetector()
    result = fall_detector.detect_fall()
    print(f"[WiFiFallDetector] label={result.label}, confidence={result.confidence:.2f}")

    print("\n=== 6. Payload Preview ===")
    sample_result = DetectionResult("fall_detected", 0.97)
    motion_payload = preprocess_motion_event_data(
        sample_result, person_id="senior_01", location="living_room"
    )
    id_payload = preprocess_person_identified_data(
        person_id="senior_01",
        signature=sample[:8],  # 미리보기용 앞 8개 요소
    )
    print(f"[Motion payload] {json.dumps(motion_payload, ensure_ascii=False, indent=2)}")
    print(f"[ID payload keys] {list(id_payload.keys())}")
    print(f"[hashedBiometricSignature] {id_payload['hashedBiometricSignature'][:16]}…")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    demo()
