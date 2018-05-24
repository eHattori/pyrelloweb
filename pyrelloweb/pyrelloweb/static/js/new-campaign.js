$(document).ready(function () {
	$('#agree-terms').click(function(){
		var has_checked = $('#agree-terms:checkbox:checked').length > 0;
		if (has_checked) {
			$('#btn-send').show();
		} else {
			$('#btn-send').hide();
		};
	});
});