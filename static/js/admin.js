;(function($){
    $(function(){
	function locateAndVerifyElements($prefix,$elements,$err_div_name){
	    $return_data = {};
	    $.each($elements, function(num, $name){
		$_el_name = '#' + $prefix + $name;
		$el = $($_el_name);
		if($el){
		    $el_val = $el.val();
		    $return_data[$name] = ($el_val) ? $el_val : false;
		    $el.val('');
		}else{
		    alert("Cannot find element " + $_el_name);
		}
	    });
	    for($i in $return_data){
		if(!$return_data[$i]){
		    $('#'+$err_div_name).html("Please provide a " + $i.charAt(0).toUpperCase() + $i.slice(1));
		    $('#'+$err_div_name).addClass('alert-danger');
		    $('#'+$err_div_name).removeClass('hide');
		    return false;
		}
	    }
	    return $return_data;
	}
	
	// Admin functions
	$('#post_btn').click(function(){
	    $elements = ['title', 'body', 'tags'];
	    $new_post = locateAndVerifyElements('entry_', $elements, 'post_output');
	    if (!$new_post) return false;
	    $new_post['public'] = $('#entry_public').attr('checked');
	    $.ajax({
                url: '/api/admin/create-post',
                type: 'POST',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify($new_post),
                success: function($return_data) {
                    if($return_data['error']){
			$('#post_output').html($return_data['error']);
			$('#post_output').addClass('alert-danger');
			$('#post_output').removeClass('hide');
                    }else{
			window.location = $return_data['location'];
                    }
                }
            });
	});
	
	$('#delete_post').click(function(){
	    $post_id = $('#delete_post').attr('data-post-id');
	    $('#delete_modal').modal();
	});
	
	$('#delete_confirm').click(function(){
	    $delete_data = {'post_id': $('#delete_post').attr('data-post-id')};
	    $.ajax({
                url: '/api/admin/delete-post',
                type: 'POST',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify($delete_data),
                success: function($return_data) {
                    if($return_data['error'])
			alert($return_data['error']);
                    else
			window.location = '/';
                }
            });
	});
	
	$('#update_post_btn').click(function(){
	    $elements = ['title', 'body', 'tags', 'id'];
	    $edit_post = locateAndVerifyElements('entry_', $elements, 'post_output');
	    if (!$edit_post) return false;
	    $edit_post['public'] = $('#entry_public').attr('checked');
	    $.ajax({
                url: '/api/admin/edit-post',
                type: 'POST',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify($edit_post),
                success: function($return_data) {
                    if($return_data['error']){
			$('#post_output').html($return_data['error']);
			$('#post_output').addClass('alert-danger');
			$('#post_output').removeClass('hide');
                    }else{
			window.location = $return_data['location'];
                    }
                }
            });
	});
	
	$('#update_password_btn').click(function(){
	    $elements = ['new', 'old', 'confirm'];
	    $new_post = locateAndVerifyElements('password_', $elements, 'password_output');
	    $.ajax({
                url: '/api/admin/change-password',
                type: 'POST',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify($delete_data),
                success: function($return_data) {
                    if($return_data['error'])
			alert($return_data['error']);
                    else
			window.location = '/';
                }
            });
	});
    });
})(jQuery);