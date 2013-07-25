{% extends "base.tpl" %}
{% block body %}
<div class="span2 text-center blog-page">
    <ul class="blog-admin-nav left-indent nav nav-tabs nav-stacked">
        {% include 'admin/admin_links.tpl' %}
    </ul>
</div>
<div class="blog-content span10">
    {% block admin %}
    Stuff
    {% endblock %}
</div>
{% endblock %}