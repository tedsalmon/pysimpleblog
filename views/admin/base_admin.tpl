{% extends "base.tpl" %}
{% block body %}
DERP
<div class="span2 text-center">
    <ul class="blog-admin-nav left-indent nav nav-tabs nav-stacked">
      <li><a href='/admin/newpost'>New Post</a></li>
      <li><a>Comments</a></li>
      <li><a>Users</a></li>
    </ul>
</div>
<div class="span10">
    {% block admin %}
    {% endblock %}
</div>
{% endblock %}