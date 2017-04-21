$(document).ready(function(e) {
    $('.search-panel .dropdown-menu').find('a').click(function(e) {
		e.preventDefault();
		var param = $(this).attr("href").replace("#","");
		var concept = $(this).text();
		$('.search-panel span#search_concept').text(concept);
		$('.input-group #search_param').val(param);

	});

	$('#search-form').submit(function(e) {
		$('#title').hide();

		e.preventDefault();
	});
});