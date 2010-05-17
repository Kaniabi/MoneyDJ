(function($){
	
	$.fn.suggest = function(data)
	{
		var options = $.extend({}, $.fn.suggest.defaults, data);
		
		if (!options.url)
		{
			return this;
		}
		
		return $(this).each(function() {
			var $t = $(this);
			if (!$t.is('input'))
			{
				return;
			}
			var word = '';
			var xhr;
			var request;
			var cache = {};
			var mouseDownOnList = false;
			
			// Store the options
			$t.data('options', options);
			
			var id = 'autocomplete_' + Math.floor(Math.random() * 1000000);
			var suggestions = $('<div class="suggestions"></div>').attr('id', id).hide().appendTo('body');
			var data = [];
			
			$t.attr('autocomplete', 'off');
			$t.bind('keypress', function(event) {
				// Enter or tab
				if (event.keyCode == 13 || event.keyCode == 9)
				{
					// Only prevent the event if enter was pressed and the suggestions are visible
					if (event.keyCode == 13 && suggestions.is(':visible'))
					{
						useSuggestion();
						xhr && xhr.abort();
						return false;
					}
					else if (suggestions.is(':visible'))
					{
						useSuggestion();
						xhr && xhr.abort();
					}
				}
			}).bind('keyup', function(event) {
				var $t = $(this);
				var val = $t.val();
				var range = $t.caret();
				var options = $t.data('options');
				// Up or down arrow
				if (event.keyCode == 38 || event.keyCode == 40)
				{
					var selected = getSelected();
					var selectedId = suggestions.find('li').index(selected);
					var total = suggestions.find('li').length;
					switch(event.keyCode) 
					{
						// Up
						case 38:
							if (selected.length == 0)
							{
								selectSuggestion(total - 1);
							}
							else
							{
								selectSuggestion(selectedId - 1);
							}
							return false;
							break;
						// Down
						case 40:
							if (selected.length == 0)
							{
								selectSuggestion(0);
							}
							else
							{
								selectSuggestion(selectedId + 1);
							}
							return false;
							break;
					}
				}
				// Escape
				else if (event.keyCode == 27)
				{
					selectSuggestion(-1);
					hideSuggestions();
					xhr && xhr.abort();
					return false;
				}
				// Keycode 58/59/186 == ':' depending on the browser
				else if (options.amountElement && val.slice(range.start - 1, range.start) == ':' && (event.keyCode == 58 || event.keyCode == 59 || event.keyCode == 186))
				{
					xhr && xhr.abort();
					var cur = getCurrentWord();
					var currentTotal = getSplitTotal($t.is('input') ? $.trim($t.val()) : $.trim($t.text()));
					var total = ($(options.amountElement).is('input') ? $(options.amountElement).val() : $(options.amountElement).text());
					total = total.replace(/[^0-9\-+.]+/, '');
					var value = parseFloat(total);
					
					if (currentTotal >= value)
					{
						var newVal = '0';
					}
					else
					{
						var newVal = "" + (value - currentTotal).toFixed(2);
					}
					
					setCurrentWord(cur += newVal, $t, options.multiWords);
					$t.caret($t.caret().start - newVal.length, $t.caret().start);
					
					hideSuggestions();
				}
				else
				{
					// Space bar or enter
					if (options.multiWords && event.keyCode == 32 || event.keyCode == 13)
					{
						hideSuggestions();
					}
					// We have pressed a letter or number
					else
					{
						word = (options.multiWords === true ? getCurrentWord() : val);
						if (word.length >= options.minLetters)
						{
							getSuggestions(word);
						}
						else
						{
							hideSuggestions();
						}
					}
				}
			}).bind('blur', function() {
				if (!mouseDownOnList)
				{
					hideSuggestions();
				}
			});
			
			function getSplitTotal(string)
			{
				var split = string.split(' ');
				var total = 0;
				for (var i = 0; i < split.length; i++)
				{
					var sColon = split[i].indexOf(':');
					if (sColon > 0)
					{
						var str = split[i].substring(sColon + 1);
						if (str.length > 0)
						{
							var val = parseFloat(str);
							if (!isNaN(val) && val > 0)
							{
								total += val;
							}
						}
					}
				}
				return total;
			}
			
			function getSuggestions(word)
			{
				// If we have the word cached, use that
				if (cache[word])
				{
					showSuggestions(cache[word]);
					return;
				}
				// Abort the request if there's one already active
				if (xhr)
				{
					xhr.abort();
				}
				var data = {};
				data[options.queryString] = word;
				
				var cruft = getCruft($t);

				var width = $t.width();
				var offset = $t.offset();
				var left = offset.left + cruft.left;
				var top = offset.top + $t.height() + cruft.top + cruft.bottom;
				
				suggestions.addClass('loading').text(gettext('Loading')).show().css({
					position: 'absolute',
					top: top + 'px',
					left: left + 'px',
					width: width
				}).show();
				
				// Cancel previous requests
				if (request)
				{
					clearTimeout(request);
				}
				
				request = setTimeout(function() {
					xhr = $.ajax({
						type: 'GET',
						url: options.url,
						cache: true,
						data: data,
						dataType: 'json',
						success: function(ret) {
							cache[word] = ret;
							showSuggestions(ret);
						}
					});
				}, options.delay);
			}
			
			function getCurrentWord()
			{
				var range = $t.caret();
				var lastSpace = $t.val().substr(0, range.end).lastIndexOf(' ');
				if (lastSpace == -1)
				{
					lastSpace = 0;
				}
				else
				{
					lastSpace++;
				}
				return $t.val().slice(lastSpace, range.end);
			}
			
			function showSuggestions(list)
			{
				data = list;
				if (list.length == 0)
				{
					hideSuggestions();
					return;
				}
				var ul = $('<ul></ul>').bind('mouseover', function(event) {
					selectSuggestion(suggestions.find('li').index(target(event)));
				}).bind('click', function(event) {
					selectSuggestion(suggestions.find('li').index(target(event)));
					useSuggestion();
					return false;
				}).bind('mousedown', function() {
					mouseDownOnList = true;
				}).bind('mousedown', function() {
					mouseDownOnList = false;
				});
				for (var i in data)
				{
					if (typeof data[i] == 'object') 
					{
						var w = data[i][1];
					}
					else 
					{
						var w = data[i];
					}
					ul.append('<li>' + w.replace(new RegExp('(' + RegExp.escape(word) + ')', 'gi'), '<span>$1</span>') + '</li>');
				}
				
				var cruft = getCruft($t);

				var width = $t.width();
				var offset = $t.offset();
				var left = offset.left + cruft.left;
				var top = offset.top + $t.height() + cruft.top + cruft.bottom;

				suggestions.removeClass('loading').html(ul).css({
					position: 'absolute',
					top: top + 'px',
					left: left + 'px',
					width: width
				}).show();
			}
			
			function hideSuggestions()
			{
				xhr && xhr.abort();
				suggestions.hide().html('');
			}
			
			function selectSuggestion(id)
			{
				suggestions.find('li').removeClass('selected').eq(id).addClass('selected');
			}
			
			function getSelected()
			{
				return suggestions.find('li.selected');
			}
			
			function useSuggestion()
			{
				var selected = getSelected();
				if (selected.length == 1)
				{
					setCurrentWord(selected.text(), $t, options.multiWords);
					
					if (options.useIds == true && options.idField != null)
					{
						var selectedId = suggestions.find('li').index(selected);
						var id = data[selectedId][0];
						var idField = $(options.idField);
						if (options.multiWords)
						{
							idField.val(idField.val() + options.multiIdSelector + id)
						}
						else
						{
							idField.val(id);
						}
						
						if ($.isFunction(options.onChosen)) options.onChosen(id);
					}
					else
					{
						if ($.isFunction(options.onChosen)) options.onChosen(selected.text());
					}
				}
				
				hideSuggestions();
			}
	
			/* Find the target of an event. From http://docs.jquery.com/Plugins/Autocomplete */
			function target(event) 
			{
				var element = event.target;
				while(element && element.tagName != "LI")
					element = element.parentNode;
				// more fun with IE, sometimes event.target is empty, just ignore it then
				if(!element)
					return [];
				return element;
			}
		});
	}
	
	$.fn.suggest.defaults = {
		queryString: 'q',
		multiWords: true,
		minLetters: 2,
		// The plugin will expect each element of the array of results to be a two-element array of id => text
		useIds: false,
		// The field to use to hold the id(s) of the currently selected item (normally a hidden field)
		idField: null,
		multiIdSeparator: ',',
		// Called when an item is selected. Passes either the id or text of the selected item depending on the options
		onSelected: null,
		// The time delay before the request is made in milliseconds
		delay: 1000
	}
	
})(jQuery)
		
function setCurrentWord(word, element, multiWords, allowSplit)
{
	var $t = jQuery(element);
	
	allowSplit = (typeof allowSplit == 'undefined') ? true : allowSplit;
	
	// If we allow multiple words, we need to do more advanced calculation
	if (multiWords)
	{
		// Get the current selection
		var range = $t.caret();
		
		// Get the last space up until the end of the current selection
		var beforeSpace = $t.val().substr(0, range.end).lastIndexOf(' ');
		
		// If the cursor is at the end and we have no spaces we can just replace what we have in the field
		if (range.start == $t.val().length && beforeSpace == -1)
		{
			$t.val(word + (allowSplit ? '' : ' '));
			return;
		}
		// Otherwise if don't have a space then we want to replace from the beginning of the field onwards
		else if (beforeSpace == -1)
		{
			beforeSpace = 0;
		}
		
		// The current value from the beginning of the field's value to the last space
		var before = $t.val().substr(0, beforeSpace);
		
		// Work out what content we have after the cursor
		var after = $t.val().length > range.end ? ' ' + $.trim($t.val().substr(range.end)) : '';
		
		var afterSpace = after.indexOf(' ');
		// If there's a space in the content after the current position, we replace up to that space
		if (afterSpace != -1 && afterSpace != 0)
		{
			after = after.substr(afterSpace);
		}
		
		var value = before + (before.length > 0 ? ' ' : '') + word;
		if (after.length > 0 || !allowSplit)
		{
			value += ' ';
		}
		value += after;
		
		// Set the value of the element, making sure to separate everything properly
		$t.val(value);
		// Set the position of the caret - if we're not allowing a split this will be after the space
		$t.caret((before + (before.length > 0 ? ' ' : '') + word).length + (allowSplit ? 0 : 1));
	}
	// Otherwise we just set the value of the element to the word given
	else
	{
		$t.val(word);
	}
}

// From http://simonwillison.net/2006/Jan/20/escape/
RegExp.escape = function(text) {
  if (!arguments.callee.sRE) {
    var specials = [
      '/', '.', '*', '+', '?', '|',
      '(', ')', '[', ']', '{', '}', '\\'
    ];
    arguments.callee.sRE = new RegExp(
      '(\\' + specials.join('|\\') + ')', 'g'
    );
  }
  return text.replace(arguments.callee.sRE, '\\$1');
}
