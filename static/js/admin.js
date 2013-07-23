Blog.Admin = {
    init: function(){
	console.log('Admin init');
	$('#post_btn').click(function(){
	    $elements = ['title', 'body', 'tags'];
	    $new_post = Blog.locateAndVerifyElements('entry_', $elements, 'post_output');
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
			window.location = '/'+$return_data['location'];
                    }
                }
            });
	});
	
	$('#delete_post').click(function(){
	    $post_id = $('#delete_post').attr('data-post-id');
	    $('#delete_modal').modal();
	});
	
	$('#delete_confirm').click(function(){
	    $.ajax({
                url: '/api/admin/post/'+ $('#delete_post').attr('data-post-id'),
                type: 'DELETE',
                contentType: 'application/json; charset=utf-8',
                success: function($return_data) {
                    if($return_data['error'])
			alert($return_data['error']);
                    else
			window.location = '/';
                }
            });
	});
	
	$('#update_post_btn').click(function(){
	    $elements = ['title', 'body', 'tags'];
	    $edit_post = Blog.locateAndVerifyElements('entry_', $elements, 'post_output');
	    if (!$edit_post) return false;
	    $edit_post['public'] = $('#entry_public').attr('checked');
	    $.ajax({
                url: '/api/admin/post/'+$('#entry_id').val(),
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
	
	$('.comment-btn').click(function(){
	    $comment_id = this.getAttribute('data-comment-id');
	    $comment_div = $('#comment_'+$comment_id);
	    $comment_approval = this.getAttribute('data-approval');
	    console.log($comment_div);
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
    }
};