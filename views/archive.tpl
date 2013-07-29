{% extends "base.tpl" %}
{% block body %}
<div class="blog-content blog-page">
    <header>
        <hgroup>
            <h2>Archives</h2>
        </hgroup>
    </header>
    {% for year in posts %}
    <div class="row-fluid">
	<h3>{{year}}</h3>
	{% for post in posts[year] %}
	<div class="span6">
	    <span class="span3"><h4 class="inline">{{post['date'].strftime('%B %d')}}</h4></span>
	    <span class="span8"><h5><a class="muted" href='/{{year}}/{{post['url']}}'>{{post['title']}}</a></h5></span>
	</div>
	{% endfor %}
    </div>
    {% endfor %}
</div>
{% endblock %}