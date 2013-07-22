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
	    <input id="entry_tags" class="longer" type="text" placeholder="Tags, comma separated" {% if post_data %}value="{{', '.join(post_data['tags'])}}"{% endif %}/>
	</div>
    </div>
    <div class="control-group">
	<div class="controls">
	    <input checked="checked" type="checkbox" id="entry_public" /> Make Public
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