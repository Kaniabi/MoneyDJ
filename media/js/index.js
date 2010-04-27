jQuery(function () {
	$('#promoboxes img:not(:first)').hide();
	$('#promoboxes').after('<div id="promo_nav"></nav>');
	$('#promoboxes h3').remove().appendTo('#promo_nav').hover(function() {
		var id = $(this).parent().find('h3').index(this);
		console.log(id);
		$('#promoboxes img').hide().eq(id).show();
		$(this).addClass('selected').siblings().removeClass('selected');
	}).css('cursor', 'pointer').eq(0).addClass('selected');
	$('#promo_nav h3:first').addClass('first');
});
