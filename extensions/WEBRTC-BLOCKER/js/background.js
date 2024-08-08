/* Function to get the major version of Chrome. */
function getMajorVersion() {
    var raw = navigator.userAgent.match(/Chrom(e|ium)\/([0-9]+)\./);
    return raw ? parseInt(raw[2], 10) : false;
  }
  
  /* Configure WebRTC leak prevention settings. */
  chrome.runtime.onInstalled.addListener(function(details) {
    if (details.reason === 'install' || details.reason === 'update') {
      // Check Chrome version and set appropriate WebRTC settings
      const majorVersion = getMajorVersion();
      
      if (majorVersion > 47) {
        try {
          chrome.privacy.network.webRTCIPHandlingPolicy.set({
            value: 'disable_non_proxied_udp'
          });
        } catch (e) {
          console.log("Error setting webRTCIPHandlingPolicy: " + e.message);
        }
      } else if (majorVersion > 41 && majorVersion <= 47) {
        try {
          chrome.privacy.network.webRTCMultipleRoutesEnabled.set({
            value: false
          });
          chrome.privacy.network.webRTCNonProxiedUdpEnabled.set({
            value: false
          });
        } catch (e) {
          console.log("Error setting WebRTC policies: " + e.message);
        }
      }
    }
  });
  
