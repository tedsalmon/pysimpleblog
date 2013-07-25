Blog = {
    init: function() {
	//Construct
	$('#comment_submit').click(function(){
	    $elements = ['name', 'email', 'comment', 'post_id'];
	    $comment_data = Blog.locateAndVerifyElements('comment_', $elements, 'comment_output');
	    if (!$comment_data) return false;
	    $.ajax({
                url: '/api/comment',
                type: 'POST',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify($comment_data),
                success: function($return_data) {
                    if($return_data['error']){
			$('#comment_output').html($return_data['error']);
			$('#comment_output').addClass('alert-danger');
                    }else{
			$('#comment_output').addClass('alert-success');
			$('#comment_output').html($return_data['msg']);
                    }
		    $('#comment_output').removeClass('hide');
                }
            });
	    return false;
	});
	
	//Login
	$('#login_modal_btn').click(function(){
	    $('#login_modal').modal();
	});
	
	$('#login_btn').click(function(){
	    $elements = ['username', 'password'];
	    $login_data = Blog.locateAndVerifyElements('login_', $elements, 'login_output');
	    if (!$login_data) return false;
	    $.ajax({
                url: '/api/login',
                type: 'POST',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify($login_data),
                success: function($return_data) {
                    if($return_data.error){
			$('#login_output').html($return_data.error);
			$('#login_output').addClass('alert-danger');
			$('#login_output').removeClass('hide');
                    }else{
			window.location = '/admin';
                    }
                }
            });
	    return false;
	});
    },
    Admin: false,
    locateAndVerifyElements: function($prefix,$elements,$err_div_name,$optional_items){
	if(!$optional_items)
	    $optional_items = [];
	$return_data = {};
	$.each($elements, function(num, $name){
	    $_el_name = '#' + $prefix + $name;
	    $el = $($_el_name);
	    if($el){
		$el_val = $el.val();
		if($el_val)
		    $return_data[$name] = $el_val;
		$el.val('');
	    }else{
		alert("Cannot find element " + $_el_name);
	    }
	});
	for($i in $return_data){
	    if(!$return_data[$i] && $optional_items.indexOf($return_data[$i]) != -1){
		$('#'+$err_div_name).html("Please provide a " + $i.charAt(0).toUpperCase() + $i.slice(1));
		$('#'+$err_div_name).addClass('alert-danger');
		$('#'+$err_div_name).removeClass('hide');
		return false;
	    }
	}
	return $return_data;
    }
};