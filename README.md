# Sanskrit Voice Bot v2 🕉️

**A modularized Sanskrit pronunciation training application with AI-powered feedback**

Sanskrit Voice Bot v2 is a comprehensive refactoring of the original Sanskrit pronunciation learning tool. This version features improved modularity, maintainability, and enhanced user experience through intelligent audio analysis and personalized AI feedback.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🌟 Features

### Core Functionality
- **🎙️ High-Quality Audio Recording**: Professional audio capture with noise reduction
- **🎵 Audio Playbook**: Reference audio playback for pronunciation guidance
- **🗣️ Speech Recognition**: Advanced transcription using Groq's Whisper API
- **📊 Pronunciation Analysis**: Intelligent comparison with reference pronunciations
- **🤖 AI-Powered Feedback**: Personalized suggestions using Google Gemini AI
- **📈 Progress Tracking**: Comprehensive learning analytics and progress monitoring

### Learning Modes
- **📖 Full Shloka Practice**: Complete verse pronunciation training
- **🔤 Word-by-Word Practice**: Focused individual word pronunciation
- **🅰️ Alphabet Practice**: Sanskrit consonant and vowel mastery
- **👥 Multi-Speaker Support**: Practice with 27 different speakers (sp001-sp027)

### User Experience
- **🖥️ Intuitive GUI**: Clean, responsive interface built with Tkinter
- **⚡ Real-Time Feedback**: Instant pronunciation analysis and corrections
- **🎨 Visual Progress**: Color-coded accuracy indicators
- **📱 Responsive Design**: Adaptable interface for different screen sizes

## 🏗️ Architecture Overview

The v2 architecture implements a clean separation of concerns with the following modular structure:

```
v2/
├── 🚀 main.py                    # Application entry point
├── 🧠 core/                      # Core application logic
│   ├── config.py                 # Centralized configuration
│   └── app.py                    # Main application controller
├── 🎵 audio/                     # Audio processing pipeline
│   └── audio_manager.py          # Recording, playback, transcription
├── 📊 data/                      # Data management layer
│   └── transcript_manager.py     # Sanskrit text and audio data
├── 🔍 analysis/                  # Intelligence & analysis
│   ├── pronunciation_analyzer.py # Pronunciation comparison engine
│   └── feedback_generator.py     # AI feedback generation
├── 📚 practice/                  # Practice session management
│   ├── word_practice_tracker.py  # Individual word progress
│   └── alphabet_practice.py      # Alphabet learning system
├── 🛠️ utils/                     # Utility functions
│   └── text_processor.py         # Sanskrit text processing
└── 🎨 ui/                        # User interface components
    ├── main_window.py             # Primary application interface
    └── results_display.py         # Results formatting & display
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** with pip
- **Audio device** (microphone and speakers)
- **Internet connection** (for AI services)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Kaushik-2005/SanskritVoiceBot.git
   cd SanskritVoiceBot
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API keys** (Edit `v2/core/config.py`)
   ```python
   # Add your API keys
   GROQ_API_KEY = "your_groq_api_key_here"
   GEMINI_API_KEY = "your_gemini_api_key_here"
   ```

### Running the Application

**🎯 Recommended Method:**
```bash
# From project root
python run_v2.py
```

**Alternative Methods:**
```bash
# Option 1: Direct execution
python v2/main.py

# Option 2: From v2 directory
cd v2
python main.py
```

## 📋 Module Documentation

### 🧠 Core Module (`core/`)

#### `config.py` - Configuration Hub
**Purpose**: Centralized configuration management for all application settings.

**Key Components**:
- `AppConfig`: Application metadata and data paths
- `AudioConfig`: Audio processing parameters and API settings
- `AnalysisConfig`: Analysis thresholds and accuracy criteria
- `UIConfig`: Interface styling, colors, and typography
- `PracticeConfig`: Learning session parameters
- `SanskritConstants`: Language-specific data and phoneme mappings

#### `app.py` - Application Controller
**Purpose**: Main orchestrator that coordinates all application components.

**Responsibilities**:
- Initialize and manage component lifecycle
- Handle user interactions and application flow
- Coordinate between UI, audio, analysis, and practice systems
- Manage application state and error handling

### 🎵 Audio Module (`audio/`)

#### `audio_manager.py` - Audio Processing Pipeline
**Purpose**: Complete audio handling from recording to transcription.

**Features**:
- High-quality audio recording with configurable parameters
- Multi-format audio playback (MP3, WAV)
- Integration with Groq API for speech-to-text
- Audio quality validation and enhancement
- Error handling for audio device issues

### 📊 Data Module (`data/`)

#### `transcript_manager.py` - Data Access Layer
**Purpose**: Manages Sanskrit text data and audio file access.

**Capabilities**:
- Load Devanagari and SLP1 transcript files
- Manage multi-speaker audio datasets (sp001-sp027)
- Provide structured data access for practice sessions
- Handle file I/O operations with error recovery
- Implement caching for improved performance

### 🔍 Analysis Module (`analysis/`)

#### `pronunciation_analyzer.py` - Analysis Engine
**Purpose**: Core pronunciation comparison and accuracy calculation.

**Features**:
- Advanced phonetic similarity algorithms
- Word-by-word pronunciation breakdown
- Accuracy scoring with configurable thresholds
- Support for both full shloka and individual word analysis
- Detailed error reporting and suggestions

#### `feedback_generator.py` - AI Feedback System
**Purpose**: Generate personalized learning feedback using Google Gemini AI.

**Capabilities**:
- Context-aware pronunciation feedback
- Constructive improvement suggestions
- Motivational messaging
- Error pattern recognition
- Adaptive difficulty recommendations

### 📚 Practice Module (`practice/`)

#### `word_practice_tracker.py` - Individual Word Progress
**Purpose**: Track and optimize individual word learning progress.

**Features**:
- Per-word accuracy tracking
- Attempt count and improvement trends
- Identify words needing additional practice
- Generate personalized practice schedules
- Historical performance analytics

#### `alphabet_practice.py` - Sanskrit Alphabet Mastery
**Purpose**: Systematic Sanskrit alphabet pronunciation training.

**Components**:
- Vowel (स्वर) and consonant (व्यञ्जन) practice
- Progressive difficulty levels
- Pronunciation guide with audio examples
- Mastery criteria and progress tracking

### 🛠️ Utils Module (`utils/`)

#### `text_processor.py` - Sanskrit Text Processing
**Purpose**: Handle Sanskrit text conversion and processing.

**Utilities**:
- Devanagari ↔ SLP1 transliteration
- Sanskrit text normalization and validation
- Phonetic similarity calculations
- Text preprocessing for analysis
- Character encoding handling

### 🎨 UI Module (`ui/`)

#### `main_window.py` - Primary Interface
**Purpose**: Main application window and user interaction handling.

**Components**:
- Speaker and shloka selection interfaces
- Audio recording and playback controls
- Practice mode selection and navigation
- Real-time status updates and progress display
- Error handling with user-friendly messages

#### `results_display.py` - Results Presentation
**Purpose**: Format and display analysis results and feedback.

**Features**:
- Color-coded accuracy results
- Formatted AI feedback with syntax highlighting
- Practice guidance and suggestions
- Error messages and troubleshooting tips
- Progress visualization

## 🎯 Usage Guide

### Getting Started
1. **Launch the application** using one of the startup methods
2. **Select a speaker** from the dropdown (sp001-sp027)
3. **Choose a shloka** for practice
4. **Select practice mode**: Full shloka or word-by-word

### Practice Workflow
1. **Listen** to the reference pronunciation
2. **Record** your pronunciation attempt
3. **Analyze** to get instant feedback
4. **Review** AI-powered suggestions
5. **Practice** areas needing improvement
6. **Track** your progress over time

### Advanced Features
- **Custom Practice Sets**: Create personalized word lists
- **Progress Analytics**: View detailed learning statistics
- **Audio Quality Testing**: Validate microphone setup
- **Export Results**: Save practice sessions for review

## ⚙️ Configuration

### API Setup
Update `v2/core/config.py` with your API credentials:

```python
class AudioConfig:
    # Groq API for speech recognition
    GROQ_API_KEY = "your_groq_api_key"
    
class AnalysisConfig:
    # Google Gemini for AI feedback
    GEMINI_API_KEY = "your_gemini_api_key"
```

### Customization Options
- **UI Themes**: Modify colors and fonts in `UIConfig`
- **Analysis Sensitivity**: Adjust accuracy thresholds in `AnalysisConfig`
- **Audio Quality**: Configure recording parameters in `AudioConfig`
- **Practice Settings**: Customize learning parameters in `PracticeConfig`

## 🔧 Development

### Architecture Benefits
- **Modularity**: Clear separation of concerns for easier maintenance
- **Scalability**: Plugin-ready architecture for new features
- **Testability**: Individual components can be unit tested
- **Documentation**: Comprehensive docstrings and type hints
- **Error Handling**: Robust error recovery throughout the application

### Adding New Features
1. Identify the appropriate module for new functionality
2. Follow established patterns and interfaces
3. Add configuration options to `config.py`
4. Update documentation and type hints
5. Test integration with existing components

### Code Quality Standards
- **PEP 8**: Python style guidelines compliance
- **Type Hints**: Full type annotation coverage
- **Docstrings**: Comprehensive documentation for all public APIs
- **Error Handling**: Graceful error recovery with user feedback
- **Testing**: Unit tests for critical functionality

## 🔄 Migration from v1

The v2 architecture maintains **100% functional compatibility** with the original application while providing significant improvements:

### Preserved Features
- ✅ All original pronunciation analysis capabilities
- ✅ Multi-speaker support (sp001-sp027)
- ✅ Full shloka and word-level practice modes
- ✅ Audio recording and playback functionality
- ✅ Progress tracking and analytics

### New Enhancements
- 🆕 Modular architecture with clear component boundaries
- 🆕 Centralized configuration management
- 🆕 Enhanced error handling and user feedback
- 🆕 Improved code documentation and maintainability
- 🆕 Type safety with comprehensive type hints
- 🆕 Scalable design for future feature additions

## 🐛 Troubleshooting

### Common Issues

**Import Errors**
```bash
# Solution: Run from project root
cd "path/to/SanskritVoiceBot"
python run_v2.py
```

**Audio Device Issues**
- Check microphone permissions
- Verify audio device connections
- Test with the built-in audio test feature

**API Connection Problems**
- Verify internet connectivity
- Check API key configuration
- Review API usage limits

**Data Loading Issues**
- Ensure data directory exists in project root
- Verify transcript file permissions
- Check audio file formats (MP3 required)

### Performance Optimization
- **Memory**: Close unused practice sessions
- **Storage**: Clear temporary audio files periodically
- **Network**: Use local caching for repeated requests

## 🤝 Contributing

We welcome contributions to improve Sanskrit Voice Bot v2! Here's how you can help:

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Follow the established code style
4. Add tests for new functionality
5. Submit a pull request

### Areas for Contribution
- **New Language Support**: Extend to other ancient languages
- **Advanced Analytics**: Enhanced progress tracking
- **Mobile Compatibility**: Responsive design improvements
- **Performance Optimization**: Audio processing improvements
- **Documentation**: Tutorial videos and user guides

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Sanskrit Scholars**: For pronunciation guidance and validation
- **Open Source Community**: For the excellent libraries used in this project
- **Contributors**: Everyone who helped improve the application
- **Users**: For feedback and suggestions that shaped v2

## 📞 Support

For questions, issues, or contributions:
- **GitHub Issues**: [Report bugs or request features](https://github.com/Kaushik-2005/SanskritVoiceBot/issues)
- **Documentation**: Check this README and inline code documentation
- **Community**: Join discussions in the repository

---

**Sanskrit Voice Bot v2** - Bridging ancient wisdom with modern technology through intelligent software architecture.

*"यत्र योगः तत्र जयः" - Where there is dedicated practice, there is victory.*
