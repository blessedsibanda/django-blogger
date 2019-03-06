$(document).ready(function() {
	// like action
	$('#btn-like').on('click', function(event) {
		event.preventDefault();
		let articleSlug = $(this).data('slug');
		$.get('/article/' + articleSlug + '/like/').done(function(data) {
			$('#article-likes').text(data.likes);
		});
	});
	//dislike action
	$('#btn-dislike').on('click', function(event) {
		event.preventDefault();
		let articleSlug = $(this).data('slug');
		$.get('/article/' + articleSlug + '/dislike/').done(function(data) {
			$('#article-dislikes').text(data.dislikes);
		});
	});
});
