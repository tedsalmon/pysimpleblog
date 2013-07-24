{% extends "admin/main.tpl" %}
{% block admin %}
<form class="form left-indent" action="#">
    <div class="control-group">
	<div class="controls">
	    <input id="entry_title" class="longer" type="text" placeholder="Title..." {% if post_data %}value="{{post_data['title']}}"{% endif %} />
	</div>
    </div>
    <div class="control-group">
	<div class="controls">
	    <textarea id="entry_body" class="blog-post-textarea" placeholder="Post content">{% if post_data %}{{post_data['body']}}{% endif %}</textarea>
	</div>
    </div>
    <div class="control-group">
	<div class="controls">
	    <label for="entry_status">Publishing</label>
	    <select id="entry_status">
		<option value="0">Draft</option>
		<option value="1">Published</option>
	    </select>
	</div>
	<div class="controls">
	    <label for="entry_type">Type</label>
	    <select id="entry_type">
		<option value="0">Blog post</option>
		<option value="1">Page</option>
	    </select>
	</div>
	<div class="controls">
	    <label for="entry_tags">Tags</label>
	    <input id="entry_tags" class="longer" type="text" placeholder="Tags, comma separated" {% if post_data %}value="{{', '.join(post_data['tags'])}}"{% endif %}/>
	</div>
    </div>
    <div class="control-group">
	<div class="controls">
	    {% if post_data %}
	    <button id="update_post_btn" type="button" class="btn">Update Post</button>
	    <input type="hidden" id="entry_id" value="{{post_data['_id']}}" />
	    {% else %}
	    <button id="post_btn" type="button" class="btn">Submit Post</button>
	    {% endif %}
	</div>
    </div>
    <div class="control-group">
	<div class="controls">
	    <span id="post_output" class="alert hide in"></span>
	</div>
    </div>
</form>
{% endblock %}