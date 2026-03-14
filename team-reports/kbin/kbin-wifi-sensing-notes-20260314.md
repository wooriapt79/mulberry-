# Mulberry WiFi Sensing MVP Notes

## Why the original code failed

The uploaded concept code was not directly runnable because it referenced undefined classes,
functions, and methods, including:

- `CSIReader`
- `load_mhc_model`
- `CSIAnalyzer`
- `CSICollector`
- `MHCMotionModel`
- `self.alert_emergency()`
- `self.tts_speak()`
- `self.align_modalities()`
- `self.is_speech_present()`
- `self.trigger_emergency()`
- `self.extract_biometric_features()`
- `self.compare_patterns()`
- `self.extract_amplitude()`

It also mixed string results with object-style access:

- `if result == 'fall_detected' and result.confidence > 0.95`

## What was changed in the MVP

This MVP introduces:

- runnable stub hardware classes
- a structured `DetectionResult`
- mock LED / TTS / emergency handlers
- bounded `run()` loops
- simple `demo()` execution
- fixed fall detection logic
- mock biometric enrollment / comparison

## What still needs real implementation

To move from MVP to production:

1. Replace CSI stubs with real CSI extraction
2. Integrate actual mHC inference models
3. Add real voice/TTS modules
4. Add emergency notification services
5. Add consent persistence and privacy logs
6. Validate model thresholds with field data
7. Add unit tests and edge runtime packaging
