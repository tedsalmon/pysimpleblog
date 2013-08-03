Blog = {
    init: function() {
	//Construct
	this.bindUIActions();
    },
    _addClass: function($el, $class){
	if (!$el.hasClass)
	    $el.addClass($class);
    },
    _parseElements: function($elements,$err_div_name){
	$return_data = {};
	$error = false;
	$('#'+$err_div_name).fadeOut();
	$.each($elements, function($name, $settings){
	    $_el_name = '#' + $name;
	    $el = $($_el_name);
	    if ($el) {
		$el_val = $el.val();
		if(!$el_val && $settings.required){
		    $el.focus();
		    $('#'+$err_div_name).html("Please provide " + $settings.err_msg);
		    $('#'+$err_div_name).addClass('alert-danger');
		    $('#'+$err_div_name).fadeIn();
		    $error = true;
		    return false;
		}
		$key_name = $name.slice($name.indexOf('_') + 1, $name.legnth);
		$return_data[$key_name] = $el_val;
	    }else{
		alert("Cannot find element " + $_el_name);
	    }
	});
	if ($error)
	    return false;
	$.each($elements, function($name, $settings){
	    if($settings.clear_value)
		$('#' + $name).val('');
	});
	return $return_data;
    },
    _error: function(event, xhr, ajaxSettings, thrownError){
	switch (event.status){
	    case 403:
	    case 401:
		$login_msg = $('#login_output');
		$login_msg.html('Sesssion Expired - Please login in and try again.');
		$login_msg.fadeIn();
		$('#login_modal').modal();
		break;
	    default:
		alert("Shit! - Some bad stuff happened, m'kay? Error: " + event.status);
		break;
	}
    },
    Admin: false,
    bindUIActions: function(){
	// Create Comment
	$('#comment_submit').click(this.createComment);
	// Login
	$('#login_modal_btn').click(function(){
	    $('#login_modal').modal();
	    setTimeout($('#login_username').focus, 500);
	});
	$('#login_btn').click(this.doLogin);
    },
    createComment: function(){
	$elements = {'comment_name': {'required': 1, 'err_msg': 'your name.', 'clear_value': 1},
		     'comment_email': {'required': 1, 'err_msg': 'your email.', 'clear_value': 1},
		     'comment_body': {'required': 1, 'err_msg': 'a comment.', 'clear_value': 1},
		     'comment_post_id': {'required': 1, 'err_msg': 'a Post ID.', 'clear_value': 0},
	};
	$comment_data = Blog._parseElements($elements, 'comment_output');
	if(!$comment_data)
	    return false;
	$.ajax({
	    url: '/api/v1/comment',
	    type: 'POST',
	    contentType: 'application/json; charset=utf-8',
	    data: JSON.stringify($comment_data),
	    error: Blog._error,
	    success: function($return_data) {
		if($return_data['error']){
		    $('#comment_output').html($return_data.error);
		    $('#comment_output').addClass('alert-danger');
		}else{
		    $('#comment_output').addClass('alert-success');
		    $('#comment_output').fadeIn(400, function(){
			$('#comment_output').html($return_data.msg);
		    });
		}
		$('#comment_output').removeClass('hide');
	    }
	});
	return false;
    },
    doLogin: function(){
	$elements = {'login_username': {'required': 1, 'err_msg': 'a Username.', 'clear_value': 0},
		     'login_password': {'required': 1, 'err_msg': 'a Password.', 'clear_value': 0}
	};
	$login_data = Blog._parseElements($elements, 'login_output');
	if (!$login_data)
	    return false;
	$.ajax({
	    url: '/api/v1/login',
	    type: 'POST',
	    contentType: 'application/json; charset=utf-8',
	    data: JSON.stringify($login_data),
	    error: Blog._error,
	    success: function($return_data) {
		if($return_data.error){
		    $login_err = $('#login_output');
		    $login_err.html($return_data.error);
		    $login_err.fadeIn();
		    $('#login_password').select();
		}else{
		    location.reload();
		}
	    }
	});
	return false;
    }
};