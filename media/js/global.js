$(function() {
	$.datepicker.setDefaults({
		autoSize: true,
		dayNames: [gettext('Sunday'), gettext('Monday'), gettext('Tuesday'), gettext('Wednesday'), gettext('Thursday'), gettext('Friday'), gettext('Saturday')],
		firstDay: 1,
		maxDate: '+1d',
		dateFormat: 'yy-mm-dd',
		showAnim: 'slideDown'
	});
	$('.uiDateField').datepicker();
	
	$('#id_payee').suggest({url: '/accounts/payee/suggest/', multiWords: false});
	$('#id_tags').suggest({url: '/tags/suggest/', amountElement: $('#id_amount')});
	
	// Remove the add transaction form from the page so we can make it nicer
	var t = $('form#add_transaction');
	var transactions = $('table.transactions:first');
	if (t.length == 1 && transactions.length == 1)
	{
		var a = $('<a href="#add_transaction_button" class="button">+ ' + gettext('Add Transaction') + '</a>');
		transactions.before(a);
		var offset = a.offset();
		var offsetParent = a.offsetParent().offset();
		var cruft = getCruft(a);
		
		t.wrap($('<div id="add_transaction_holder"></div>').css({
				position: 'absolute',
				left: offset.left - offsetParent.left,
				top: offset.top + a.height() + cruft.top + cruft.bottom - offsetParent.top,
				zIndex: 9998
			}).hide());
		var holder = $('#add_transaction_holder');
		
		a.click(function(e) {
			e.preventDefault();
			e.stopPropagation();
			holder.slideDown();
			/*
$('body').append($('<div class="overlay"></div>').css('z-index', 500).click(function(e) {
				e.preventDefault();
				e.stopPropagation();
				holder.slideUp();
				$(this).remove();
			}));
*/
		});
	}
});

function getCruft(element)
{
	var $e = $(element);	
	return {
		left: parseInt($e.css('borderLeftWidth')) + parseInt($e.css('paddingLeft')),
		right: parseInt($e.css('borderRightWidth')) + parseInt($e.css('paddingRight')),
		top: parseInt($e.css('borderTopWidth')) + parseInt($e.css('paddingTop')),
		bottom: parseInt($e.css('borderBottomWidth')) + parseInt($e.css('paddingBottom'))
	}
}

/*
 * jQuery Caret Range plugin
 * Copyright (c) 2009 Matt Zabriskie
 * Released under the MIT and GPL licenses.
 */
(function($) {
	$.extend($.fn, {
		caret: function (start, end) {
			var elem = this[0];

			if (elem) {							
				// get caret range
				if (typeof start == "undefined") {
					if (elem.selectionStart) {
						start = elem.selectionStart;
						end = elem.selectionEnd;
					}
					else if (document.selection) {
						var val = this.val();
						var range = document.selection.createRange().duplicate();
						range.moveEnd("character", val.length)
						start = (range.text == "" ? val.length : val.lastIndexOf(range.text));

						range = document.selection.createRange().duplicate();
						range.moveStart("character", -val.length);
						end = range.text.length;
					}
				}
				// set caret range
				else {
					var val = this.val();

					if (typeof start != "number") start = -1;
					if (typeof end != "number") end = -1;
					if (start < 0) start = 0;
					if (end > val.length) end = val.length;
					if (end < start) end = start;
					if (start > end) start = end;

					elem.focus();

					if (elem.selectionStart) {
						elem.selectionStart = start;
						elem.selectionEnd = end;
					}
					else if (document.selection) {
						var range = elem.createTextRange();
						range.collapse(true);
						range.moveStart("character", start);
						range.moveEnd("character", end - start);
						range.select();
					}
				}

				return {start:start, end:end};
			}
		}
	});
})(jQuery);