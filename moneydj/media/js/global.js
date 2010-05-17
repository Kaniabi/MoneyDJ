$(function() {
	$.datepicker.setDefaults({
		autoSize: true,
		dayNames: [gettext('Sunday'), gettext('Monday'), gettext('Tuesday'), gettext('Wednesday'), gettext('Thursday'), gettext('Friday'), gettext('Saturday')],
		firstDay: 1,
		maxDate: '+0d',
		dateFormat: 'dd/mm/yy',
		showAnim: 'slideDown'
	});
	
	$('#nav li.accounts ul').hide().css('margin', 0);
	$('#nav li.accounts').hover(function() {$(this).find('ul').stop(false, true).slideDown('fast');}, function() {$(this).find('ul').stop(false, true).slideUp('fast');});

    // Sort out any messages showing on the page
    $('#messages').hide().css('left', ($(document).width() - $('#messages').width()) / 2 + 'px').delay(500).slideDown();
    setTimeout(function() {
        $('#messages .contents').slideUp();
        $('#messages').append($('<a href="#">' + gettext('Show Messages') + '</a>').toggle(function() { $(this).text(gettext('Hide Messages')).siblings('.contents').slideDown(); }, function() {
            $(this).text(gettext('Show Messages')).siblings('.contents').slideUp(); }));
    }, 10000);
	
	// Remove the add transaction form from the page so we can make it nicer
	var t = $('form#add_transaction').remove();
	var transactions = $('table.transactions');
	if (t.length == 1 && transactions.length == 1)
	{
		var a = $('<a href="#add_transaction_button" class="button">+ ' + gettext('Add Transaction') + '</a>');
		transactions.eq(0).before(a);
		var offset = a.offset();
		var cruft = getCruft(a);
		
		var holder = $('<div id="add_transaction_holder"></div>').html(t);
		holder.dialog({ autoOpen: false, modal: true, resizable: false, width: '80%' });
		if (holder.find('li.error').length > 0)
		{
			holder.dialog('open');
		}
		
		// When the button's clicked, add an overlay and show the form
		a.click(function () {
			holder.dialog('open');
		});
	}
	$('.uiDateField').datepicker();

	// Add a confirmation to the delete action
	var yes = gettext('Delete'), cancel = gettext('Don\'t Delete');
	var buttons = {};
    // Build the buttons this way so we can translate them
	buttons[cancel] = function() { $(this).dialog('close'); };
	$('a:has(span.delete)').click(function(e) {
		e.stopPropagation();
		var url = $(this).attr('href');
		buttons[yes] = function() { document.location = url; };
		$('<p>' + gettext('Are you sure you want to delete this transaction?') + '</p>').dialog({
			modal: true,
			buttons: buttons,
			resizable: false
		});
		return false;
	});

    // Setup tabs
    $('div.tabs').tabs();
	
	// Set up the tag editing
	var tagXhr;
	
	$('div.tags', transactions).hover(function() {
			$(this).find('> .sprite').removeClass('tag').addClass('tag_edit');
		}, function() {
			$(this).find('> .sprite').addClass('tag').removeClass('tag_edit');
		}).find('> .sprite').css('cursor', 'pointer');
		
	$('div.tags:has(span.tags) > span.sprite', transactions).attr('title', gettext('Edit tags')).live('click', function() {
		var $t = $(this).siblings('span.tags');
		var text = $t.hasClass('notags') ? '' : $.trim($t.text());
		var input = $('<input type="text"/>').data('tags', text).data('hastags', $t.hasClass('notags')).val(text).bind('blur.editTags', function() {
				var $t = $(this);
				var tags = $t.val();
				if ($t.data('tags') != tags && (tags != '' || !$t.data('hastags')))
				{
					var status = $t.parent().siblings('span.sprite').removeClass('success error tag').addClass('loading');
					
					if (tagXhr)
					{
						tagXhr.abort();
					}
					
					var id = $t.parents('td').attr('id').substring(12);
					$t.replaceWith('<span class="tags uneditable">' + gettext('Loading') + '</span>');
					tagXhr = $.ajax({
						url: '/accounts/transaction/' + id + '/tag/',
						type: 'POST',
						data: {'tags': tags, 'transactionId': id},
						success: function(results) {
							var c = '';
							var tagHolder = $('#transaction-' + results.transaction + ' div.tags');
							var holder = tagHolder.find('> span.tags').removeClass('uneditable');
							var status = tagHolder.find('> span.sprite');
							if (results.tags.length > 0)
							{
								holder.empty();
								for (var i = 0; i < results.tags.length; i++)
								{
									holder.append($('<a></a>').text(results.tags[i].name).attr('href', '/tags/view/' + results.tags[i].name));
									if (results.tags[i].amount && results.tags[i].amount != results.total)
									{
										holder.append(':' + (Math.round(results.tags[i].amount * 100) / 100));
									}
									holder.append(' ');
								}
								holder.removeClass('notags');
							}
							else
							{
								holder.addClass('notags').text(gettext('No tags'));
							}
							status.removeClass('loading').addClass('success');
							setTimeout(function() {
								status.removeClass('success').addClass('tag');
							}, 3000);
						},
						error: function(request) {
							$('#transaction-' + this.data.transactionId + ' div.tags span.tags').removeClass('uneditable').addClass('notags').text(gettext('An error occurred')).siblings('span.sprite.status').removeClass('loading').addClass('error');
						},
						dataType: 'json'
					});
				}
				else
				{
					tags = tags.split(' ');
					
					var repl = $('<span class="tags"></span>');
					
					if ($t.data('hastags'))
					{
						repl.text(gettext('No tags')).addClass('notags');
					}
					else
					{
						for (var i = 0; i < tags.length; i++)
						{
							if (tags[i].length > 0)
							{
								var s = tags[i].split(':', 2);
								repl.append('<a href="/tags/view/' + s[0] + '/">' + s[0] + '</a>');
								
								if (s.length > 1)
								{
									repl.append(':' + s[1]);
								}
								
								repl.append(' ');
							}
						}
					}
					$t.replaceWith(repl);
				}
			}).suggest({url: '/tags/suggest/', amountElement: $t.parents('td').siblings('td.money')});
		$t.replaceWith(input);
		input.focus();
	});
	
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
						setCurrentWord($t.text(), tags, true, false);
						return false;
					});
					
					ul.appendTo(payeeTagSuggestions);
				}
			}
		})
	}
	
	$('#id_payee').suggest({url: '/accounts/payee/suggest/', multiWords: false, useIds: true, idField: $('#id_payee_id'), onChosen: getPayeeTags});
	$('#id_tags').suggest({url: '/tags/suggest/', amountElement: $('#id_amount')});

	// Make form help text tooltips instead
	$('ol.form > li').contents().filter(function() { 
		// nodeType 3 is text (help text in django forms is just appended to the containing LI)
		return this.nodeType == 3 && $.trim(this.nodeValue).length > 0;
	}).wrap($('<div class="help_tooltip"></div>').css('display', 'none'));
	$('.help_tooltip');

	$('form li:has(.help_tooltip) > :input').tooltip({'tip': '.help_tooltip', relative: true, effect: 'fade', position: 'center right', offset: [0, 10]});
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
