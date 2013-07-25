{% extends "admin/main.tpl" %}
{% block admin %}
<header>
    <hgroup>
        <h2>Comment Manager</h2>
    </hgroup>
</header>
<hr />
{% if comments %}
<div class="blog-comments">
    {% for comment in comments %}
    <div id="comment_{{comment['id']}}" class="comment">
	<div>{{comment['name']}} wrote on {{comment['date'].strftime("%B %d, %Y %H:%M")}}:</div>
	<div class="blog-comment-body">{{comment['comment']}}</div>
	<form>
        <div class="control-group">
            <div class="control-group">
                <div class="controls">
                    <button data-approval="1" data-comment-id="{{comment['id']}}" class="comment-btn btn">Approve</button>
                    <button data-approval="0" data-comment-id="{{comment['id']}}" class="comment-btn btn">Deny</button>
                </div>
            </div>
	</div>
    {% endfor %}
</div>
{% else %}
    <h4>No comments pending approval</h4>
{% endif %}
{% endblock %}