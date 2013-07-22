{% extends "base.tpl" %}
{% block body %}
<article class="blog-content">
    <header>
	<hgroup>
	    <h2 class="muted">{{page['title']}}</h2>
	</hgroup>
    </header>
    <div>{{page['body']}}</div>
</article>
{% endblock %}