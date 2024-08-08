(function() {
    console.log("Content script loaded");

    function blockWebRTC() {
        // Disable navigator.getUserMedia (deprecated but still used in some cases)
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
            navigator.mediaDevices.getUserMedia = function() {
                console.log('navigator.mediaDevices.getUserMedia is blocked');
                return Promise.reject(new Error('Blocked by extension'));
            };
        }

        // Disable MediaStreamTrack
        if (window.MediaStreamTrack) {
            Object.defineProperty(window, 'MediaStreamTrack', {
                value: undefined,
                configurable: true
            });
            console.log('MediaStreamTrack is blocked');
        }

        // Disable RTCPeerConnection
        if (window.RTCPeerConnection) {
            Object.defineProperty(window, 'RTCPeerConnection', {
                value: undefined,
                configurable: true
            });
            console.log('RTCPeerConnection is blocked');
        }

        // Disable RTCSessionDescription
        if (window.RTCSessionDescription) {
            Object.defineProperty(window, 'RTCSessionDescription', {
                value: undefined,
                configurable: true
            });
            console.log('RTCSessionDescription is blocked');
        }
        
        // Optionally, block WebRTC-specific APIs
        if (navigator.mediaDevices) {
            navigator.mediaDevices.enumerateDevices = function() { 
                return Promise.resolve([]); 
            };
        }

        console.log("WebRTC objects have been modified:");
        console.log("RTCPeerConnection:", window.RTCPeerConnection);
        console.log("MediaStreamTrack:", window.MediaStreamTrack);
        console.log("RTCSessionDescription:", window.RTCSessionDescription);
        console.log("navigator.mediaDevices.getUserMedia:", navigator.mediaDevices.getUserMedia);
    }

    // Apply the WebRTC blocking initially
    blockWebRTC();
})();
