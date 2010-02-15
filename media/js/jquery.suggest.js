(function($){
	
	$.fn.suggest = function(data)
	{
		options = $.extend({}, $.fn.suggest.defaults, data);
		
		if (!options.url)
		{
			return this;
		}
		
		return $(this).each(function() {
			var $t = $(this);
			var word = '';
			if (!$t.is('input'))
			{
				return;
			}
			var suggestions = $('<div class="suggestions"></div>').hide();
			
			$t.attr('autocomplete', 'off').after(suggestions);
			
			$('body').bind('click', function() {
				hideSuggestions();
			});
			$t.bind('keypress', function(event) {
				// Enter
				if (event.keyCode == 13)
				{
					useSuggestion();
					return false;
				}
			}).bind('keyup', function(event) {
				var val = $(this).val();
				var range = $(this).caret();
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
					var cur = $t.val().substr(0, range.start);
					var valFirst = cur + options.amountElement.val();
					var val = valFirst + ($t.val().length > cur.length ? ' ' + $t.val().substr(range.end) : '');
					$(this).val(val);
					$t.caret(valFirst.length);
					hideSuggestions();
				}
				// We have pressed a letter
				else if ((event.keyCode > 64 && event.keyCode < 91) || (event.keyCode > 69 && event.keyCode < 123))
				{
					word = (options.multiWords ? getCurrentWord() : $t.val());
					if (word.length >= options.minLetters)
					{
						getSuggestions(word);
					}
					else
					{
						hideSuggestions();
					}
				}
				else
				{
					hideSuggestions();
				}
			});
			
			suggestions.find('li').live('hover', function() {
				selectSuggestion(suggestions.find('li').index(this));
			}).live('click', function() {
				useSuggestion(suggestions.find('li').index(this));
			});
			
			function getSuggestions(word)
			{
				suggestions.addClass('loading').text(gettext('Loading'));
				$.ajax({
					type: 'GET',
					url: options.url,
					data: options.queryString + '=' + word,
					dataType: 'json',
					success: function(ret) {
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
				var range = $t.caret();
				var lastSpace = $t.val().substr(0, range.end).lastIndexOf(' ');
				if (lastSpace == -1)
				{
					lastSpace = 0;
				}
				
				var cur = $t.val().substr(0, lastSpace);
				var valFirst = cur + (cur.length > 0 ? ' ' : '') + word;
				var val = valFirst + ($t.val().length > cur.length ? ' ' + $.trim($t.val().substr(range.end)) : '');
				$t.val(val);
				$t.caret(valFirst.length);
			}
			
			function showSuggestions(list)
			{
				if (list.length == 0)
				{
					hideSuggestions();
					return;
				}
				var ul = $('<ul></ul>');
				for (var i in list)
				{
					var w = list[i];
					ul.append('<li>' + w.replace(word, '<span>' + word + '</span>') + '</li>');
				}
				var cruftLeft = parseInt($t.css('borderLeftWidth')) + parseInt($t.css('paddingLeft'));
				var cruftRight = parseInt($t.css('borderRightWidth')) + parseInt($t.css('paddingRight'));
				var cruftTop = parseInt($t.css('borderTopWidth')) + parseInt($t.css('paddingTop'));
				var cruftBottom = parseInt($t.css('borderBottomWidth')) + parseInt($t.css('paddingBottom'));

				var width = $t.width();
				var offset = $t.offset();
				var parent = $t.offsetParent().offset();
				var left = offset.left - parent.left + cruftLeft;
				var top = offset.top - parent.top + $t.height() + cruftTop + cruftBottom;

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
		});
	}
	
	$.fn.suggest.defaults = {
		queryString: 'q',
		multiWords: true,
		minLetters: 2
	}
	
})(jQuery)
