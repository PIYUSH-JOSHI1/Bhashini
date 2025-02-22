// static/js/live-translation.js

class LiveTranslationManager {
    constructor() {
        this.isTranslating = false;
        this.socket = null;
        this.sourceLanguage = document.querySelector('#source-language');
        this.targetLanguage = document.querySelector('#target-language');
        this.subtitlesContainer = document.querySelector('#subtitles');
        this.startButton = document.querySelector('#start-translation');
        this.endButton = document.querySelector('#end-session');
        this.videoPlaceholder = document.querySelector('#video-placeholder');
        this.qualitySelector = document.querySelector('#quality-selector');
        this.audioIndicator = document.querySelector('#audio-indicator');
        
        this.translations = [];
        this.maxTranslations = 50; // Maximum number of translations to keep in history
        
        this.initializeEventListeners();
        this.initializeWebSocket();
    }

    initializeEventListeners() {
        // Start/Stop translation button
        if (this.startButton) {
            this.startButton.addEventListener('click', () => this.toggleTranslation());
        }

        // End session button
        if (this.endButton) {
            this.endButton.addEventListener('click', () => this.endSession());
        }

        // Language change handlers
        if (this.sourceLanguage) {
            this.sourceLanguage.addEventListener('change', () => this.handleLanguageChange());
        }
        if (this.targetLanguage) {
            this.targetLanguage.addEventListener('change', () => this.handleLanguageChange());
        }

        // Quality selector handler
        if (this.qualitySelector) {
            this.qualitySelector.addEventListener('change', (e) => this.handleQualityChange(e.target.value));
        }

        // Window beforeunload handler
        window.addEventListener('beforeunload', (e) => {
            if (this.isTranslating) {
                e.preventDefault();
                e.returnValue = 'Translation is in progress. Are you sure you want to leave?';
            }
        });
    }

    initializeWebSocket() {
        // In a real application, replace with actual WebSocket URL
        const wsUrl = `ws://${window.location.host}/ws/translation`;
        
        try {
            this.socket = new WebSocket(wsUrl);
            
            this.socket.onopen = () => {
                console.log('WebSocket connection established');
                this.updateConnectionStatus('Connected');
            };

            this.socket.onmessage = (event) => {
                this.handleTranslationMessage(JSON.parse(event.data));
            };

            this.socket.onclose = () => {
                console.log('WebSocket connection closed');
                this.updateConnectionStatus('Disconnected');
                // Attempt to reconnect after 5 seconds
                setTimeout(() => this.initializeWebSocket(), 5000);
            };

            this.socket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus('Connection Error');
            };
        } catch (error) {
            console.error('Failed to initialize WebSocket:', error);
            this.fallbackToSimulation();
        }
    }

    fallbackToSimulation() {
        // Fallback to simulated translations for development/demo
        console.log('Using simulated translation mode');
        this.simulationInterval = null;
        this.sampleTranslations = [
            {
                original: "नमस्कार, आजच्या सभेत आपले स्वागत आहे.",
                translation: "Welcome to today's meeting.",
                timestamp: new Date()
            },
            {
                original: "आज आपण महत्वाच्या विषयांवर चर्चा करणार आहोत.",
                translation: "Today we will discuss important topics.",
                timestamp: new Date()
            },
            {
                original: "कृपया आपले प्रश्न चॅट बॉक्समध्ये टाइप करा.",
                translation: "Please type your questions in the chat box.",
                timestamp: new Date()
            }
        ];
    }

    toggleTranslation() {
        this.isTranslating = !this.isTranslating;
        
        if (this.isTranslating) {
            this.startTranslation();
        } else {
            this.stopTranslation();
        }
        
        this.updateUI();
    }

    startTranslation() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                action: 'start',
                sourceLanguage: this.sourceLanguage.value,
                targetLanguage: this.targetLanguage.value
            }));
        } else {
            // Start simulation mode
            this.simulationInterval = setInterval(() => {
                this.simulateTranslation();
            }, 3000);
        }
        
        this.startButton.textContent = 'Stop Translation';
        this.startButton.classList.remove('bg-orange-600');
        this.startButton.classList.add('bg-red-600');
    }

    stopTranslation() {
        if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                action: 'stop'
            }));
        } else if (this.simulationInterval) {
            clearInterval(this.simulationInterval);
        }
        
        this.startButton.textContent = 'Start Translation';
        this.startButton.classList.remove('bg-red-600');
        this.startButton.classList.add('bg-orange-600');
    }

    handleTranslationMessage(data) {
        const translationDiv = document.createElement('div');
        translationDiv.className = 'mb-4 p-3 bg-gray-100 rounded-lg';
        
        const timestamp = new Date(data.timestamp);
        
        translationDiv.innerHTML = `
            <div class="text-sm text-gray-500">${timestamp.toLocaleTimeString()}</div>
            <div class="font-semibold">${data.original}</div>
            <div class="text-orange-600">${data.translation}</div>
        `;
        
        this.addTranslationToHistory(translationDiv);
    }

    simulateTranslation() {
        const randomTranslation = this.sampleTranslations[
            Math.floor(Math.random() * this.sampleTranslations.length)
        ];
        
        this.handleTranslationMessage({
            ...randomTranslation,
            timestamp: new Date()
        });
    }

    addTranslationToHistory(translationElement) {
        if (this.subtitlesContainer) {
            this.subtitlesContainer.insertBefore(translationElement, this.subtitlesContainer.firstChild);
            
            // Keep only the last N translations
            while (this.subtitlesContainer.children.length > this.maxTranslations) {
                this.subtitlesContainer.removeChild(this.subtitlesContainer.lastChild);
            }
            
            // Smooth scroll to the latest translation
            translationElement.scrollIntoView({ behavior: 'smooth' });
        }
    }

    handleLanguageChange() {
        if (this.isTranslating) {
            // Restart translation with new language settings
            this.stopTranslation();
            this.startTranslation();
        }
    }

    handleQualityChange(quality) {
        // Simulate quality change
        console.log(`Changing translation quality to: ${quality}`);
        // In a real application, send quality preference to backend
    }

    updateConnectionStatus(status) {
        const statusElement = document.querySelector('#connection-status');
        if (statusElement) {
            statusElement.textContent = `Status: ${status}`;
            statusElement.className = `text-sm ${
                status === 'Connected' ? 'text-green-600' : 'text-red-600'
            }`;
        }
    }

    updateUI() {
        // Update UI elements based on current state
        if (this.endButton) {
            this.endButton.disabled = !this.isTranslating;
        }
        
        if (this.qualitySelector) {
            this.qualitySelector.disabled = !this.isTranslating;
        }
    }

    endSession() {
        if (confirm('Are you sure you want to end this translation session?')) {
            this.stopTranslation();
            window.location.href = '/';
        }
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    const translationManager = new LiveTranslationManager();
});