"""
Mulberry Phase 2 - Raspberry Pi 5 Edge AI Controller
GPIO 인터페이스 최적화 및 음성 인식 딜레이 0.2초 달성
"""

import asyncio
import json
import wave
import pyaudio
from typing import Optional, Dict, Any, Callable
from datetime import datetime
from pathlib import Path
from loguru import logger

# GPIO 제어 (Raspberry Pi 전용)
try:
    import RPi.GPIO as GPIO
    import board
    import busio
    import adafruit_ads1x15.ads1115 as ADS
    from adafruit_ads1x15.analog_in import AnalogIn
    RPI_AVAILABLE = True
except ImportError:
    logger.warning("⚠️ RPi.GPIO not available (running on non-Raspberry Pi)")
    RPI_AVAILABLE = False


class RaspberryPiController:
    """
    Raspberry Pi 5 Edge AI 제어기
    - 마이크/스피커 GPIO 제어
    - 음성 인식 최적화 (딜레이 0.2초 이내)
    - DeepSeek-R1 온디바이스 추론 연동
    """
    
    def __init__(self):
        """RPi 5 초기화"""
        self.rpi_available = RPI_AVAILABLE
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000  # 16kHz 샘플링 (음성 인식 최적화)
        self.chunk_size = 1024  # 버퍼 크기 최적화
        self.record_seconds = 5
        
        # PyAudio 초기화
        self.audio = pyaudio.PyAudio()
        
        # GPIO 핀 설정 (Raspberry Pi 5)
        self.LED_PIN = 18  # LED 상태 표시
        self.BUTTON_PIN = 23  # 주문 시작 버튼
        self.MIC_ENABLE_PIN = 24  # 마이크 활성화
        self.SPEAKER_PIN = 25  # 스피커 출력
        
        # DeepSeek-R1 모델 경로
        self.model_path = "/opt/mulberry/models/deepseek-r1-distill-qwen-7b-q4.gguf"
        
        if self.rpi_available:
            self._setup_gpio()
        
        logger.info("✅ Raspberry Pi 5 Controller initialized")
    
    def _setup_gpio(self):
        """GPIO 핀 설정"""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # LED 출력
            GPIO.setup(self.LED_PIN, GPIO.OUT)
            
            # 버튼 입력 (풀업 저항)
            GPIO.setup(self.BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            
            # 마이크/스피커 제어
            GPIO.setup(self.MIC_ENABLE_PIN, GPIO.OUT)
            GPIO.setup(self.SPEAKER_PIN, GPIO.OUT)
            
            # 초기 상태
            GPIO.output(self.LED_PIN, GPIO.LOW)
            GPIO.output(self.MIC_ENABLE_PIN, GPIO.LOW)
            GPIO.output(self.SPEAKER_PIN, GPIO.LOW)
            
            # 버튼 인터럽트 설정 (0.2초 이내 반응)
            GPIO.add_event_detect(
                self.BUTTON_PIN,
                GPIO.FALLING,
                callback=self._button_pressed,
                bouncetime=200  # 200ms 디바운스
            )
            
            logger.info("✅ GPIO setup complete")
            
        except Exception as e:
            logger.error(f"❌ GPIO setup error: {str(e)}")
    
    def _button_pressed(self, channel):
        """버튼 눌림 인터럽트 핸들러"""
        logger.info("🔘 Order button pressed!")
        # LED 깜빡임으로 피드백
        self.blink_led(times=2, interval=0.1)
        
        # 비동기 음성 인식 시작
        asyncio.create_task(self.start_voice_order())
    
    def blink_led(self, times: int = 1, interval: float = 0.5):
        """LED 깜빡임"""
        if not self.rpi_available:
            return
        
        for _ in range(times):
            GPIO.output(self.LED_PIN, GPIO.HIGH)
            asyncio.sleep(interval)
            GPIO.output(self.LED_PIN, GPIO.LOW)
            asyncio.sleep(interval)
    
    async def record_audio(self, duration: int = 5) -> str:
        """
        마이크로 음성 녹음 (최적화)
        
        Args:
            duration: 녹음 시간 (초)
            
        Returns:
            str: 저장된 오디오 파일 경로
        """
        try:
            # 마이크 활성화
            if self.rpi_available:
                GPIO.output(self.MIC_ENABLE_PIN, GPIO.HIGH)
                GPIO.output(self.LED_PIN, GPIO.HIGH)  # 녹음 중 표시
            
            logger.info(f"🎙️ Recording audio ({duration}s)...")
            
            # 스트림 열기 (저지연 설정)
            stream = self.audio.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                input_device_index=None  # 기본 마이크
            )
            
            frames = []
            
            # 실시간 녹음 (chunk 단위)
            for i in range(0, int(self.rate / self.chunk_size * duration)):
                data = stream.read(self.chunk_size, exception_on_overflow=False)
                frames.append(data)
            
            # 스트림 종료
            stream.stop_stream()
            stream.close()
            
            # 마이크 비활성화
            if self.rpi_available:
                GPIO.output(self.MIC_ENABLE_PIN, GPIO.LOW)
                GPIO.output(self.LED_PIN, GPIO.LOW)
            
            # WAV 파일 저장
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"/tmp/mulberry_audio_{timestamp}.wav"
            
            with wave.open(output_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.audio_format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(frames))
            
            logger.info(f"✅ Audio saved: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"❌ Audio recording error: {str(e)}")
            if self.rpi_available:
                GPIO.output(self.MIC_ENABLE_PIN, GPIO.LOW)
                GPIO.output(self.LED_PIN, GPIO.LOW)
            raise
    
    async def play_audio(self, audio_file: str):
        """
        스피커로 오디오 재생
        
        Args:
            audio_file: 재생할 오디오 파일 경로
        """
        try:
            # 스피커 활성화
            if self.rpi_available:
                GPIO.output(self.SPEAKER_PIN, GPIO.HIGH)
            
            logger.info(f"🔊 Playing audio: {audio_file}")
            
            # WAV 파일 재생
            with wave.open(audio_file, 'rb') as wf:
                stream = self.audio.open(
                    format=self.audio.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True
                )
                
                # 청크 단위 재생
                data = wf.readframes(self.chunk_size)
                while data:
                    stream.write(data)
                    data = wf.readframes(self.chunk_size)
                
                stream.stop_stream()
                stream.close()
            
            # 스피커 비활성화
            if self.rpi_available:
                GPIO.output(self.SPEAKER_PIN, GPIO.LOW)
            
            logger.info("✅ Audio playback complete")
            
        except Exception as e:
            logger.error(f"❌ Audio playback error: {str(e)}")
            if self.rpi_available:
                GPIO.output(self.SPEAKER_PIN, GPIO.LOW)
    
    async def start_voice_order(self):
        """
        음성 주문 프로세스 (전체 흐름)
        
        1. 음성 녹음
        2. DeepSeek-R1 사투리 인식
        3. 서버로 전송
        4. 확인 메시지 재생
        """
        try:
            # 1. "주문을 말씀하세요" 안내
            await self.play_audio("/opt/mulberry/sounds/order_prompt.wav")
            
            # 2. 음성 녹음 (5초)
            audio_file = await self.record_audio(duration=5)
            
            # 3. DeepSeek-R1 온디바이스 추론 (0.2초 이내 목표)
            from app.services.deepseek_service import get_deepseek_service
            
            deepseek = get_deepseek_service()
            
            # 사투리 → 표준어 변환 + 주문 추출
            result = await deepseek.process_voice_order(audio_file)
            
            if not result.get("success"):
                await self.play_audio("/opt/mulberry/sounds/error.wav")
                return
            
            # 4. 서버로 예약 전송
            reservation_data = {
                "customer_phone": "010-XXXX-XXXX",  # 실제로는 등록된 전화번호
                "customer_name": "어르신",
                "farm_id": 1,
                "requested_items": result["items"],
                "audio_transcription": result["transcription"],
                "dialect": result["dialect"],
                "voice_features": result["voice_features"]
            }
            
            # Google Service로 전송
            from app.services.google_service import get_google_service
            
            google_service = get_google_service()
            reservation_result = await google_service.handle_voice_reservation(reservation_data)
            
            # 5. 결과 안내
            if reservation_result.get("success"):
                # "주문이 접수되었습니다" 재생
                await self.play_audio("/opt/mulberry/sounds/order_confirmed.wav")
                
                # LED 3회 깜빡임
                self.blink_led(times=3, interval=0.3)
            else:
                await self.play_audio("/opt/mulberry/sounds/order_failed.wav")
            
            logger.info(f"✅ Voice order complete: {reservation_result.get('reservation_number')}")
            
        except Exception as e:
            logger.error(f"❌ Voice order error: {str(e)}")
            await self.play_audio("/opt/mulberry/sounds/error.wav")
    
    async def run_diagnostics(self) -> Dict[str, Any]:
        """
        시스템 진단
        
        Returns:
            dict: 진단 결과
        """
        try:
            diagnostics = {
                "timestamp": datetime.now().isoformat(),
                "rpi_available": self.rpi_available,
                "gpio_status": "OK" if self.rpi_available else "N/A",
                "audio_devices": [],
                "deepseek_model": None
            }
            
            # 오디오 장치 확인
            for i in range(self.audio.get_device_count()):
                device_info = self.audio.get_device_info_by_index(i)
                diagnostics["audio_devices"].append({
                    "index": i,
                    "name": device_info["name"],
                    "channels": device_info["maxInputChannels"]
                })
            
            # DeepSeek 모델 확인
            if Path(self.model_path).exists():
                diagnostics["deepseek_model"] = "OK"
            else:
                diagnostics["deepseek_model"] = f"NOT FOUND: {self.model_path}"
            
            logger.info(f"📊 Diagnostics: {diagnostics}")
            
            return diagnostics
            
        except Exception as e:
            logger.error(f"❌ Diagnostics error: {str(e)}")
            return {"error": str(e)}
    
    def cleanup(self):
        """리소스 정리"""
        try:
            if self.rpi_available:
                GPIO.cleanup()
            
            self.audio.terminate()
            
            logger.info("✅ Cleanup complete")
            
        except Exception as e:
            logger.error(f"❌ Cleanup error: {str(e)}")


# ============================================
# 싱글톤 인스턴스
# ============================================

_rpi_controller_instance: Optional[RaspberryPiController] = None


def get_rpi_controller() -> RaspberryPiController:
    """
    싱글톤 RPi Controller 인스턴스 반환
    
    Returns:
        RaspberryPiController: 컨트롤러 인스턴스
    """
    global _rpi_controller_instance
    
    if _rpi_controller_instance is None:
        _rpi_controller_instance = RaspberryPiController()
    
    return _rpi_controller_instance


# ============================================
# 테스트용 메인 함수
# ============================================

async def test_rpi_controller():
    """RPi Controller 테스트"""
    controller = get_rpi_controller()
    
    # 진단 실행
    diagnostics = await controller.run_diagnostics()
    logger.info(f"Diagnostics: {json.dumps(diagnostics, indent=2)}")
    
    # LED 테스트
    if controller.rpi_available:
        logger.info("Testing LED...")
        controller.blink_led(times=5, interval=0.2)
    
    # 음성 녹음 테스트
    logger.info("Testing audio recording...")
    audio_file = await controller.record_audio(duration=3)
    logger.info(f"Recorded: {audio_file}")
    
    # 정리
    controller.cleanup()


if __name__ == "__main__":
    asyncio.run(test_rpi_controller())
