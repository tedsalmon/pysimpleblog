{% extends "base.tpl" %}
{% block body %}
<div class="blog-content">
    <h1>Archives</h1>
    {% for year in special %}
    <div class="row-fluid">
	<h3>{{year}}</h3>
	{% for post in special[year] %}
	<div class="span6">
	    <span class="span3"><h4 class="inline">{{post['date'].strftime('%B %d')}}</h4></span>
	    <span class="span8"><h5><a class="muted" href='#'>{{post['title']}}</a></h5></span>
	</div>
	{% endfor %}
    </div>
    {% endfor %}
</div>
{% endblock %}