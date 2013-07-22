{% extends "admin/main.tpl" %}
{% block admin %}
<h3>Comments Pending Approval</h3>
{% if comments %}
<div class="blog-comments">
    {% for comment in comments %}
    <div class="comment">
	<div>{{comment['name']}} wrote on {{comment['date'].strftime("%B %d, %Y %H:%M")}}:</div>
	<div class="blog-comment-body">{{comment['comment']}}</div>
    </div>
    {% endfor %}
</div>
{% else %}
    <h4>No comments pending approval</h4>
{% endif %}
{% endblock %}