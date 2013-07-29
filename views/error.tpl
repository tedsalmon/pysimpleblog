{% extends "base.tpl" %}
{% block body %}
<div class="blog-content blog-page">
    <article>
        <h4>{{error}}</h4>
        {% if stacktrace %}
        <pre>
            {{stacktrace}}
        </pre>
        {% endif %}
    </article>
</div>
{% endblock %}