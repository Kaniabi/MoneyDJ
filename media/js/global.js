$(function() {
	$.datepicker.setDefaults({
		autoSize: true,
		dayNames: [gettext('Sunday'), gettext('Monday'), gettext('Tuesday'), gettext('Wednesday'), gettext('Thursday'), gettext('Friday'), gettext('Saturday')],
		firstDay: 1,
		maxDate: '+1d',
		dateFormat: 'yy-mm-dd',
		showAnim: 'slideDown'
	});
	$('.uiDateField').datepicker()
});
