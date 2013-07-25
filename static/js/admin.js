Blog.Admin = {
    init: function(){
	this.bindUIActions();
    },
    bindUIActions: function(){
	
	$('#post_btn').click(function(){
	    $elements = ['title', 'body', 'tags', 'status', 'type'];
	    $new_post = Blog.locateAndVerifyElements('entry_', $elements, 'post_output', ['tags']);
	    if (!$new_post) return false;
	    $new_post['public'] = $('#entry_public').attr('checked');
	    $.ajax({
                url: '/api/admin/post',
                type: 'POST',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify($new_post),
                success: function($return_data) {
                    if($return_data['error']){
			$('#post_output').html($return_data['error']);
			$('#post_output').addClass('alert-danger');
			$('#post_output').removeClass('hide');
                    }else{
			window.location = '/' + $return_data['location'];
                    }
                }
            });
	    return false;
	});
	
	$('.delete-post').click(function(){
	    $post_id = this.getAttribute('data-post-id');
	    this.className += ' deleteable';
	    $('#delete_modal').modal();
	});
	
	$('#delete_confirm').click(function(){
	    $.ajax({
                url: '/api/post/'+ $('.deleteable').attr('data-post-id'),
                type: 'DELETE',
                contentType: 'application/json; charset=utf-8',
                success: function($return_data) {
                    if($return_data['error'])
			alert($return_data['error']);
                    else
			if($('.deleteable').attr('data-no-refresh') == 'true'){
			    $tr = $('.deleteable').closest('tr');
			    $tr.fadeOut(400, function(){
				$tr.remove();
			    });
			}else{
			    window.location = '/';
			}
                }
            });
	});
	
	$('#update_post_btn').click(function(){
	    $elements = ['title', 'body', 'tags', 'status', 'type'];
	    $edit_post = Blog.locateAndVerifyElements('entry_', $elements, 'post_output');
	    if (!$edit_post) return false;
	    $edit_post['public'] = $('#entry_public').attr('checked');
	    $.ajax({
                url: '/api/post/' + $('#entry_id').val(),
                type: 'PUT',
                contentType: 'application/json; charset=utf-8',
                data: JSON.stringify($edit_post),
                success: function($return_data) {
                    if($return_data['error']){
			$('#post_output').html($return_data['error']);
			$('#post_output').addClass('alert-danger');
			$('#post_output').removeClass('hide');
                    }else{
			window.location = '/'+$return_data['location'];
                    }
                }
            });
	});

	
	$('.comment-btn').click(function(){
	    $comment_id = this.getAttribute('data-comment-id');
	    $comment_div = $('#comment_'+$comment_id);
	    $comment_approval = this.getAttribute('data-approval');
	    $.ajax({
                url: '/api/comment/'+$comment_id,
                type: ($comment_approval == '1') ? 'PUT' : 'DELETE',
                contentType: 'application/json; charset=utf-8',
                success: function($return_data) {
                    if($return_data['error'])
			alert($return_data['error']);
                    else
			$comment_div.remove();
                }
            });
	});
	
	
	$('#link_add').click(function(){
	    $elements = ['url', 'title'];
	    $add_link = Blog.locateAndVerifyElements('link_', $elements, 'link_output');
	    if (!$add_link) return false;
	    $.ajax({
                url: '/api/link',
                type: 'POST',
		data: JSON.stringify($add_link),
                contentType: 'application/json; charset=utf-8',
                success: function($return_data) {
                    if($return_data.error)
			alert($return_data.error);
                    else
			console.log('No Error');//location.reload();
                }
            });
	});
	
	$('#update_password_btn').click(function(){
	    $elements = ['new', 'old', 'confirm'];
	    $new_post = Blog.locateAndVerifyElements('password_', $elements, 'password_output');
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
    }
};