{% extends "admin/main.tpl" %}
{% block admin %}
{% set types = {0: 'Blog Post', 1: 'Page' } %}
{% set statuses = {0: 'Draft', 1: 'Published' } %}
<header>
    <hgroup>
	{% if post_data %}
        <h2>Edit Post</h2>
	{% else %}
	<h2>New Post</h2>
	{% endif %}
    </hgroup>
</header>
<hr />
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
	    <label for="entry_status">Publishing Status</label>
	    <select id="entry_status">
		{% for status in statuses %}
		<option {%if post_data %}{%if post_data['status'] == status %}selected{%endif%}{%endif%} value="{{status}}">{{statuses[status]}}</option>
		{% endfor %}
	    </select>
	</div>
	<div class="controls">
	    <label for="entry_type">Type</label>
	    <select id="entry_type">
		{% for type in types %}
		<option {%if post_data %}{%if post_data['type'] == type %}selected{%endif%}{%endif%} value="{{type}}">{{types[type]}}</option>
		{% endfor %}
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
	    <span id="post_output" class="alert hide alert-danger"></span>
	</div>
    </div>
</form>
{% endblock %}