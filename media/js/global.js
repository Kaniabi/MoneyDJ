$(function() {
	$.datepicker.setDefaults({
		autoSize: true,
		dayNames: [gettext('Sunday'), gettext('Monday'), gettext('Tuesday'), gettext('Wednesday'), gettext('Thursday'), gettext('Friday'), gettext('Saturday')],
		firstDay: 1,
		maxDate: '+1d',
		dateFormat: 'yy-mm-dd',
		showAnim: 'slideDown'
	});
	
	// Remove the add transaction form from the page so we can make it nicer
	var t = $('form#add_transaction').remove();
	var transactions = $('table.transactions:first');
	if (t.length == 1 && transactions.length == 1)
	{
		var a = $('<a href="#add_transaction_button" class="button">+ ' + gettext('Add Transaction') + '</a>');
		transactions.before(a);
		var offset = a.offset();
		var cruft = getCruft(a);
		
		var holder = $('<div id="add_transaction_holder"></div>').css({
				position: 'absolute',
				left: offset.left,
				top: offset.top + a.height() + cruft.top + cruft.bottom,
				zIndex: 9998
			}).html(t).appendTo('body');
		if (holder.find('li.error').length == 0)
		{
			holder.hide()
		}
		
		a.click(function(e) {
			e.preventDefault();
			e.stopPropagation();
			holder.slideDown();
			$('body').append($('<div class="overlay"></div>').css({
				zIndex: 500,
				height: $('body').height(),
				width: $('body').width()
			}).click(function(e) {
				e.preventDefault();
				e.stopPropagation();
				holder.slideUp();
				$(this).remove();
			}));
		});
	}
	$('.uiDateField').datepicker();
	
	var payeeTagXhr = null;
	var payeeTagSuggestions = null;
	var getPayeeTags = function(payee)
	{
		if (payeeTagXhr)
		{
			payeeTagXhr.abort();
		}
		
		if (!payeeTagSuggestions)
		{
			payeeTagSuggestions = $('<li></li>').addClass('tag_suggestions').insertAfter($('#id_tags').parent());
		}
		
		payeeTagSuggestions.text(gettext('Loading')).addClass('loading');
		
		payeeTagXhr = $.ajax({
			type: 'GET',
			url: '/tags/suggest/' + payee + '/',
			cache: true,
			dataType: 'json',
			success: function(ret) {
				payeeTagSuggestions.text('').removeClass('loading');
				if (ret.length > 0)
				{
					payeeTagSuggestions.append('<label>' + gettext('Tag Suggestions:') + '</label>');
					var ul = $('<ul></ul>');
					for (var i = 0; i < ret.length; i++)
					{
						ul.append('<li><a href="#">' + ret[i] + '</a></li>');
					}
					
					ul.find('a').click(function() {
						var $t = $(this);
						var tags = $('#id_tags');
						setCurrentWord($t.text(), tags, true);
						return false;
					});
					
					ul.appendTo(payeeTagSuggestions);
				}
			}
		})
	}
	
	$('#id_payee').suggest({url: '/accounts/payee/suggest/', multiWords: false, useIds: true, idField: $('#id_payee_id'), onChosen: getPayeeTags});
	$('#id_tags').suggest({url: '/tags/suggest/', amountElement: $('#id_amount')});
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