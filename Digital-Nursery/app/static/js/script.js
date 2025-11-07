// Auto-dismiss Bootstrap alerts after 5 seconds with fade-out
window.addEventListener('DOMContentLoaded', function() {
	var alerts = document.querySelectorAll('.alert');
	alerts.forEach(function(alert) {
		setTimeout(function() {
			// Use Bootstrap's built-in alert close if available
			if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
				var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
				bsAlert.close();
			} else {
				// Fallback: fade out and remove
				alert.classList.add('fade');
				alert.classList.remove('show');
				setTimeout(function() {
					alert.remove();
				}, 500);
			}
		}, 5000);
	});
});
