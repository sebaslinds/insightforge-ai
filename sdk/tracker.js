/**
 * InsightForge SDK (Module 1)
 * Script léger pour la capture d'événements.
 */
class InsightForge {
    constructor(config) {
        this.apiKey = config.apiKey;
        this.apiUrl = config.apiUrl || 'http://localhost:8005/events';
        this.userId = config.userId;
    }

    async track(eventType, feature = null, properties = {}) {
        console.log(`[InsightForge] Tracking ${eventType} for feature: ${feature}`);
        
        const payload = {
            user_id: this.userId,
            event_type: eventType,
            feature: feature,
            properties: properties
        };

        try {
            const response = await fetch(this.apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': this.apiKey
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const error = await response.json();
                console.error('[InsightForge] Tracking failed:', error.detail);
            }
        } catch (err) {
            console.error('[InsightForge] Network error:', err);
        }
    }

    async trackConversion(planType, revenue = 0) {
        console.log(`[InsightForge] Tracking conversion to ${planType} with revenue: ${revenue}`);
        return this.track('conversion', planType, { revenue: revenue });
    }

    // Capture automatique des clics sur les éléments avec 'data-if-feature'
    initAutoTracking() {
        document.addEventListener('click', (e) => {
            const target = e.target.closest('[data-if-feature]');
            if (target) {
                const feature = target.getAttribute('data-if-feature');
                this.track('feature_use', feature);
            }
        });
        console.log('[InsightForge] Auto-tracking initialized.');
    }
}

// Export pour usage en module ou global
if (typeof module !== 'undefined' && module.exports) {
    module.exports = InsightForge;
} else {
    window.InsightForge = InsightForge;
}
