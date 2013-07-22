{% extends "base.tpl" %}
{% block body %}
<div class="span2 text-center">
    <ul class="blog-admin-nav left-indent nav nav-tabs nav-stacked">
      <li><a href='/admin/new-post'>New Post</a></li>
      <li><a href='/admin/comment-approver'>Comments</a></li>
      <li><a>Special Pages</a></li>
      <li><a>Users</a></li>
    </ul>
</div>
<div class="span10">
    {% block admin %}
    {% endblock %}
</div>
{% endblock %}