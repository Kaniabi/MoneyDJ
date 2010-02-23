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
			var cache = {};
			var mouseDownOnList = false;
			
			// Store the options
			$t.data('options', options);
			
			var id = 'autocomplete_' + Math.floor(Math.random() * 1000000);
			var suggestions = $('<div class="suggestions"></div>').attr('id', id).hide().appendTo('body');
			
			$t.attr('autocomplete', 'off');
			$t.bind('keypress', function(event) {
				// Enter or tab
				if (event.keyCode == 13 || event.keyCode == 9)
				{
					useSuggestion();
					// Only prevent the event if enter was pressed
					if (event.keyCode == 13)
					{
						return false;
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
					return false;
				}
				// Keycode 58/59/186 == ':' depending on the browser
				else if (options.amountElement && val.slice(range.start - 1, range.start) == ':' && (event.keyCode == 58 || event.keyCode == 59 || event.keyCode == 186))
				{
					var cur = getCurrentWord();
					var currentTotal = getSplitTotal($t.val());
					var value = parseFloat(options.amountElement.val());
					
					if (currentTotal >= value)
					{
						var newVal = '0';
					}
					else
					{
						var newVal = "" + (value - currentTotal).toFixed(2);
					}
					
					setCurrentWord(cur += newVal);
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
			
			function setCurrentWord(word)
			{
				if (options.multiWords)
				{
					var range = $t.caret();
					var lastSpace = $t.val().substr(0, range.end).lastIndexOf(' ');
					if (lastSpace == -1)
					{
						lastSpace = 0;
					}
					
					var cur = $t.val().substr(0, lastSpace);
					var valFirst = cur + (cur.length > 0 ? ' ' : '') + word;
					var val = valFirst + ($t.val().length > range.end ? ' ' + $.trim($t.val().substr(range.end)) : '');
					$t.val(val);
					$t.caret(valFirst.length);
				}
				else
				{
					$t.val(word);
				}
			}
			
			function showSuggestions(list)
			{
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
				for (var i in list)
				{
					var w = list[i];
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
					setCurrentWord(selected.text());
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
		minLetters: 2
	}
	
})(jQuery)

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
