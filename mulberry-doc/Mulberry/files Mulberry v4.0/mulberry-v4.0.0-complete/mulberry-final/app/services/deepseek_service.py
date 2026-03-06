"""
Mulberry Phase 2 - DeepSeek-R1 On-Device Service
8GB RAM 라즈베리파이에서 사투리→표준어 변환 온디바이스 추론
Quantization (4-bit) 최적화
"""

import asyncio
import json
import time
import wave
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
from loguru import logger

# llama-cpp-python (4-bit quantization 지원)
try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ llama-cpp-python not available")
    LLAMA_CPP_AVAILABLE = False

# Whisper (음성 → 텍스트)
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ whisper not available")
    WHISPER_AVAILABLE = False


@dataclass
class VoiceOrderResult:
    """음성 주문 처리 결과"""
    success: bool
    transcription: str
    dialect: str
    standard_korean: str
    items: List[Dict[str, Any]]
    voice_features: Dict[str, Any]
    inference_time_ms: float
    emergency_level: int = 0


class DeepSeekService:
    """
    DeepSeek-R1 온디바이스 추론 서비스
    - 4-bit Quantization으로 8GB RAM에서 동작
    - 사투리 → 표준어 변환
    - 주문 정보 추출
    - 0.2초 이내 추론 목표
    """
    
    def __init__(self):
        """DeepSeek-R1 모델 초기화"""
        
        # 모델 경로 (4-bit quantized GGUF)
        self.model_path = "/opt/mulberry/models/deepseek-r1-distill-qwen-7b-q4_k_m.gguf"
        
        # Whisper 경량 모델 (음성 인식)
        self.whisper_model_size = "tiny"  # tiny, base, small (8GB RAM에서는 tiny/base 권장)
        
        # 모델 인스턴스
        self.llm: Optional[Llama] = None
        self.whisper_model = None
        
        # 사투리 데이터베이스 (오프라인 캐시)
        self.dialect_db = self._load_dialect_database()
        
        # 성능 측정
        self.inference_times = []
        
        if LLAMA_CPP_AVAILABLE:
            self._load_deepseek_model()
        
        if WHISPER_AVAILABLE:
            self._load_whisper_model()
        
        logger.info("✅ DeepSeek on-device service initialized")
    
    def _load_deepseek_model(self):
        """
        DeepSeek-R1 모델 로드 (4-bit Quantization)
        
        메모리 최적화:
        - n_ctx: 컨텍스트 길이 (짧게 = 메모리 절약)
        - n_batch: 배치 크기
        - n_threads: CPU 스레드 수
        - use_mlock: 메모리 고정 (스왑 방지)
        """
        try:
            if not Path(self.model_path).exists():
                logger.error(f"❌ Model not found: {self.model_path}")
                logger.info("📥 Download model from: https://huggingface.co/deepseek-ai/DeepSeek-R1-Distill-Qwen-7B-GGUF")
                return
            
            logger.info(f"🔄 Loading DeepSeek-R1 model from {self.model_path}...")
            
            start_time = time.time()
            
            # llama.cpp 모델 로드 (8GB RAM 최적화)
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=512,  # 컨텍스트 길이 512 (짧은 대화에 충분)
                n_batch=256,  # 배치 크기
                n_threads=4,  # Raspberry Pi 5는 4코어
                n_gpu_layers=0,  # CPU only (RPi에 GPU 가속 없음)
                use_mlock=True,  # 메모리 고정 (스왑 방지)
                verbose=False
            )
            
            load_time = time.time() - start_time
            
            logger.info(f"✅ DeepSeek-R1 loaded in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to load DeepSeek model: {str(e)}")
    
    def _load_whisper_model(self):
        """
        Whisper 모델 로드 (음성 → 텍스트)
        
        모델 크기:
        - tiny: 39M params, ~1GB RAM (가장 빠름)
        - base: 74M params, ~1.5GB RAM
        - small: 244M params, ~2.5GB RAM
        """
        try:
            logger.info(f"🔄 Loading Whisper ({self.whisper_model_size}) model...")
            
            start_time = time.time()
            
            self.whisper_model = whisper.load_model(
                self.whisper_model_size,
                device="cpu"  # Raspberry Pi는 CPU only
            )
            
            load_time = time.time() - start_time
            
            logger.info(f"✅ Whisper loaded in {load_time:.2f}s")
            
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper: {str(e)}")
    
    def _load_dialect_database(self) -> Dict[str, Dict[str, str]]:
        """
        사투리 데이터베이스 로드 (오프라인 캐시)
        
        🆕 인제군 현장 최적화:
        - 실제 어르신 사투리 패턴 반영
        - 가격 문의, 취소, 배송 일정 등 실전 매핑
        - 목표: 인식률 98% 달성
        """
        return {
            # ============================================
            # 강원도 (인제군 중심)
            # ============================================
            "강원도": {
                # 기본 어미
                "~감": "~습니다",
                "~제": "~지요",
                "~게": "~요",
                "~슈": "~죠",
                
                # 가격 문의 (🆕 현장 최적화)
                "얼매고": "얼마예요",
                "얼마고": "얼마예요",
                "이거 얼매": "이것 얼마",
                "값이 얼매": "가격이 얼마",
                "돈이 얼매": "돈이 얼마",
                
                # 주문/구매 의사
                "살라요": "사려고요",
                "사고 싶슈": "사고 싶어요",
                "주세요": "주세요",
                "다오": "주세요",
                
                # 수량 표현
                "대따": "많이",
                "고마": "그만",
                "요만큼": "이만큼",
                "이만치": "이만큼",
                "한 스무개": "약 20개",
                
                # 긍정/부정
                "그려": "그래요",
                "아니유": "아니에요",
                "맞슈": "맞아요",
                
                # 취소/종료 (🆕 현장 최적화)
                "고마 대따": "그만할게요",
                "안 살래": "안 살게요",
                "됐슈": "됐어요",
                "필요 없슈": "필요 없어요",
                
                # 배송 일정 (🆕 현장 최적화)
                "내일 가다 주나": "내일 가져다줄 수 있나요",
                "언제 오나": "언제 오나요",
                "빨리 오나": "빨리 오나요",
                "오늘 되나": "오늘 되나요",
                "급한디": "급해요",
                
                # 상태/품질
                "싱싱한 거": "신선한 것",
                "좋은 거": "좋은 것",
                "큰 거": "큰 것",
                "잘 익은 거": "잘 익은 것",
                
                # 확인/문의
                "맞나": "맞나요",
                "그런가": "그런가요",
                "있나": "있나요",
                "되나": "되나요",
            },
            
            # ============================================
            # 경상도 (인접 지역)
            # ============================================
            "경상도": {
                # 기본 어미
                "~카노": "~인가요",
                "~노": "~네요",
                "~데이": "~입니다",
                "심더": "합니다",
                "~능교": "~는군요",
                "머시마": "무엇입니까",
                "~이라": "~입니다",
                
                # 가격 문의
                "얼마고": "얼마예요",
                "이거 얼마꼬": "이것 얼마예요",
                
                # 주문
                "주이소": "주세요",
                "사 갈끼다": "사 갈게요",
                
                # 수량
                "많이": "많이",
                "조금": "조금",
                
                # 배송
                "가다 주나": "가져다주나요",
                "언제 오노": "언제 오나요",
                
                # 취소
                "안 되겠다": "안 되겠어요",
                "그만 할끼다": "그만할게요",
            },
            
            # ============================================
            # 전라도
            # ============================================
            "전라도": {
                "~잉": "~이에요",
                "~당께": "~니까",
                "~라우": "~입니다",
                "~제": "~지요",
                "~게": "~요",
                "~소": "~습니다",
                
                # 가격
                "얼마여": "얼마예요",
                "값이 얼매여": "가격이 얼마예요",
                
                # 주문
                "주시소": "주세요",
                "사불께": "살게요",
                
                # 배송
                "가다주소": "가져다주세요",
            },
            
            # ============================================
            # 충청도
            # ============================================
            "충청도": {
                "~유": "~요",
                "~구먼유": "~군요",
                "~지유": "~지요",
                "~당께유": "~니까요",
                
                # 가격
                "얼마유": "얼마예요",
                
                # 주문
                "주이소": "주세요",
            },
            
            # ============================================
            # 제주도
            # ============================================
            "제주도": {
                "~우다": "~입니다",
                "~수과": "~습니까",
                "~게": "~요",
                "~주": "~지요",
            },
            
            # ============================================
            # 🆕 특수 패턴 (의도 추출용)
            # ============================================
            "_intent_patterns": {
                # 가격 문의 패턴
                "price_inquiry": [
                    "얼매", "얼마", "값", "가격", "돈", "비싸", "싸"
                ],
                
                # 주문 의사 패턴
                "order_intent": [
                    "살래", "사고 싶", "주세요", "다오", "주이소", "주소"
                ],
                
                # 취소 의사 패턴
                "cancel_intent": [
                    "고마", "그만", "안 살", "안 돼", "필요 없", "됐"
                ],
                
                # 배송 문의 패턴
                "delivery_inquiry": [
                    "언제", "내일", "오늘", "빨리", "급", "가다 주", "배달"
                ],
                
                # 품질 문의 패턴
                "quality_inquiry": [
                    "싱싱", "신선", "좋은", "큰", "작은", "익은", "상태"
                ],
                
                # 재고 문의 패턴
                "stock_inquiry": [
                    "있나", "있어", "남았", "팔아"
                ],
            }
        }
    
    def _detect_intent(self, text: str) -> Optional[str]:
        """
        사투리 텍스트에서 의도(Intent) 추출
        
        🆕 현장 최적화:
        - 가격 문의, 주문, 취소, 배송 등 의도 파악
        - DeepSeek 추론 전 빠른 1차 필터링
        
        Args:
            text: 사투리 텍스트
            
        Returns:
            str: Intent (price_inquiry, order_intent, etc.) or None
        """
        text_lower = text.lower()
        
        intent_patterns = self.dialect_db.get("_intent_patterns", {})
        
        # 각 의도 패턴 매칭
        intent_scores = {}
        
        for intent, keywords in intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                intent_scores[intent] = score
        
        # 가장 높은 점수의 의도 반환
        if intent_scores:
            detected_intent = max(intent_scores, key=intent_scores.get)
            logger.info(f"🎯 Intent detected: {detected_intent} (confidence: {intent_scores[detected_intent]})")
            return detected_intent
        
        return None
    
    async def process_voice_order(self, audio_file: str) -> VoiceOrderResult:
        """
        음성 주문 전체 처리 파이프라인
        
        1. Whisper: 음성 → 텍스트
        2. 사투리 감지
        3. 🆕 Intent 감지 (가격 문의, 주문, 취소 등)
        4. DeepSeek-R1: 사투리 → 표준어 + 주문 추출
        5. 음성 특징 분석 (Emergency Level)
        
        Args:
            audio_file: WAV 오디오 파일 경로
            
        Returns:
            VoiceOrderResult: 처리 결과
        """
        try:
            total_start = time.time()
            
            # 1. 음성 → 텍스트 (Whisper)
            transcription, voice_features = await self._transcribe_audio(audio_file)
            
            if not transcription:
                return VoiceOrderResult(
                    success=False,
                    transcription="",
                    dialect="unknown",
                    standard_korean="",
                    items=[],
                    voice_features={},
                    inference_time_ms=0
                )
            
            # 2. 사투리 감지
            dialect = self._detect_dialect(transcription)
            
            # 🆕 3. Intent 감지 (현장 최적화)
            intent = self._detect_intent(transcription)
            
            # Intent에 따른 빠른 처리
            if intent == "cancel_intent":
                # 취소 의도 → 주문 없이 종료
                logger.info("🚫 Cancel intent detected. Ending order process.")
                return VoiceOrderResult(
                    success=True,
                    transcription=transcription,
                    dialect=dialect,
                    standard_korean="주문을 취소하셨습니다.",
                    items=[],
                    voice_features=voice_features,
                    inference_time_ms=(time.time() - total_start) * 1000,
                    emergency_level=0
                )
            
            elif intent == "price_inquiry":
                # 가격 문의만 → 가격 정보 제공 (주문 없음)
                logger.info("💰 Price inquiry detected.")
                # 실제로는 상품 가격 조회 후 반환
            
            # 4. DeepSeek-R1 추론
            if self.llm:
                # AI 추론으로 사투리 변환 + 주문 추출
                standard_korean, items = await self._deepseek_inference(
                    transcription,
                    dialect,
                    intent=intent  # 🆕 Intent 전달
                )
            else:
                # Fallback: 룰 기반 변환
                standard_korean = self._rule_based_translation(transcription, dialect)
                items = self._extract_order_items(standard_korean)
            
            # 5. Emergency Level 감지
            emergency_level = self._calculate_emergency_level(
                transcription,
                voice_features
            )
            
            total_time = (time.time() - total_start) * 1000  # ms
            
            self.inference_times.append(total_time)
            
            logger.info(f"✅ Voice order processed in {total_time:.1f}ms (Target: <200ms)")
            
            if total_time > 200:
                logger.warning(f"⚠️ Inference time exceeded target: {total_time:.1f}ms > 200ms")
            
            return VoiceOrderResult(
                success=True,
                transcription=transcription,
                dialect=dialect,
                standard_korean=standard_korean,
                items=items,
                voice_features=voice_features,
                inference_time_ms=total_time,
                emergency_level=emergency_level
            )
            
        except Exception as e:
            logger.error(f"❌ Voice order processing error: {str(e)}")
            return VoiceOrderResult(
                success=False,
                transcription="",
                dialect="unknown",
                standard_korean="",
                items=[],
                voice_features={},
                inference_time_ms=0
            )
    
    async def _transcribe_audio(self, audio_file: str) -> Tuple[str, Dict[str, Any]]:
        """
        음성 → 텍스트 변환 (Whisper)
        
        Args:
            audio_file: 오디오 파일 경로
            
        Returns:
            tuple: (텍스트, 음성 특징)
        """
        try:
            if not self.whisper_model:
                logger.error("❌ Whisper model not loaded")
                return "", {}
            
            logger.info(f"🎙️ Transcribing audio: {audio_file}")
            
            start_time = time.time()
            
            # Whisper 추론
            result = self.whisper_model.transcribe(
                audio_file,
                language="ko",  # 한국어
                fp16=False,  # CPU에서는 fp32
                verbose=False
            )
            
            transcription = result["text"].strip()
            
            # 음성 특징 추출
            voice_features = self._extract_voice_features(audio_file)
            
            transcribe_time = (time.time() - start_time) * 1000
            
            logger.info(f"✅ Transcription: '{transcription}' ({transcribe_time:.1f}ms)")
            
            return transcription, voice_features
            
        except Exception as e:
            logger.error(f"❌ Transcription error: {str(e)}")
            return "", {}
    
    def _extract_voice_features(self, audio_file: str) -> Dict[str, Any]:
        """
        음성 특징 추출 (Emergency Level 판단용)
        
        Args:
            audio_file: WAV 파일 경로
            
        Returns:
            dict: 음성 특징 (주파수, 음량, 속도)
        """
        try:
            with wave.open(audio_file, 'rb') as wf:
                frames = wf.readframes(wf.getnframes())
                audio_data = np.frombuffer(frames, dtype=np.int16)
                
                # 1. 평균 주파수 (Pitch) 추정
                # FFT로 주파수 분석
                fft = np.fft.fft(audio_data)
                frequencies = np.fft.fftfreq(len(fft), 1/wf.getframerate())
                magnitude = np.abs(fft)
                
                # 가장 강한 주파수 (fundamental frequency)
                peak_freq_idx = np.argmax(magnitude[:len(magnitude)//2])
                pitch_hz = abs(frequencies[peak_freq_idx])
                
                # 2. 평균 음량 (RMS)
                rms = np.sqrt(np.mean(audio_data**2))
                volume_db = 20 * np.log10(rms + 1e-10)
                
                # 3. 말 속도 추정 (간단한 zero-crossing rate)
                zero_crossings = np.sum(np.diff(np.sign(audio_data)) != 0)
                duration_s = len(audio_data) / wf.getframerate()
                speech_rate = zero_crossings / duration_s / 100  # 정규화
                
                # 4. 휴지 시간 (간단한 추정)
                threshold = rms * 0.1
                silence_frames = np.sum(np.abs(audio_data) < threshold)
                pause_duration_ms = (silence_frames / wf.getframerate()) * 1000
                
                features = {
                    "pitch_hz": float(pitch_hz),
                    "volume_db": float(volume_db),
                    "speech_rate": float(speech_rate),
                    "pause_duration_ms": float(pause_duration_ms),
                    "duration_s": duration_s
                }
                
                logger.debug(f"🎵 Voice features: {features}")
                
                return features
                
        except Exception as e:
            logger.error(f"❌ Voice feature extraction error: {str(e)}")
            return {
                "pitch_hz": 200,
                "volume_db": 60,
                "speech_rate": 2.0,
                "pause_duration_ms": 500
            }
    
    def _detect_dialect(self, text: str) -> str:
        """
        사투리 감지
        
        Args:
            text: 음성 인식 텍스트
            
        Returns:
            str: 사투리 지역 (경상도, 전라도, 충청도, 제주도, 표준어)
        """
        text_lower = text.lower()
        
        # 각 사투리 특징 점수
        scores = {
            "경상도": 0,
            "전라도": 0,
            "충청도": 0,
            "제주도": 0
        }
        
        # 사투리 키워드 매칭
        for dialect, patterns in self.dialect_db.items():
            for pattern in patterns.keys():
                if pattern in text_lower:
                    scores[dialect] += 1
        
        # 가장 높은 점수의 사투리
        max_dialect = max(scores, key=scores.get)
        max_score = scores[max_dialect]
        
        if max_score == 0:
            return "표준어"
        
        logger.info(f"🗣️ Dialect detected: {max_dialect} (score: {max_score})")
        
        return max_dialect
    
    async def _deepseek_inference(
        self,
        transcription: str,
        dialect: str,
        intent: Optional[str] = None
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        DeepSeek-R1로 사투리 → 표준어 변환 + 주문 추출
        
        🆕 Intent 활용으로 정확도 향상
        
        Args:
            transcription: 원본 텍스트
            dialect: 감지된 사투리
            intent: 감지된 의도 (price_inquiry, order_intent, etc.)
            
        Returns:
            tuple: (표준어, 주문 항목 리스트)
        """
        try:
            if not self.llm:
                # Fallback to rule-based
                return self._rule_based_translation(transcription, dialect), []
            
            # 🆕 Intent 기반 프롬프트 최적화
            intent_guidance = ""
            if intent == "price_inquiry":
                intent_guidance = "\n⚠️ 이것은 가격 문의입니다. items는 빈 배열로 반환하세요."
            elif intent == "cancel_intent":
                intent_guidance = "\n⚠️ 이것은 취소 요청입니다. items는 빈 배열로 반환하세요."
            elif intent == "delivery_inquiry":
                intent_guidance = "\n⚠️ 이것은 배송 일정 문의입니다."
            
            # 프롬프트 엔지니어링
            prompt = f"""당신은 한국 사투리 전문가입니다.
다음 {dialect} 사투리 문장을 표준어로 변환하고, 주문 정보를 추출하세요.

【사투리 문장】
{transcription}
{intent_guidance}

【출력 형식 (JSON)】
{{
  "standard_korean": "표준어 변환 결과",
  "items": [
    {{"product_name": "사과", "quantity": 10, "unit": "kg"}}
  ]
}}

JSON만 출력하세요:"""
            
            start_time = time.time()
            
            # DeepSeek-R1 추론
            response = self.llm(
                prompt,
                max_tokens=256,
                temperature=0.1,
                top_p=0.9,
                stop=["```", "---"],
                echo=False
            )
            
            inference_time = (time.time() - start_time) * 1000
            
            logger.info(f"⚡ DeepSeek inference: {inference_time:.1f}ms")
            
            # JSON 파싱
            output_text = response["choices"][0]["text"].strip()
            
            # JSON 추출 (```json 제거)
            if "```json" in output_text:
                output_text = output_text.split("```json")[1].split("```")[0]
            elif "```" in output_text:
                output_text = output_text.split("```")[1].split("```")[0]
            
            result = json.loads(output_text)
            
            standard_korean = result.get("standard_korean", transcription)
            items = result.get("items", [])
            
            logger.info(f"✅ Standard Korean: {standard_korean}")
            logger.info(f"✅ Items: {items}")
            
            return standard_korean, items
            
        except Exception as e:
            logger.error(f"❌ DeepSeek inference error: {str(e)}")
            # Fallback
            return self._rule_based_translation(transcription, dialect), []
    
    def _rule_based_translation(self, text: str, dialect: str) -> str:
        """
        룰 기반 사투리 → 표준어 변환 (Fallback)
        
        Args:
            text: 사투리 텍스트
            dialect: 사투리 지역
            
        Returns:
            str: 표준어
        """
        if dialect not in self.dialect_db:
            return text
        
        result = text
        
        # 패턴 매칭 변환
        for pattern, replacement in self.dialect_db[dialect].items():
            result = result.replace(pattern, replacement)
        
        return result
    
    def _extract_order_items(self, text: str) -> List[Dict[str, Any]]:
        """
        표준어에서 주문 항목 추출 (간단한 규칙 기반)
        
        Args:
            text: 표준어 텍스트
            
        Returns:
            list: 주문 항목
        """
        items = []
        
        # 간단한 패턴 매칭
        # 예: "사과 10킬로", "배추 2포기"
        import re
        
        patterns = [
            r'(\w+)\s*(\d+(?:\.\d+)?)\s*(킬로|kg|포기|개|박스)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                product_name, quantity, unit = match
                items.append({
                    "product_name": product_name,
                    "quantity": float(quantity),
                    "unit": unit
                })
        
        return items
    
    def _calculate_emergency_level(
        self,
        transcription: str,
        voice_features: Dict[str, Any]
    ) -> int:
        """
        Emergency Level 계산 (간단 버전)
        
        자세한 버전은 google_service.py에 구현됨
        """
        text_lower = transcription.lower()
        
        # 긴급 키워드
        if any(word in text_lower for word in ["죽", "아파", "살려", "위급"]):
            return 4
        elif any(word in text_lower for word in ["급해", "빨리빨리", "당장"]):
            return 3
        elif any(word in text_lower for word in ["빨리", "서둘러"]):
            return 2
        
        # 음성 특징 기반
        pitch = voice_features.get("pitch_hz", 200)
        volume = voice_features.get("volume_db", 60)
        
        if pitch > 350 and volume > 75:
            return max(3, 0)  # 최소 Level 3
        
        return 0
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """
        성능 통계
        
        Returns:
            dict: 평균/최소/최대 추론 시간
        """
        if not self.inference_times:
            return {"message": "No inference data yet"}
        
        return {
            "total_inferences": len(self.inference_times),
            "avg_time_ms": np.mean(self.inference_times),
            "min_time_ms": np.min(self.inference_times),
            "max_time_ms": np.max(self.inference_times),
            "under_200ms": sum(1 for t in self.inference_times if t < 200),
            "success_rate": sum(1 for t in self.inference_times if t < 200) / len(self.inference_times) * 100
        }


# ============================================
# 싱글톤 인스턴스
# ============================================

_deepseek_service_instance: Optional[DeepSeekService] = None


def get_deepseek_service() -> DeepSeekService:
    """
    싱글톤 DeepSeek 서비스 인스턴스
    
    Returns:
        DeepSeekService: 서비스 인스턴스
    """
    global _deepseek_service_instance
    
    if _deepseek_service_instance is None:
        _deepseek_service_instance = DeepSeekService()
    
    return _deepseek_service_instance


# ============================================
# 테스트용 메인 함수
# ============================================

async def test_deepseek_service():
    """DeepSeek Service 테스트"""
    service = get_deepseek_service()
    
    # 성능 통계
    stats = service.get_performance_stats()
    logger.info(f"Performance: {stats}")
    
    # 사투리 텍스트 테스트
    test_cases = [
        ("사과 10킬로 주문하고 싶은데요", "표준어"),
        ("사과 10킬로 사고 싶심더", "경상도"),
        ("배추 2포기 주문하고 싶당께라우", "전라도"),
    ]
    
    for text, dialect in test_cases:
        logger.info(f"\n🧪 Test: {text} ({dialect})")
        
        # 간단 테스트 (음성 파일 없이)
        detected_dialect = service._detect_dialect(text)
        standard = service._rule_based_translation(text, detected_dialect)
        items = service._extract_order_items(standard)
        
        logger.info(f"  Detected: {detected_dialect}")
        logger.info(f"  Standard: {standard}")
        logger.info(f"  Items: {items}")


if __name__ == "__main__":
    asyncio.run(test_deepseek_service())
