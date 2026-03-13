# Mulberry WiFi Sensing MVP (Minimum Viable Product)

이 프로젝트는 WiFi 신호(CSI: Channel State Information)를 활용하여 사람의 움직임 감지, 낙상 감지, 멀티모달 센싱, 그리고 사람 식별 기능을 시뮬레이션하는 MVP(Minimum Viable Product) 버전입니다.

## 주요 기능 및 클래스

*   **`CSIReader`**: WiFi 인터페이스로부터 CSI 데이터를 읽는 것을 모의합니다.
*   **`CSIAnalyzer`**: CSI 데이터를 수집하고 분석하는 기본적인 기능을 제공합니다.
*   **`CSICollector`**: 지정된 시간 동안 CSI 데이터를 수집하는 것을 모의합니다.
*   **`LEDIndicator`**: 시스템 상태를 시각적으로 나타내는 LED 동작을 모의합니다.
*   **`MHCMotionDetector`**: CSI 데이터의 평균 진폭을 기반으로 `normal`, `abnormal_movement`, `fall_detected`를 분석합니다. 임계값(`fall_threshold`, `abnormal_threshold`)을 조정할 수 있습니다.
*   **`MHCMotionModel`**: 진폭 데이터를 사용하여 `normal`, `abnormal_movement`, `fall_detected`를 예측하고 신뢰도를 반환합니다.
*   **`MHCMultiModalModel`**: 오디오와 CSI 데이터를 결합한 신호의 평균을 기반으로 상황을 예측합니다.
*   **`WiFiSensingModule`**: CSI 추출 및 `MHCMotionDetector`를 활용하여 움직임을 감지하고, 낙상 시 비상 알림을 트리거합니다.
*   **`WiFiSensingPrivacy`**: 사용자 동의 및 데이터 수집 활성화/비활성화를 관리하며, 음성 명령에 반응하는 것을 모의합니다.
*   **`MHCMultiModalSensor`**: `MHCMultiModalModel`을 사용하여 오디오와 CSI 데이터를 통합 분석하고, 음성 존재 여부, 낙상 및 비정상 움직임 감지 시 특정 액션을 수행합니다.
*   **`WhoFiIdentifier`**: CSI 패턴을 '바디 시그니처'로 사용하여 사람을 등록하고 식별합니다.
*   **`WiFiFallDetector`**: `CSICollector`와 `MHCMotionModel`을 사용하여 낙상을 감지하고, 높은 신뢰도로 낙상 감지 시 비상 알림을 트리거합니다.

## 프로젝트 실행 방법

Google Colab 환경에서 이 노트북(`mulberry_wifi_sensing_mvp.ipynb`와 같은 파일)을 엽니다. 모든 셀을 순서대로 실행하여 각 모듈의 동작을 확인할 수 있습니다.

*   **모든 셀 실행**: Colab 메뉴에서 `런타임(Runtime)` -> `모두 실행(Run all)`을 선택합니다.
*   **개별 셀 실행**: 원하는 셀을 선택한 후 `Ctrl + Enter` 또는 셀 좌측의 실행 버튼(▶)을 클릭합니다.

## 시뮬레이션 및 테스트

노트북에는 각 클래스 및 모듈의 기능을 테스트하기 위한 다양한 시뮬레이션 코드가 포함되어 있습니다. 이를 통해 각 모듈의 동작 방식과 임계값 변경에 따른 영향을 확인할 수 있습니다.

### `MHCMotionDetector` 임계값 조정
`MHCMotionDetector` 클래스 내 `fall_threshold` 및 `abnormal_threshold` 변수의 값을 변경하여 감지 민감도를 조정할 수 있습니다.

### `WiFiFallDetector` 낙상 시뮬레이션
`MockCSICollector`를 통해 고의적으로 낙상 상황과 유사한 CSI 데이터를 주입하여 비상 알림이 트리거되는 과정을 확인할 수 있습니다.

### `WhoFiIdentifier` 사람 식별
특정 `person_id`로 사람의 바디 시그니처를 등록한 후, 유사하거나 다른 CSI 데이터로 식별을 시도하여 모듈의 정확도를 테스트할 수 있습니다.

# Mulberry WiFi Sensing MVP (Minimum Viable Product)

이 프로젝트는 WiFi 신호(CSI: Channel State Information)를 활용하여 사람의 움직임 감지, 낙상 감지, 멀티모달 센싱, 그리고 사람 식별 기능을 시뮬레이션하는 MVP(Minimum Viable Product) 버전입니다.

## 주요 기능 및 클래스

*   **`CSIReader`**: WiFi 인터페이스로부터 CSI 데이터를 읽는 것을 모의합니다.
*   **`CSIAnalyzer`**: CSI 데이터를 수집하고 분석하는 기본적인 기능을 제공합니다.
*   **`CSICollector`**: 지정된 시간 동안 CSI 데이터를 수집하는 것을 모의합니다.
*   **`LEDIndicator`**: 시스템 상태를 시각적으로 나타내는 LED 동작을 모의합니다.
*   **`MHCMotionDetector`**: CSI 데이터의 평균 진폭을 기반으로 `normal`, `abnormal_movement`, `fall_detected`를 분석합니다. 임계값(`fall_threshold`, `abnormal_threshold`)을 조정할 수 있습니다.
*   **`MHCMotionModel`**: 진폭 데이터를 사용하여 `normal`, `abnormal_movement`, `fall_detected`를 예측하고 신뢰도를 반환합니다.
*   **`MHCMultiModalModel`**: 오디오와 CSI 데이터를 결합한 신호의 평균을 기반으로 상황을 예측합니다.
*   **`WiFiSensingModule`**: CSI 추출 및 `MHCMotionDetector`를 활용하여 움직임을 감지하고, 낙상 시 비상 알림을 트리거합니다.
*   **`WiFiSensingPrivacy`**: 사용자 동의 및 데이터 수집 활성화/비활성화를 관리하며, 음성 명령에 반응하는 것을 모의합니다.
*   **`MHCMultiModalSensor`**: `MHCMultiModalModel`을 사용하여 오디오와 CSI 데이터를 통합 분석하고, 음성 존재 여부, 낙상 및 비정상 움직임 감지 시 특정 액션을 수행합니다.
*   **`WhoFiIdentifier`**: CSI 패턴을 '바디 시그니처'로 사용하여 사람을 등록하고 식별합니다.
*   **`WiFiFallDetector`**: `CSICollector`와 `MHCMotionModel`을 사용하여 낙상을 감지하고, 높은 신뢰도로 낙상 감지 시 비상 알림을 트리거합니다.

## 프로젝트 실행 방법

Google Colab 환경에서 이 노트북(`mulberry_wifi_sensing_mvp.ipynb`와 같은 파일)을 엽니다. 모든 셀을 순서대로 실행하여 각 모듈의 동작을 확인할 수 있습니다.

*   **모든 셀 실행**: Colab 메뉴에서 `런타임(Runtime)` -> `모두 실행(Run all)`을 선택합니다.
*   **개별 셀 실행**: 원하는 셀을 선택한 후 `Ctrl + Enter` 또는 셀 좌측의 실행 버튼(▶)을 클릭합니다.

## 시뮬레이션 및 테스트

노트북에는 각 클래스 및 모듈의 기능을 테스트하기 위한 다양한 시뮬레이션 코드가 포함되어 있습니다. 이를 통해 각 모듈의 동작 방식과 임계값 변경에 따른 영향을 확인할 수 있습니다.

### `MHCMotionDetector` 임계값 조정
`MHCMotionDetector` 클래스 내 `fall_threshold` 및 `abnormal_threshold` 변수의 값을 변경하여 감지 민감도를 조정할 수 있습니다.

### `WiFiFallDetector` 낙상 시뮬레이션
`MockCSICollector`를 통해 고의적으로 낙상 상황과 유사한 CSI 데이터를 주입하여 비상 알림이 트리거되는 과정을 확인할 수 있습니다.

### `WhoFiIdentifier` 사람 식별
특정 `person_id`로 사람의 바디 시그니처를 등록한 후, 유사하거나 다른 CSI 데이터로 식별을 시도하여 모듈의 정확도를 테스트할 수 있습니다.

# Mulberry WiFi Sensing MVP (Minimum Viable Product)

이 프로젝트는 WiFi 신호(CSI: Channel State Information)를 활용하여 사람의 움직임 감지, 낙상 감지, 멀티모달 센싱, 그리고 사람 식별 기능을 시뮬레이션하는 MVP(Minimum Viable Product) 버전입니다.

## 주요 기능 및 클래스

*   **`CSIReader`**: WiFi 인터페이스로부터 CSI 데이터를 읽는 것을 모의합니다.
*   **`CSIAnalyzer`**: CSI 데이터를 수집하고 분석하는 기본적인 기능을 제공합니다.
*   **`CSICollector`**: 지정된 시간 동안 CSI 데이터를 수집하는 것을 모의합니다.
*   **`LEDIndicator`**: 시스템 상태를 시각적으로 나타내는 LED 동작을 모의합니다.
*   **`MHCMotionDetector`**: CSI 데이터의 평균 진폭을 기반으로 `normal`, `abnormal_movement`, `fall_detected`를 분석합니다. 임계값(`fall_threshold`, `abnormal_threshold`)을 조정할 수 있습니다.
*   **`MHCMotionModel`**: 진폭 데이터를 사용하여 `normal`, `abnormal_movement`, `fall_detected`를 예측하고 신뢰도를 반환합니다.
*   **`MHCMultiModalModel`**: 오디오와 CSI 데이터를 결합한 신호의 평균을 기반으로 상황을 예측합니다.
*   **`WiFiSensingModule`**: CSI 추출 및 `MHCMotionDetector`를 활용하여 움직임을 감지하고, 낙상 시 비상 알림을 트리거합니다.
*   **`WiFiSensingPrivacy`**: 사용자 동의 및 데이터 수집 활성화/비활성화를 관리하며, 음성 명령에 반응하는 것을 모의합니다.
*   **`MHCMultiModalSensor`**: `MHCMultiModalModel`을 사용하여 오디오와 CSI 데이터를 통합 분석하고, 음성 존재 여부, 낙상 및 비정상 움직임 감지 시 특정 액션을 수행합니다.
*   **`WhoFiIdentifier`**: CSI 패턴을 '바디 시그니처'로 사용하여 사람을 등록하고 식별합니다.
*   **`WiFiFallDetector`**: `CSICollector`와 `MHCMotionModel`을 사용하여 낙상을 감지하고, 높은 신뢰도로 낙상 감지 시 비상 알림을 트리거합니다.

## 프로젝트 실행 방법

Google Colab 환경에서 이 노트북(`mulberry_wifi_sensing_mvp.ipynb`와 같은 파일)을 엽니다. 모든 셀을 순서대로 실행하여 각 모듈의 동작을 확인할 수 있습니다.

*   **모든 셀 실행**: Colab 메뉴에서 `런타임(Runtime)` -> `모두 실행(Run all)`을 선택합니다.
*   **개별 셀 실행**: 원하는 셀을 선택한 후 `Ctrl + Enter` 또는 셀 좌측의 실행 버튼(▶)을 클릭합니다.

## 시뮬레이션 및 테스트

노트북에는 각 클래스 및 모듈의 기능을 테스트하기 위한 다양한 시뮬레이션 코드가 포함되어 있습니다. 이를 통해 각 모듈의 동작 방식과 임계값 변경에 따른 영향을 확인할 수 있습니다.

### `MHCMotionDetector` 임계값 조정
`MHCMotionDetector` 클래스 내 `fall_threshold` 및 `abnormal_threshold` 변수의 값을 변경하여 감지 민감도를 조정할 수 있습니다.

### `WiFiFallDetector` 낙상 시뮬레이션
`MockCSICollector`를 통해 고의적으로 낙상 상황과 유사한 CSI 데이터를 주입하여 비상 알림이 트리거되는 과정을 확인할 수 있습니다.

### `WhoFiIdentifier` 사람 식별
특정 `person_id`로 사람의 바디 시그니처를 등록한 후, 유사하거나 다른 CSI 데이터로 식별을 시도하여 모듈의 정확도를 테스트할 수 있습니다.
