{% extends "base.tpl" %}
{% block body %}
<div class="span2 blog-page blog-admin-nav-container">
    <ul class="nav nav-list well blog-admin-nav">
        {% include 'admin/admin_links.tpl' %}
    </ul>
</div>
<div class="blog-content span10">
    {% block admin %}
    Stuff
    {% endblock %}
</div>
{% endblock %}